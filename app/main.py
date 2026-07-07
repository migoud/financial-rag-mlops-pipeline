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

# Initialize decoupled core orchestration instance 
engine = RAGOrchestrationEngine()

# Graceful Error Reporting setup for runtime environment independence
try:
    error_client = error_reporting.Client()
except Exception:
    error_client = None

# --- GKE PRODUCTION STRUCTURED LOGGING CONFIGURATION ---
class GKEJsonFormatter(logging.Formatter):
    """Formats Python log records into native single-line GCP jsonPayload dictionaries."""
    def format(self, record):
        if isinstance(record.msg, dict):
            log_entry = record.msg
        else:
            log_entry = {
                "message": record.getMessage(),
                "severity": record.levelname,
                "component": "rag-backend-service"
            }
        return json.dumps(log_entry)

# Redirect standard output streams to use our custom structural JSON formatter
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(GKEJsonFormatter())

logger = logging.getLogger("rag_application")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.propagate = False  # Blocks standard formatting duplication loops

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
    
    logger.info(log_payload)
    return response

# --- SYSTEM EXCEPTION HANDLER ---
@app.exception_handler(Exception)
async def global_crash_exception_handler(request: Request, exc: Exception):
    """Interceptors unhandled application failures and pushes stack traces to GCP Error Reporting."""
    if error_client:
        error_client.report_exception()
        
    log_payload = {
        "severity": "CRITICAL",
        "message": f"Unhandled exception encountered: {str(exc)}",
        "component": "rag-backend-service"
    }
    logger.error(log_payload)
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
