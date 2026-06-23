import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

# Instantiate the local test worker
client = TestClient(app)

def test_read_health_endpoint():
    """Validates cloud architecture liveness checks return 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "rag-backend"}

@patch("app.engine.RAGOrchestrationEngine.generate_grounded_answer")
def test_successful_rag_query_routing(mock_engine_call):
    """Verifies end-to-end API processing and schema compliance under a happy path."""
    # Mock out the external Gemini network dependency
    mock_engine_call.return_value = "In 2020, Canada's local currency GDP per capita was 50300.1 CAD."
    
    payload = {
        "prompt": "What was the local currency GDP per capita for Canada in 2020?",
        "context": "year: 2020 country_code: CAN gdp_per_capita_local_currency: 50300.1"
    }
    
    response = client.post("/v1/query", json=payload)
    
    # Assert network-level compliance
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "50300.1 CAD" in response.json()["answer"]
    
    # Ensure our engine script was safely triggered exactly once
    mock_engine_call.assert_called_once_with(
        prompt=payload["prompt"],
        context=payload["context"]
    )

def test_validation_error_on_invalid_payload():
    """Asserts that bad input data drops with a 422 standard validation code."""
    incomplete_payload = {
        "prompt": "Missing context parameters"
    }
    response = client.post("/v1/query", json=incomplete_payload)
    assert response.status_code == 422
