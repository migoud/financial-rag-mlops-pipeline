import os
from google import genai
from google.genai import types

class RAGOrchestrationEngine:
    def __init__(self):
        # Configure fallback identifiers matching your baseline workspace environment
        self.project_id = os.getenv("GCP_PROJECT", "project-2e0885aa-8f3e-4da5-86a")
        self.location = os.getenv("GCP_LOCATION", "us-central1")
        self.model_name = "gemini-2.5-flash"
        
        # Instantiate the explicit Vertex AI production system client
        self.client = genai.Client(vertexai=True, project=self.project_id, location=self.location)

    def generate_grounded_answer(self, prompt: str, context: str) -> str:
        """Injects retrieval context and queries the production LLM foundation block."""
        formatted_contents = f"{prompt} using context: {context}"
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=formatted_contents,
        )
        
        if not response.text:
            raise ValueError("Model engine returned an empty token generation output.")
            
        return response.text
