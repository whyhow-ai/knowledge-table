from unittest.mock import AsyncMock, patch

import pytest

from app.models.query_core import Chunk
from app.schemas.query_api import QueryResult


@pytest.fixture(scope="session")
def mock_query_response():
    return QueryResult(
        answer="The capital of France is Paris.",
        chunks=[Chunk(content="Paris is the capital of France.", page=1)],
    )


def test_run_query_vector(
    client, mock_llm_service, mock_vector_db_service, mock_query_response
):
    request_data = {
        "document_id": "doc123",
        "prompt": {
            "id": "prompt123",
            "query": "What is the capital of France?",
            "type": "str",
            "entity_type": "text",
            "rules": [],
        },
    }

    # Create an async mock that returns the mock_query_response
    async_mock = AsyncMock(return_value=mock_query_response)

    with patch(
        "app.api.v1.endpoints.query.simple_vector_query",
        new=async_mock,
    ):
        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 200
    assert (
        response.json()["answer"]["answer"]
        == "The capital of France is Paris."
    )


def test_run_query_hybrid(
    client, mock_llm_service, mock_vector_db_service, mock_query_response
):
    request_data = {
        "document_id": "doc123",
        "prompt": {
            "id": "prompt123",
            "query": "Is Paris the capital of France?",
            "type": "bool",
            "entity_type": "text",
            "rules": [],
        },
    }

    # Create an async mock that returns the mock_query_response
    async_mock = AsyncMock(return_value=mock_query_response)

    with patch(
        "app.api.v1.endpoints.query.hybrid_query",
        new=async_mock,
    ):
        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 200
    assert (
        response.json()["answer"]["answer"]
        == "The capital of France is Paris."
    )
    assert len(response.json()["chunks"]) == 1
    assert (
        response.json()["chunks"][0]["content"]
        == "Paris is the capital of France."
    )
    assert response.json()["chunks"][0]["page"] == 1


def test_run_query_invalid_type(client):
    request_data = {
        "document_id": "doc123",
        "prompt": {
            "id": "prompt123",
            "query": "What is the capital of France?",
            "type": "invalid_type",
            "entity_type": "text",
            "rules": [],
        },
    }

    response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 422
    assert "Input should be" in response.json()["detail"][0]["msg"]
