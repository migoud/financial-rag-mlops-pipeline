import logging
import json
import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from google.cloud import error_reporting
from app.engine import RAGOrchestrationEngine

# Keep your original title and version
app = FastAPI(title="Financial RAG Analytics Engine", version="1.0.0")

# Initialize your decoupled core orchestration instance 
engine = RAGOrchestrationEngine()

# Initialize the GCP Error Reporting Client (auto-detects project credentials at runtime)
try:
    error_client = error_reporting.Client()
except Exception:
    # Fallback for local development if GCP credentials aren't initialized
    error_client = None

# Configure the standard python root logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag_application")

# Define your original Pydantic schemas
class RAGQueryRequest(BaseModel):
    prompt: str
    context: str

class RAGQueryResponse(BaseModel):
    answer: str

# --- CLOUD LOGGING MIDDLEWARE ---
@app.middleware("http")
async def cloud_logging_middleware(request: Request, call_next):
    """Intercepts requests to track latency and structure JSON logs for GCP."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Construct a structured JSON log entry that GCP Cloud Logging indexes perfectly
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
    
    print(json.dumps(log_payload))
    return response

# --- GLOBAL EXCEPTION HANDLER FOR ERROR REPORTING ---
@app.exception_handler(Exception)
async def global_crash_exception_handler(request: Request, exc: Exception):
    """Catches unhandled server errors and routes them straight to GCP Error Reporting."""
    if error_client:
        error_client.report_exception()
        
    log_payload = {
        "severity": "CRITICAL",
        "message": f"Unhandled exception encountered: {str(exc)}",
        "component": "rag-backend-service"
    }
    print(json.dumps(log_payload))
    
    return {"detail": "Internal Server Error occurred during RAG pipeline processing."}

# --- YOUR ORIGINAL ROUTES ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "rag-backend"}

@app.post("/v1/query", response_model=RAGQueryResponse)
async def execute_rag_pipeline(payload: RAGQueryRequest):
    try:
        # Route processing through your isolated engine script
        result_text = engine.generate_grounded_answer(
            prompt=payload.prompt,
            context=payload.context
        )
        return RAGQueryResponse(answer=result_text)
        
    except Exception as e:
        # FastAPI custom HTTPExceptions are fine, but an unhandled generic Exception 
        # here will now bubble up and get caught by our global_crash_exception_handler above!
        raise HTTPException(status_code=500, detail=f"Internal Orchestration Failure: {str(e)}")
