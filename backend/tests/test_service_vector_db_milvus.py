from unittest.mock import Mock

import pytest

from app.schemas.query_api import VectorResponseSchema
from app.services.vector_db.base import VectorDBService


class MockVectorDBService(VectorDBService):
    """A concrete implementation of VectorDBService for testing"""

    def __init__(self, embedding_service, llm_service, settings):
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.settings = settings
        self.client = Mock()

        # Set up synchronous return values
        self.client.has_collection.return_value = True
        self.client.insert.return_value = {"insert_count": 2}
        self.client.query.return_value = []
        self.client.search.return_value = [
            [{"entity": {"text": "result", "page_number": 1}}]
        ]
        self.client.delete.return_value = {"delete_count": 1}

    async def ensure_collection_exists(self) -> None:
        self.client.has_collection()
        return None

    async def upsert_vectors(self, vectors):
        result = self.client.insert()
        return {
            "status": "success",
            "message": f"Inserted {result['insert_count']} vectors",
        }

    async def vector_search(self, queries, document_id):
        # Mock using get_single_embedding
        for query in queries:
            _ = await self.get_single_embedding(query)
        return VectorResponseSchema(message="success", chunks=[])

    async def keyword_search(self, query, document_id, keywords):
        return VectorResponseSchema(message="success", chunks=[])

    async def hybrid_search(self, query, document_id, rules):
        # Mock using get_single_embedding
        _ = await self.get_single_embedding(query)
        return VectorResponseSchema(
            message="Query processed successfully.", chunks=[]
        )

    async def decomposed_search(self, query, document_id, rules):
        return {"status": "success"}

    async def delete_document(self, document_id):
        self.client.query()
        return {
            "status": "success",
            "message": "Document deleted successfully.",
        }


@pytest.fixture
def vector_db_service(
    mock_embeddings_service, mock_llm_service, test_settings
):
    return MockVectorDBService(
        embedding_service=mock_embeddings_service,
        llm_service=mock_llm_service,
        settings=test_settings,
    )


@pytest.mark.asyncio
async def test_ensure_collection_exists(vector_db_service):
    await vector_db_service.ensure_collection_exists()
    assert vector_db_service.client.has_collection.called


@pytest.mark.asyncio
async def test_upsert_vectors(vector_db_service):
    vectors = [
        {"id": "1", "vector": [0.1, 0.2]},
        {"id": "2", "vector": [0.3, 0.4]},
    ]

    result = await vector_db_service.upsert_vectors(vectors)

    assert result["status"] == "success"
    assert vector_db_service.client.insert.called


@pytest.mark.asyncio
async def test_hybrid_search(vector_db_service):
    query = "test query"
    document_id = "test_doc"
    rules = []

    result = await vector_db_service.hybrid_search(query, document_id, rules)

    assert isinstance(result, VectorResponseSchema)
    assert result.message == "Query processed successfully."


@pytest.mark.asyncio
async def test_delete_document(vector_db_service):
    document_id = "test_doc"

    result = await vector_db_service.delete_document(document_id)

    assert result["status"] == "success"
    assert result["message"] == "Document deleted successfully."


@pytest.mark.asyncio
async def test_get_single_embedding(vector_db_service):
    # Reset the mock before the test
    vector_db_service.embedding_service.get_embeddings.reset_mock()

    # Mock the embedding service to return a known value
    vector_db_service.embedding_service.get_embeddings.return_value = [
        [0.1, 0.2, 0.3]
    ]

    # Test getting a single embedding
    result = await vector_db_service.get_single_embedding("test text")

    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 3  # Length of our mock embedding
    assert result == [0.1, 0.2, 0.3]

    # Verify the embedding service was called correctly
    vector_db_service.embedding_service.get_embeddings.assert_called_once_with(
        ["test text"]
    )
