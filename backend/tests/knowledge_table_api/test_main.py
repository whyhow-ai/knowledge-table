"""Tests for the main FastAPI application"""

from fastapi.testclient import TestClient
from knowledge_table_api.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
