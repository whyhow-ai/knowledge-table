from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app import main
from app.core.config import Settings, get_settings
from app.models.query_core import Chunk
from app.schemas.query_api import QueryResult
from app.services.document_service import DocumentService
from app.services.embedding.base import EmbeddingService
from app.services.llm.base import CompletionService
from app.services.vector_db.base import VectorDBService


def get_settings_override():
    return Settings(
        testing=True,
        database_url="test_db_url",
        chunk_size=1000,
        chunk_overlap=200,
        loader="test_loader",
        vector_db_provider="test_vector_db",
        llm_provider="test_provider",
        embedding_provider="test_provider",
        openai_api_key=None,
        embedding_model="test_embedding_model",
        dimensions=1536,
        llm_model="test_llm_model",
    )


@pytest.fixture(scope="session")
def test_settings():
    return get_settings_override()


@pytest.fixture(scope="session")
def test_app(test_settings):
    main.app.dependency_overrides[get_settings] = lambda: test_settings
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def client(test_app):
    return test_app


@pytest.fixture(scope="session")
def mock_embeddings_service(test_settings):
    service = AsyncMock(spec=EmbeddingService)
    service.get_embeddings.return_value = [[0.1, 0.2, 0.3]]
    service.settings = test_settings
    service.model = test_settings.embedding_model
    return service


@pytest.fixture(scope="session")
def mock_llm_service(test_settings):
    service = AsyncMock(spec=CompletionService)
    service.settings = test_settings
    service.model = test_settings.llm_model

    # Create a mock response that matches test expectations
    mock_response = QueryResult(
        answer="The capital of France is Paris.",
        chunks=[Chunk(content="Paris is the capital of France.", page=1)],
    )

    # Update the mock methods to return the same response
    service.generate_completion = AsyncMock(return_value=mock_response)
    service.generate_response = AsyncMock(return_value=mock_response)
    return service


@pytest.fixture(scope="session")
def mock_vector_db_service(
    mock_embeddings_service, mock_llm_service, test_settings
):
    service = AsyncMock(spec=VectorDBService)
    service.embedding_service = mock_embeddings_service
    service.llm_service = mock_llm_service
    service.settings = test_settings
    return service


@pytest.fixture(scope="session")
def document_service(test_settings, mock_vector_db_service, mock_llm_service):
    return DocumentService(
        mock_vector_db_service, mock_llm_service, test_settings
    )


@pytest.fixture(scope="session", autouse=True)
def mock_dependencies(
    mock_embeddings_service, mock_llm_service, mock_vector_db_service
):
    """Mock dependencies for API endpoints only"""
    with pytest.MonkeyPatch.context() as m:
        # Only mock the embedding and LLM factories
        m.setattr(
            "app.services.embedding.factory.EmbeddingServiceFactory.create_service",
            lambda *args, **kwargs: mock_embeddings_service,
        )
        m.setattr(
            "app.services.llm.factory.CompletionServiceFactory.create_service",
            lambda *args, **kwargs: mock_llm_service,
        )
        # Don't mock the vector DB factory as we want to test it
        yield
