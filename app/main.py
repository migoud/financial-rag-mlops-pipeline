import logging
import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from google.cloud import error_reporting
import google.cloud.logging  # <--- Official Cloud Logging SDK

# Initialize core FastAPI app
app = FastAPI(title="Financial RAG Analytics Engine", version="1.0.0")

# Setup Native Cloud Logging API Client Pipeline
try:
    logging_client = google.cloud.logging.Client()
    # This single line instantly binds the root logger directly to the GCP Logging API
    logging_client.setup_logging()
    logger = logging.getLogger("rag-backend-service")
except Exception:
    # Fallback to standard logging if client initialization drops locally
    logger = logging.getLogger("rag-backend-service")
    logger.setLevel(logging.INFO)

try:
    error_client = error_reporting.Client()
except Exception:
    error_client = None

# --- PYDANTIC APPLICATION SCHEMAS ---
class RAGQueryRequest(BaseModel):
    prompt: str
    context: str

class RAGQueryResponse(BaseModel):
    answer: str

# --- SYSTEM PERF & OBSERVABILITY MIDDLEWARE ---
@app.middleware("http")
async def cloud_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    # Passing structured dictionaries directly to the SDK logger forces jsonPayload packaging natively
    log_payload = {
        "component": "rag-backend-service",
        "message": f"{request.method} {request.url.path} responded {response.status_code} in {process_time:.2f}ms",
        "http_meta": {
            "requestMethod": request.method,
            "requestUrl": str(request.url),
            "status": response.status_code,
            "latency": f"{process_time / 1000:.3f}s"
        }
    }
    
    if response.status_code < 400:
        logger.info(log_payload)
    else:
        logger.warning(log_payload)
        
    return response

# --- SYSTEM EXCEPTION HANDLER ---
@app.exception_handler(Exception)
async def global_crash_exception_handler(request: Request, exc: Exception):
    if error_client:
        error_client.report_exception()
        
    log_payload = {
        "component": "rag-backend-service",
        "message": f"Unhandled exception encountered: {str(exc)}"
    }
    logger.critical(log_payload)
    return {"detail": "Internal Server Error occurred during RAG pipeline processing."}

# --- APPLICATION CONTROLLERS ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "rag-backend"}

@app.post("/v1/query", response_model=RAGQueryResponse)
async def execute_rag_pipeline(payload: RAGQueryRequest):
    # Dynamic runtime imports protect testing hooks
    from app.engine import RAGOrchestrationEngine
    engine = RAGOrchestrationEngine()
    try:
        result_text = engine.generate_grounded_answer(
            prompt=payload.prompt,
            context=payload.context
        )
        return RAGQueryResponse(answer=result_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Orchestration Failure: {str(e)}")
