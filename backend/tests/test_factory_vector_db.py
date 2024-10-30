from unittest.mock import Mock

import pytest

from app.core.config import Settings
from app.services.embedding.base import EmbeddingService
from app.services.llm.base import CompletionService
from app.services.vector_db.factory import VectorDBFactory
from app.services.vector_db.milvus_service import MilvusService


@pytest.fixture
def mock_llm_service():
    return Mock(spec=CompletionService)


@pytest.fixture
def mock_embeddings_service():
    return Mock(spec=EmbeddingService)


def test_create_milvus_service(mock_llm_service, mock_embeddings_service):
    settings = Settings(vector_db_provider="milvus")
    vector_db_service = VectorDBFactory.create_vector_db_service(
        mock_embeddings_service, mock_llm_service, settings
    )
    assert isinstance(vector_db_service, MilvusService)


def test_create_unknown_vector_db_service(mock_llm_service):
    settings = Settings(vector_db_provider="unknown")
    vector_db_service = VectorDBFactory.create_vector_db_service(
        mock_embeddings_service, mock_llm_service, settings
    )
    assert vector_db_service is None
