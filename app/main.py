import logging
import json
import time
import sys
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from google.cloud import error_reporting
from app.engine import RAGOrchestrationEngine

# Initialize core FastAPI app
app = FastAPI(title="Financial RAG Analytics Engine", version="1.0.0")
engine = RAGOrchestrationEngine()

try:
    error_client = error_reporting.Client()
except Exception:
    error_client = None

# --- GKE PRODUCTION STRUCTURED LOGGING CONFIGURATION ---
class GKEJsonFormatter(logging.Formatter):
    """Formats all engine and application logs into single-line GCP jsonPayload dictionaries."""
    def format(self, record):
        if isinstance(record.msg, dict):
            log_entry = record.msg
        else:
            log_entry = {
                "message": record.getMessage(),
                "severity": record.levelname,
                "component": "rag-backend-service",
                "logger": record.name
            }
        return json.dumps(log_entry)

# Reconfigure the system ROOT logger to drop raw text and use our clean JSON formatter
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Clear any pre-existing default handlers to prevent string-based text collisions
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(GKEJsonFormatter())
root_logger.addHandler(log_handler)

# Capture and force Uvicorn log sub-channels to drop text headers and align with the root JSON configuration
for uvicorn_logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
    uvicorn_logger = logging.getLogger(uvicorn_logger_name)
    uvicorn_logger.handlers = []
    uvicorn_logger.propagate = True

# --- PYDANTIC APPLICATION SCHEMAS ---
class RAGQueryRequest(BaseModel):
    prompt: str
    context: str

class RAGQueryResponse(BaseModel):
    answer: str

# --- SYSTEM PERF & OBSERVABILITY MIDDLEWARE ---
@app.middleware("http")
async def cloud_logging_middleware(request: Request, call_next):
    """Tracks network transaction overhead metrics natively indexed by GCP."""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Milliseconds
    
    log_payload = {
        "severity": "INFO" if response.status_code < 400 else "WARNING",
        "message": f"{request.method} {request.url.path} responded {response.status_code} in {process_time:.2f}ms",
        "httpRequest": {
            "requestMethod": request.method,
            "requestUrl": str(request.url),
            "status": response.status_code,
            "latency": f"{process_time / 1000:.3f}s",
        },
        "component": "rag-backend-service",
    }
    
    root_logger.info(log_payload)
    return response

# --- SYSTEM EXCEPTION HANDLER ---
@app.exception_handler(Exception)
async def global_crash_exception_handler(request: Request, exc: Exception):
    """Interceptors unhandled failures and pushes stack traces to GCP Error Reporting."""
    if error_client:
        error_client.report_exception()
        
    log_payload = {
        "severity": "CRITICAL",
        "message": f"Unhandled exception encountered: {str(exc)}",
        "component": "rag-backend-service"
    }
    root_logger.error(log_payload)
    return {"detail": "Internal Server Error occurred during RAG pipeline processing."}

# --- APPLICATION CONTROLLERS ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "rag-backend"}

@app.post("/v1/query", response_model=RAGQueryResponse)
async def execute_rag_pipeline(payload: RAGQueryRequest):
    try:
        result_text = engine.generate_grounded_answer(
            prompt=payload.prompt,
            context=payload.context
        )
        return RAGQueryResponse(answer=result_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Orchestration Failure: {str(e)}")
