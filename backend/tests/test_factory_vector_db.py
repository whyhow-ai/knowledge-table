from unittest.mock import Mock, patch

from app.core.config import Settings
from app.schemas.query_api import VectorResponseSchema
from app.services.vector_db.base import VectorDBService
from app.services.vector_db.factory import VectorDBFactory


class MockVectorDBService(VectorDBService):
    """A concrete implementation of VectorDBService for testing"""

    def __init__(self, embedding_service, llm_service, settings):
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.settings = settings
        self.client = Mock()

    async def ensure_collection_exists(self) -> None:
        return None

    async def upsert_vectors(self, vectors):
        return {"status": "success"}

    async def vector_search(self, queries, document_id):
        return VectorResponseSchema(message="success", chunks=[])

    async def keyword_search(self, query, document_id, keywords):
        return VectorResponseSchema(message="success", chunks=[])

    async def hybrid_search(self, query, document_id, rules):
        return VectorResponseSchema(message="success", chunks=[])

    async def decomposed_search(self, query, document_id, rules):
        return {"status": "success"}

    async def delete_document(self, document_id):
        return {"status": "success"}


def test_create_supported_vector_db_service(
    mock_llm_service, mock_embeddings_service
):
    """Test that the factory creates a service for a supported provider"""
    settings = Settings(vector_db_provider="milvus")

    with patch(
        "app.services.vector_db.factory.MilvusService", MockVectorDBService
    ):
        vector_db_service = VectorDBFactory.create_vector_db_service(
            mock_embeddings_service, mock_llm_service, settings
        )
        assert isinstance(vector_db_service, VectorDBService)
        assert vector_db_service.embedding_service == mock_embeddings_service
        assert vector_db_service.llm_service == mock_llm_service
