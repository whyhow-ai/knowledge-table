from unittest.mock import Mock, patch

import pytest

from app.schemas.query_api import VectorResponseSchema
from app.services.vector_db.qdrant_service import QdrantService


@pytest.fixture
def mock_qdrant_client():
    with patch("app.services.vector_db.qdrant_service.QdrantClient") as mock:
        client = Mock()
        # Set up mock responses
        client.collection_exists.return_value = True
        client.upsert.return_value = None

        # Use a simple Mock instead of Qdrant models
        response_mock = Mock()
        response_mock.points = [
            Mock(
                payload={
                    "text": "test text",
                    "page_number": 1,
                    "chunk_number": 1,
                    "document_id": "test_doc",
                }
            )
        ]
        client.query_points.return_value = response_mock

        client.delete.return_value = None
        mock.return_value = client
        yield client


@pytest.fixture
def qdrant_service(
    mock_embeddings_service,
    mock_llm_service,
    test_settings,
    mock_qdrant_client,
):
    service = QdrantService(
        embedding_service=mock_embeddings_service,
        llm_service=mock_llm_service,
        settings=test_settings,
    )
    # Override the client with our mock
    service.client = mock_qdrant_client
    return service


@pytest.mark.asyncio
async def test_ensure_collection_exists(qdrant_service):
    await qdrant_service.ensure_collection_exists()
    assert qdrant_service.client.collection_exists.called


@pytest.mark.asyncio
async def test_upsert_vectors(qdrant_service):
    vectors = [
        {
            "id": "1",
            "vector": [0.1, 0.2],
            "text": "test",
            "page_number": 1,
            "chunk_number": 1,
            "document_id": "doc1",
        }
    ]

    result = await qdrant_service.upsert_vectors(vectors)

    assert "message" in result
    assert qdrant_service.client.upsert.called


@pytest.mark.asyncio
async def test_vector_search(qdrant_service, mock_embeddings_service):
    mock_embeddings_service.get_embeddings.return_value = [[0.1, 0.2]]

    result = await qdrant_service.vector_search(["test query"], "test_doc")

    assert isinstance(result, VectorResponseSchema)
    assert result.message == "Query processed successfully."
    assert qdrant_service.client.query_points.called


@pytest.mark.asyncio
async def test_hybrid_search(qdrant_service, mock_embeddings_service):
    mock_embeddings_service.get_embeddings.return_value = [[0.1, 0.2]]

    with patch.object(
        qdrant_service,
        "extract_keywords",
        return_value=["keyword1", "keyword2"],
    ):
        result = await qdrant_service.hybrid_search(
            "test query", "test_doc", []
        )

        assert isinstance(result, VectorResponseSchema)
        assert result.message == "Query processed successfully."
        assert qdrant_service.client.query_points.called


@pytest.mark.asyncio
async def test_decomposed_search(qdrant_service, mock_llm_service):
    mock_llm_service.decompose_query.return_value = {
        "sub-queries": ["query1", "query2"]
    }

    result = await qdrant_service.decomposed_search(
        "test query", "test_doc", []
    )

    assert "sub_queries" in result
    assert "chunks" in result


@pytest.mark.asyncio
async def test_delete_document(qdrant_service):
    result = await qdrant_service.delete_document("test_doc")

    assert result["status"] == "success"
    assert result["message"] == "Document deleted successfully."
    assert qdrant_service.client.delete.called


@pytest.mark.asyncio
async def test_keyword_search_not_implemented(qdrant_service):
    with pytest.raises(NotImplementedError):
        await qdrant_service.keyword_search("query", "doc_id", ["keyword"])


@pytest.mark.asyncio
async def test_get_single_embedding(qdrant_service):
    # Reset the mock before the test
    qdrant_service.embedding_service.get_embeddings.reset_mock()

    # Mock the embedding service to return a known value
    qdrant_service.embedding_service.get_embeddings.return_value = [
        [0.1, 0.2, 0.3]
    ]

    # Test getting a single embedding
    result = await qdrant_service.get_single_embedding("test text")

    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 3
    assert result == [0.1, 0.2, 0.3]

    # Verify the embedding service was called correctly
    qdrant_service.embedding_service.get_embeddings.assert_called_once_with(
        ["test text"]
    )
