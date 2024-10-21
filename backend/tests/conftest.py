import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app import main
from app.core.config import Settings, get_settings
from app.services.document_service import DocumentService
from app.services.llm.factory import LLMFactory
from app.services.llm.openai_service import OpenAIService
from app.services.vector_db.base import VectorDBService
from app.services.vector_db.factory import VectorDBFactory


def get_settings_override():
    return Settings(
        testing=True,
        database_url=os.environ.get("DATABASE_TEST_URL"),
        chunk_size=1000,
        chunk_overlap=200,
        loader="test_loader",
        vector_db_provider="test_vector_db",
        llm_provider="test_llm",
        openai_api_key="test_api_key",
        embedding_model="test_embedding_model",
        dimensions=1536,
        llm_model="test_llm_model",
    )


@pytest.fixture(scope="session")
def test_settings():
    return get_settings_override()


@pytest.fixture(scope="session")
def mock_openai_client():
    return MagicMock()


@pytest.fixture(scope="session")
def mock_openai_embeddings():
    return MagicMock()


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
def mock_vector_db_service():
    return AsyncMock(spec=VectorDBService)


@pytest.fixture(scope="session")
def mock_llm_service():
    service = MagicMock(spec=OpenAIService)
    service.client = MagicMock()
    service.generate_completion.return_value = "Mocked completion"
    service.get_embeddings.return_value = [0.1, 0.2, 0.3]
    return service


@pytest.fixture
def mock_factories(mock_llm_service, mock_vector_db_service):
    with pytest.MonkeyPatch.context() as m:
        m.setattr(
            LLMFactory,
            "create_llm_service",
            lambda *args, **kwargs: mock_llm_service,
        )
        m.setattr(
            VectorDBFactory,
            "create_vector_db_service",
            lambda *args, **kwargs: mock_vector_db_service,
        )
        yield


@pytest.fixture(scope="session")
def document_service(test_settings, mock_vector_db_service, mock_llm_service):
    return DocumentService(
        mock_vector_db_service, mock_llm_service, test_settings
    )
