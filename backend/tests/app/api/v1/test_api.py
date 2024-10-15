"""Tests for the main API router configuration."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.v1.api import api_router
from app.main import app


def test_api_router_configuration():
    """Test that the API router is configured correctly."""
    # GIVEN: The main FastAPI application with the API router included

    # WHEN: We inspect the routes of the API router
    routes = api_router.routes

    # THEN: The router should have the correct number of routes
    assert len(routes) == 4  # Update this number if it changes again

    # AND: Each route should have the correct path and methods
    expected_routes = [
        ("/document", ["POST"]),
        ("/document/{document_id}", ["DELETE"]),
        ("/graph/export-triples", ["POST"]),
        ("/query", ["POST"]),
    ]

    for route, (expected_path, expected_methods) in zip(
        routes, expected_routes
    ):
        assert route.path == expected_path
        assert set(route.methods) == set(expected_methods)


@pytest.mark.asyncio
async def test_api_endpoints_accessibility():
    """Test that the API endpoints are accessible."""
    client = TestClient(app)
    mock_llm_service = AsyncMock()
    mock_vector_db_service = AsyncMock()
    mock_document_service = AsyncMock()

    # Mock the vector generation
    mock_vector = [0.1] * 1536  # Assuming 1536-dimensional vector
    mock_llm_service.get_embeddings.return_value = mock_vector

    # Mock the document upload process
    mock_document_service.upload_document.return_value = "test_doc_id"
    mock_vector_db_service.prepare_chunks.return_value = [
        {"id": "chunk1", "vector": mock_vector, "text": "test content"}
    ]
    mock_vector_db_service.upsert_vectors.return_value = None

    with (
        patch(
            "app.core.dependencies.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.core.dependencies.get_vectordb_service",
            return_value=mock_vector_db_service,
        ),
        patch(
            "app.services.document_service.DocumentService",
            return_value=mock_document_service,
        ),
        patch(
            "app.services.vector_db.factory.VectorDBFactory.create_vector_db_service",
            return_value=mock_vector_db_service,
        ),
        patch("app.services.llm.openai_service.OpenAI"),
        patch("app.services.llm.openai_service.OpenAIEmbeddings"),
    ):

        responses = [
            client.post(
                "/api/v1/document",
                files={"file": ("test.txt", b"test content", "text/plain")},
            ),
            client.post("/api/v1/graph/export-triples", json={"table": {}}),
            client.post("/api/v1/query", json={"query": "test query"}),
        ]

    for response in responses:
        assert (
            response.status_code < 500
        ), f"Endpoint returned {response.status_code}: {response.text}"
        print(f"Response: {response.status_code} - {response.text}")
