from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.query import Chunk


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
        "rag_type": "vector",
        "prompt": {
            "id": "prompt123",
            "query": "What is the capital of France?",
            "type": "str",
            "entity_type": "text",
            "rules": [],
        },
    }

    mock_response = {
        "answer": "The capital of France is Paris.",
        "chunks": [
            Chunk(
                content="Paris is the capital of France.", page=1
            ).model_dump()
        ],
    }
    mock_simple_vector_query.return_value = mock_response

    with (
        patch(
            "app.api.v1.endpoints.query.get_llm_service",
            return_value=mock_llm_service,
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
        "rag_type": "hybrid",
        "prompt": {
            "id": "prompt123",
            "query": "Is Paris the capital of France?",
            "type": "bool",
            "entity_type": "text",
            "rules": [],
        },
    }

    mock_response = {
        "answer": "Yes, Paris is the capital of France.",
        "chunks": [
            Chunk(
                content="Paris is the capital of France.", page=1
            ).model_dump()
        ],
    }
    mock_hybrid_query.return_value = mock_response

    with (
        patch(
            "app.api.v1.endpoints.query.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch("app.api.v1.endpoints.query.hybrid_query", mock_hybrid_query),
    ):

        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 200
    assert response.json()["answer"] == "Yes, Paris is the capital of France."
    assert len(response.json()["chunks"]) == 1


def test_run_query_decomposed(
    client, mock_llm_service, mock_decomposition_query
):
    request_data = {
        "document_id": "doc123",
        "rag_type": "decomposed",
        "prompt": {
            "id": "prompt123",
            "query": "Compare the populations of Paris and London.",
            "type": "str",
            "entity_type": "text",
            "rules": [],
        },
    }

    mock_response = {
        "answer": "Paris has a population of about 2.2 million, while London has a population of about 9 million.",
        "chunks": [
            Chunk(
                content="Paris, the capital of France, has a population of approximately 2.2 million people.",
                page=1,
            ).model_dump(),
            Chunk(
                content="London, the capital of the United Kingdom, has a population of about 9 million inhabitants.",
                page=2,
            ).model_dump(),
        ],
    }
    mock_decomposition_query.return_value = mock_response

    with (
        patch(
            "app.api.v1.endpoints.query.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.api.v1.endpoints.query.decomposition_query",
            mock_decomposition_query,
        ),
    ):

        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 200
    assert (
        "Paris has a population of about 2.2 million"
        in response.json()["answer"]
    )
    assert (
        "London has a population of about 9 million"
        in response.json()["answer"]
    )
    assert len(response.json()["chunks"]) == 2


def test_run_query_invalid_type(client, mock_llm_service):
    request_data = {
        "document_id": "doc123",
        "rag_type": "invalid_type",
        "prompt": {
            "id": "prompt123",
            "query": "What is the capital of France?",
            "type": "str",
            "entity_type": "text",
            "rules": [],
        },
    }

    with patch(
        "app.api.v1.endpoints.query.get_llm_service",
        return_value=mock_llm_service,
    ):
        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 422
    assert any(
        "Input should be 'vector', 'hybrid' or 'decomposed'" in error["msg"]
        for error in response.json()["detail"]
    )


def test_run_query_empty_chunks(
    client, mock_llm_service, mock_simple_vector_query
):
    request_data = {
        "document_id": "doc123",
        "rag_type": "vector",
        "prompt": {
            "id": "prompt123",
            "query": "What is the capital of Atlantis?",
            "type": "str",
            "entity_type": "text",
            "rules": [],
        },
    }

    mock_response = {"answer": None, "chunks": []}
    mock_simple_vector_query.return_value = mock_response

    with (
        patch(
            "app.api.v1.endpoints.query.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.api.v1.endpoints.query.simple_vector_query",
            mock_simple_vector_query,
        ),
    ):

        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 200
    assert response.json()["answer"] is None
    assert len(response.json()["chunks"]) == 0


def test_run_query_internal_error(
    client, mock_llm_service, mock_simple_vector_query
):
    request_data = {
        "document_id": "doc123",
        "rag_type": "vector",
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
            "app.api.v1.endpoints.query.simple_vector_query",
            mock_simple_vector_query,
        ),
    ):

        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
