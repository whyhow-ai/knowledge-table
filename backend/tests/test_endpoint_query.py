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


@pytest.fixture(scope="session")
def mock_query_response_string_array():
    return QueryResult(
        answer=["Paris", "London", "Berlin"],
        chunks=[
            Chunk(
                content="European capitals include Paris, London, and Berlin.",
                page=1,
            )
        ],
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


def test_run_query_with_string_array(
    client,
    mock_llm_service,
    mock_vector_db_service,
    mock_query_response_string_array,
):
    request_data = {
        "document_id": "doc123",
        "prompt": {
            "id": "prompt123",
            "query": "List the European capitals mentioned.",
            "type": "str_array",
            "entity_type": "text",
            "rules": [],
        },
    }

    # Create a new mock for this specific test
    async_mock = AsyncMock(return_value=mock_query_response_string_array)

    # Reset any previous calls to vector_search
    mock_vector_db_service.vector_search.reset_mock()

    # Update the patches to target the correct paths
    with (
        patch(
            "app.api.v1.endpoints.query.hybrid_query",
            new=async_mock,
        ),
        patch.object(
            mock_llm_service,
            "generate_response",
            new=AsyncMock(return_value=mock_query_response_string_array),
        ),
        patch.object(
            mock_llm_service,
            "generate_completion",
            new=AsyncMock(return_value=mock_query_response_string_array),
        ),
    ):
        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 200
    assert response.json()["answer"]["answer"] == ["Paris", "London", "Berlin"]


@pytest.fixture(scope="session")
def mock_query_response_with_entities():
    return QueryResult(
        answer="The disease is Multiple Sclerosis and another disease is Amyotrophic Lateral Sclerosis.",
        chunks=[Chunk(content="The patient has ms and als.", page=1)],
    )


@pytest.fixture(scope="session")
def mock_query_response_string_array_with_entities():
    return QueryResult(
        answer=["Multiple Sclerosis", "Amyotrophic Lateral Sclerosis"],
        chunks=[Chunk(content="The patient has ms and als.", page=1)],
    )


def test_run_query_with_entity_resolution(
    client,
    mock_llm_service,
    mock_vector_db_service,
    mock_query_response_with_entities,
):
    request_data = {
        "document_id": "doc123",
        "prompt": {
            "id": "prompt123",
            "query": "What diseases are mentioned?",
            "type": "str",
            "entity_type": "text",
            "rules": [
                {
                    "type": "resolve_entity",
                    "options": [
                        "ms:Multiple Sclerosis",
                        "als:Amyotrophic Lateral Sclerosis",
                    ],
                }
            ],
        },
    }

    async_mock = AsyncMock(return_value=mock_query_response_with_entities)

    with patch(
        "app.api.v1.endpoints.query.hybrid_query",
        new=async_mock,
    ):
        response = client.post("/api/v1/query", json=request_data)

    assert response.status_code == 200
    assert (
        response.json()["answer"]["answer"]
        == "The disease is Multiple Sclerosis and another disease is Amyotrophic Lateral Sclerosis."
    )
