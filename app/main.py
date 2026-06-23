import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Financial RAG Analytics Engine", version="1.0.0")

# Initialize production-grade GenAI client explicitly utilizing Vertex AI backend routing
PROJECT_ID = os.getenv("GCP_PROJECT", "project-2e0885aa-8f3e-4da5-86a")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

class RAGQueryRequest(BaseModel):
    prompt: str
    context: str

class RAGQueryResponse(BaseModel):
    answer: str

@app.get("/health")
def health_check():
    """Liveness probe required by automated deployment environments."""
    return {"status": "healthy", "service": "rag-backend"}

@app.post("/v1/query", response_model=RAGQueryResponse)
async def execute_rag_pipeline(payload: RAGQueryRequest):
    """Executes production financial context injection against the baseline model."""
    try:
        formatted_contents = f"{payload.prompt} using context: {payload.context}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=formatted_contents,
        )
        
        if not response.text:
            raise HTTPException(status_code=502, detail="Empty generation response returned from model backend.")
            
        return RAGQueryResponse(answer=response.text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Orchestration Failure: {str(e)}")
