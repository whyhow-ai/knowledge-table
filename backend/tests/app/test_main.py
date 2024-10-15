"""Tests for the main FastAPI application"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app, lifespan


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_settings():
    return MagicMock(
        PROJECT_NAME="Test Project",
        API_V1_STR="/api/v1",
        vector_db_provider="test_provider",
    )


@pytest.fixture
def mock_llm_service():
    return MagicMock()


@pytest.fixture
def mock_vector_db_service():
    return AsyncMock()


@pytest.mark.asyncio
async def test_lifespan(
    mock_settings, mock_llm_service, mock_vector_db_service
):
    # Given
    with (
        patch("app.main.get_settings", return_value=mock_settings),
        patch("app.main.get_llm_service", return_value=mock_llm_service),
        patch(
            "app.main.VectorDBFactory.create_vector_db_service",
            return_value=mock_vector_db_service,
        ),
        patch("app.main.logger") as mock_logger,
    ):

        # When
        async with lifespan(app):
            pass

        # Then
        mock_logger.info.assert_any_call(f"LLM Service: {mock_llm_service}")
        mock_logger.info.assert_any_call(
            f"Vector DB Provider: {mock_settings.vector_db_provider}"
        )
        mock_logger.info.assert_any_call(f"Loader: {mock_settings.loader}")
        mock_vector_db_service.ensure_collection_exists.assert_called_once()
        mock_logger.info.assert_any_call("Vector database collection ensured.")


@pytest.mark.asyncio
async def test_lifespan_vector_db_creation_failure(
    mock_settings, mock_llm_service
):
    # Given
    with (
        patch("app.main.get_settings", return_value=mock_settings),
        patch("app.main.get_llm_service", return_value=mock_llm_service),
        patch(
            "app.main.VectorDBFactory.create_vector_db_service",
            return_value=None,
        ),
        patch("app.main.logger") as mock_logger,
    ):

        # When/Then
        with pytest.raises(
            ValueError, match="Failed to create vector database service"
        ):
            async with lifespan(app):
                pass

        mock_logger.error.assert_called_with(
            "Failed to create vector database service. Check your configuration and ensure the correct provider is set."
        )


@pytest.mark.asyncio
async def test_lifespan_ensure_collection_failure(
    mock_settings, mock_llm_service, mock_vector_db_service
):
    # Given
    mock_vector_db_service.ensure_collection_exists.side_effect = Exception(
        "Test error"
    )

    with (
        patch("app.main.get_settings", return_value=mock_settings),
        patch("app.main.get_llm_service", return_value=mock_llm_service),
        patch(
            "app.main.VectorDBFactory.create_vector_db_service",
            return_value=mock_vector_db_service,
        ),
        patch("app.main.logger") as mock_logger,
    ):

        # When/Then
        with pytest.raises(Exception, match="Test error"):
            async with lifespan(app):
                pass

        mock_logger.error.assert_called_with(
            "Failed to ensure collection exists: Test error"
        )


def test_cors_middleware():
    # Given
    client = TestClient(app)
    origin = "http://testserver"

    # When
    response = client.options(
        f"{settings.API_V1_STR}/some_endpoint",
        headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
    )

    # Then
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "OPTIONS" in response.headers["access-control-allow-methods"]


def test_api_router_inclusion():
    # Given/When
    routes = [
        route
        for route in app.routes
        if route.path.startswith(settings.API_V1_STR)
    ]

    # Then
    assert len(routes) > 0


def test_read_root(client):
    # Given/When
    response = client.get("/")

    # Then
    assert response.status_code == 200
    assert response.json() == {"message": "hello, world."}
