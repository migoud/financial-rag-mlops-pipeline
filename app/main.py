from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.engine import RAGOrchestrationEngine

app = FastAPI(title="Financial RAG Analytics Engine", version="1.0.0")

# Initialize your decoupled core orchestration instance 
engine = RAGOrchestrationEngine()

class RAGQueryRequest(BaseModel):
    prompt: str
    context: str

class RAGQueryResponse(BaseModel):
    answer: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "rag-backend"}

@app.post("/v1/query", response_model=RAGQueryResponse)
async def execute_rag_pipeline(payload: RAGQueryRequest):
    try:
        # Route processing through our isolated engine script
        result_text = engine.generate_grounded_answer(
            prompt=payload.prompt,
            context=payload.context
        )
        return RAGQueryResponse(answer=result_text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Orchestration Failure: {str(e)}")
