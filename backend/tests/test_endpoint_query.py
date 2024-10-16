from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.query_core import Chunk
from app.schemas.query_api import QueryResult


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_llm_service():
    return AsyncMock()


@pytest.fixture
def mock_simple_vector_query():
    return AsyncMock()


@pytest.fixture
def mock_hybrid_query():
    return AsyncMock()


@pytest.fixture
def mock_decomposition_query():
    return AsyncMock()


def test_run_query_vector(client, mock_llm_service, mock_simple_vector_query):
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

    mock_response = QueryResult(
        answer="The capital of France is Paris.",
        chunks=[Chunk(content="Paris is the capital of France.", page=1)],
    )
    mock_simple_vector_query.return_value = mock_response

    with (
        patch(
            "app.api.v1.endpoints.query.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.api.v1.endpoints.query.get_vector_db_service",
        ),
        patch(
            "app.api.v1.endpoints.query.simple_vector_query",
            mock_simple_vector_query,
        ),
    ):
        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 200
    assert response.json()["answer"] == "The capital of France is Paris."
    assert len(response.json()["chunks"]) == 1


def test_run_query_hybrid(client, mock_llm_service, mock_hybrid_query):
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

    mock_response = QueryResult(
        answer="Yes, Paris is the capital of France.",
        chunks=[Chunk(content="Paris is the capital of France.", page=1)],
    )
    mock_hybrid_query.return_value = mock_response

    with (
        patch(
            "app.api.v1.endpoints.query.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.api.v1.endpoints.query.get_vector_db_service",
        ),
        patch("app.api.v1.endpoints.query.hybrid_query", mock_hybrid_query),
    ):
        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 200
    assert response.json()["answer"] == "Yes, Paris is the capital of France."
    assert len(response.json()["chunks"]) == 1


def test_run_query_invalid_type(client, mock_llm_service):
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

    with (
        patch(
            "app.api.v1.endpoints.query.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.api.v1.endpoints.query.get_vector_db_service",
        ),
    ):
        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 422
    assert "Input should be" in response.json()["detail"][0]["msg"]


def test_run_query_empty_chunks(
    client, mock_llm_service, mock_simple_vector_query
):
    request_data = {
        "document_id": "doc123",
        "prompt": {
            "id": "prompt123",
            "query": "What is the capital of Atlantis?",
            "type": "str",
            "entity_type": "text",
            "rules": [],
        },
    }

    mock_response = QueryResult(answer="", chunks=[])
    mock_simple_vector_query.return_value = mock_response

    with (
        patch(
            "app.api.v1.endpoints.query.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.api.v1.endpoints.query.get_vector_db_service",
        ),
        patch(
            "app.api.v1.endpoints.query.simple_vector_query",
            mock_simple_vector_query,
        ),
    ):
        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 200
    assert response.json()["answer"] == ""
    assert len(response.json()["chunks"]) == 0


def test_run_query_internal_error(
    client, mock_llm_service, mock_simple_vector_query
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

    mock_simple_vector_query.side_effect = Exception("Internal error")

    with (
        patch(
            "app.api.v1.endpoints.query.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.api.v1.endpoints.query.get_vector_db_service",
        ),
        patch(
            "app.api.v1.endpoints.query.simple_vector_query",
            mock_simple_vector_query,
        ),
    ):
        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Internal server error"
