"""Tests for the base vector DB service"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain.schema import Document as LangchainDocument

from app.models.query import Rule
from app.services.vector_db.base import VectorDBService


class TestVectorDBService:

    @pytest.fixture
    def mock_vector_db_service(self):
        mock_service = MagicMock(spec=VectorDBService)
        mock_service.upsert_vectors = AsyncMock()
        mock_service.vector_search = AsyncMock()
        mock_service.keyword_search = AsyncMock()
        mock_service.hybrid_search = AsyncMock()
        mock_service.decomposed_search = AsyncMock()
        mock_service.delete_document = AsyncMock()
        mock_service.ensure_collection_exists = AsyncMock()
        mock_service.prepare_chunks = AsyncMock()
        return mock_service

    def test_abstract_class(self):
        """
        Given: The VectorDBService class
        When: Attempting to instantiate it directly
        Then: It should raise a TypeError
        """
        with pytest.raises(TypeError):
            VectorDBService()

    @pytest.mark.asyncio
    async def test_upsert_vectors(self, mock_vector_db_service):
        """
        Given: A mocked VectorDBService
        When: Calling upsert_vectors with a list of vectors
        Then: It should call the method with the correct arguments
        """
        vectors = [{"id": "1", "vector": [0.1, 0.2, 0.3]}]
        await mock_vector_db_service.upsert_vectors(vectors)
        mock_vector_db_service.upsert_vectors.assert_called_once_with(vectors)

    @pytest.mark.asyncio
    async def test_vector_search(self, mock_vector_db_service):
        """
        Given: A mocked VectorDBService
        When: Calling vector_search with queries and a document_id
        Then: It should call the method with the correct arguments
        """
        queries = ["test query"]
        document_id = "doc1"
        await mock_vector_db_service.vector_search(queries, document_id)
        mock_vector_db_service.vector_search.assert_called_once_with(
            queries, document_id
        )

    @pytest.mark.asyncio
    async def test_keyword_search(self, mock_vector_db_service):
        """
        Given: A mocked VectorDBService
        When: Calling keyword_search with a query, document_id, and keywords
        Then: It should call the method with the correct arguments
        """
        query = "test query"
        document_id = "doc1"
        keywords = ["keyword1", "keyword2"]
        await mock_vector_db_service.keyword_search(
            query, document_id, keywords
        )
        mock_vector_db_service.keyword_search.assert_called_once_with(
            query, document_id, keywords
        )

    @pytest.mark.asyncio
    async def test_hybrid_search(self, mock_vector_db_service):
        """
        Given: A mocked VectorDBService
        When: Calling hybrid_search with a query, document_id, and rules
        Then: It should call the method with the correct arguments
        """
        query = "test query"
        document_id = "doc1"
        rules = [Rule(type="must_return", value="test")]
        await mock_vector_db_service.hybrid_search(query, document_id, rules)
        mock_vector_db_service.hybrid_search.assert_called_once_with(
            query, document_id, rules
        )

    @pytest.mark.asyncio
    async def test_decomposed_search(self, mock_vector_db_service):
        """
        Given: A mocked VectorDBService
        When: Calling decomposed_search with a query, document_id, and rules
        Then: It should call the method with the correct arguments
        """
        query = "test query"
        document_id = "doc1"
        rules = [Rule(type="must_return", value="test")]
        await mock_vector_db_service.decomposed_search(
            query, document_id, rules
        )
        mock_vector_db_service.decomposed_search.assert_called_once_with(
            query, document_id, rules
        )

    @pytest.mark.asyncio
    async def test_delete_document(self, mock_vector_db_service):
        """
        Given: A mocked VectorDBService
        When: Calling delete_document with a document_id
        Then: It should call the method with the correct arguments
        """
        document_id = "doc1"
        await mock_vector_db_service.delete_document(document_id)
        mock_vector_db_service.delete_document.assert_called_once_with(
            document_id
        )

    @pytest.mark.asyncio
    async def test_ensure_collection_exists(self, mock_vector_db_service):
        """
        Given: A mocked VectorDBService
        When: Calling ensure_collection_exists
        Then: It should call the method
        """
        await mock_vector_db_service.ensure_collection_exists()
        mock_vector_db_service.ensure_collection_exists.assert_called_once()

    @pytest.mark.asyncio
    async def test_prepare_chunks(self, mock_vector_db_service):
        """
        Given: A mocked VectorDBService
        When: Calling prepare_chunks with a document_id and a list of LangchainDocument objects
        Then: It should call the method with the correct arguments
        """
        document_id = "doc1"
        chunks = [
            LangchainDocument(page_content="chunk1"),
            LangchainDocument(page_content="chunk2"),
        ]
        await mock_vector_db_service.prepare_chunks(document_id, chunks)
        mock_vector_db_service.prepare_chunks.assert_called_once_with(
            document_id, chunks
        )
