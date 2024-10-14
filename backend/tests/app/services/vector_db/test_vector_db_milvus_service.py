"""Tests for the Milvus service"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain.schema import Document

from app.schemas.query import Chunk, Rule, VectorResponse
from app.services.llm_service import LLMService
from app.services.vector_db.milvus_service import MilvusService


@pytest.fixture
def mock_llm_service():
    mock = AsyncMock(spec=LLMService)
    # Only add methods that actually exist in LLMService
    mock.get_embeddings.return_value = [0.1, 0.2, 0.3]
    # If decompose_query exists in LLMService, uncomment the next line
    # mock.decompose_query.return_value = {"sub_queries": ["Sub-query 1", "Sub-query 2"]}
    return mock


@pytest.fixture
def milvus_service(mock_llm_service):
    with patch("app.services.vector_db.milvus_service.MilvusClient"):
        return MilvusService(mock_llm_service)


class TestMilvusService:

    @pytest.mark.asyncio
    async def test_get_embeddings_single_text(
        self, milvus_service, mock_llm_service
    ):
        text = "Sample text"
        expected_embedding = [0.1, 0.2, 0.3]
        mock_llm_service.get_embeddings.return_value = expected_embedding

        result = await milvus_service.get_embeddings(text)

        assert result == expected_embedding
        mock_llm_service.get_embeddings.assert_called_once_with(text)

    @pytest.mark.asyncio
    async def test_get_embeddings_multiple_texts(
        self, milvus_service, mock_llm_service
    ):
        texts = ["Text 1", "Text 2", "Text 3"]
        expected_embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]

        # Update the mock to return individual embeddings for each call
        mock_llm_service.get_embeddings.side_effect = expected_embeddings

        result = await milvus_service.get_embeddings(texts)

        assert result == expected_embeddings
        assert mock_llm_service.get_embeddings.call_count == len(texts)
        for text in texts:
            mock_llm_service.get_embeddings.assert_any_call(text)

    @pytest.mark.asyncio
    async def test_ensure_collection_exists_collection_doesnt_exist(
        self, milvus_service
    ):
        """
        Given: A MilvusService instance and a non-existent collection
        When: Calling ensure_collection_exists
        Then: It should create the collection with the correct schema and index
        """
        milvus_service.client.has_collection.return_value = False
        mock_schema = MagicMock()
        milvus_service.client.create_schema.return_value = mock_schema

        await milvus_service.ensure_collection_exists()

        milvus_service.client.has_collection.assert_called_once()
        milvus_service.client.create_schema.assert_called_once()
        mock_schema.add_field.assert_called()
        milvus_service.client.prepare_index_params.assert_called_once()
        milvus_service.client.create_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_vectors(self, milvus_service):
        vectors = [
            {"id": f"id_{i}", "vector": [0.1, 0.2, 0.3]} for i in range(1500)
        ]
        milvus_service.client.insert.return_value = {"insert_count": 1000}

        result = await milvus_service.upsert_vectors(vectors)

        assert result["message"].startswith("Successfully upserted")
        assert result["message"].endswith("chunks.")
        assert int(result["message"].split()[2]) >= 1500

    @pytest.mark.asyncio
    async def test_prepare_chunks(self, milvus_service):
        """
        Given: A MilvusService instance, a document_id, and a list of chunks
        When: Calling prepare_chunks
        Then: It should return a list of prepared data for insertion
        """
        document_id = "doc_1"
        chunks = [
            Document(page_content="Content 1", metadata={"page": 0}),
            Document(page_content="Content 2", metadata={"page": 1}),
        ]
        milvus_service.get_embeddings = AsyncMock(
            return_value=[[0.1, 0.2], [0.3, 0.4]]
        )

        result = await milvus_service.prepare_chunks(document_id, chunks)

        assert len(result) == 2
        assert all(isinstance(item, dict) for item in result)
        assert all(
            key in result[0]
            for key in [
                "id",
                "vector",
                "text",
                "page_number",
                "chunk_number",
                "document_id",
            ]
        )

    @pytest.mark.asyncio
    async def test_hybrid_search(self, milvus_service):
        """
        Given: A MilvusService instance, a query, a document_id, and rules
        When: Calling hybrid_search
        Then: It should return a VectorResponse with chunks
        """
        query = "Sample query"
        document_id = "doc_1"
        rules = [Rule(type="must_return", value="important")]
        milvus_service.get_embeddings = AsyncMock(return_value=[0.1, 0.2, 0.3])
        milvus_service.client.search.return_value = [
            [
                {
                    "entity": {
                        "text": "Result",
                        "page_number": 1,
                        "chunk_number": 1,
                    }
                }
            ]
        ]

        result = await milvus_service.hybrid_search(query, document_id, rules)

        assert isinstance(result, VectorResponse)
        assert len(result.chunks) == 1
        assert isinstance(result.chunks[0], Chunk)

    @pytest.mark.asyncio
    async def test_decomposed_search(self, milvus_service, mock_llm_service):
        query = "Complex query"
        document_id = "doc_1"
        rules = [Rule(type="must_return", value="important")]

        # Mock the decompose_query method
        mock_decompose_query = AsyncMock(
            return_value={"sub-queries": ["Sub-query 1", "Sub-query 2"]}
        )
        milvus_service.llm_service.decompose_query = mock_decompose_query

        # Mock the vector_search method
        mock_vector_search = AsyncMock(
            return_value=VectorResponse(
                message="Search completed successfully",
                chunks=[
                    Chunk(text="Chunk 1", content="Content 1", page=1),
                    Chunk(text="Chunk 2", content="Content 2", page=2),
                ],
            )
        )
        milvus_service.vector_search = mock_vector_search

        result = await milvus_service.decomposed_search(
            query, document_id, rules
        )

        # Print debug information
        print(f"Result: {result}")
        print(
            f"mock_decompose_query.call_count: {mock_decompose_query.call_count}"
        )
        print(
            f"mock_vector_search.call_count: {mock_vector_search.call_count}"
        )

        assert "chunks" in result, f"'chunks' not in result. Result: {result}"
        assert isinstance(
            result["chunks"], list
        ), f"Expected chunks to be a list, got {type(result['chunks'])}"
        assert (
            len(result["chunks"]) == 2
        ), f"Expected 2 chunks, got {len(result['chunks'])}"

        mock_decompose_query.assert_called_once_with(query=query)
        mock_vector_search.assert_called_once_with(
            ["Sub-query 1", "Sub-query 2"], document_id
        )

    @pytest.mark.asyncio
    async def test_delete_document(self, milvus_service):
        """
        Given: A MilvusService instance and a document_id
        When: Calling delete_document
        Then: It should delete the document and return a success status
        """
        document_id = "doc_1"
        milvus_service.client.query.return_value = []

        result = await milvus_service.delete_document(document_id)

        assert result["status"] == "success"
        milvus_service.client.delete.assert_called_once()
        milvus_service.client.query.assert_called_once()
