import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app import main
from app.core.config import Settings, get_settings
from app.services.document_service import DocumentService
from app.services.llm.base import LLMService
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


@pytest.fixture(scope="module")
def test_app():
    main.app.dependency_overrides[get_settings] = get_settings_override
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def client():
    return TestClient(main.app)


@pytest.fixture(scope="module")
def test_settings():
    return get_settings_override()


@pytest.fixture(scope="module")
def mock_vector_db_service():
    return AsyncMock(spec=VectorDBService)


@pytest.fixture(scope="module")
def mock_llm_service():
    return AsyncMock(spec=LLMService)


@pytest.fixture
def mock_factories(mock_llm_service, mock_vector_db_service):
    original_llm_create = LLMFactory.create_llm_service
    original_vector_db_create = VectorDBFactory.create_vector_db_service

    LLMFactory.create_llm_service = MagicMock(return_value=mock_llm_service)
    VectorDBFactory.create_vector_db_service = MagicMock(
        return_value=mock_vector_db_service
    )

    yield

    LLMFactory.create_llm_service = original_llm_create
    VectorDBFactory.create_vector_db_service = original_vector_db_create


@pytest.fixture(scope="module")
def document_service(test_settings, mock_vector_db_service, mock_llm_service):
    return DocumentService(
        mock_vector_db_service, mock_llm_service, test_settings
    )

