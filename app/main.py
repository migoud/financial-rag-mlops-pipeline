import logging
import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from google.cloud import error_reporting
# Import the specialized local container handler
from google.cloud.logging.handlers import StructuredLogHandler

# Initialize core FastAPI app
app = FastAPI(title="Financial RAG Analytics Engine", version="1.0.0")

# Set up local GKE container standard output structured streams
logger = logging.getLogger("rag-backend-service")
logger.setLevel(logging.INFO)

# Direct all standard library logs into GKE's native container JSON collector
gke_handler = StructuredLogHandler()
logger.addHandler(gke_handler)

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
    
    # Passing 'json_fields' tells the StructuredLogHandler to populate jsonPayload
    log_payload = {
        "component": "rag-backend-service",
        "message": f"{request.method} {request.url.path} responded {response.status_code} in {process_time:.2f}ms",
        "latency_ms": process_time
    }
    
    if response.status_code < 400:
        logger.info("Transaction Success", extra={"json_fields": log_payload})
    else:
        logger.warning("Transaction Warning", extra={"json_fields": log_payload})
        
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
    logger.critical("System Pipeline Crash", extra={"json_fields": log_payload})
    return {"detail": "Internal Server Error occurred during RAG pipeline processing."}

# --- APPLICATION CONTROLLERS ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "rag-backend"}

@app.post("/v1/query", response_model=RAGQueryResponse)
async def execute_rag_pipeline(payload: RAGQueryRequest):
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
