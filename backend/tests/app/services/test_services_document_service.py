"""Tests for the document service"""

from unittest.mock import AsyncMock, patch

import pytest
from langchain.schema import Document as LangchainDocument

from app.services.document_service import DocumentService
from app.services.llm.base import LLMService
from app.services.loaders.factory import LoaderFactory
from app.services.vector_db.base import VectorDBService


@pytest.fixture
def mock_vector_db_service():
    return AsyncMock(spec=VectorDBService)


@pytest.fixture
def mock_llm_service():
    return AsyncMock(spec=LLMService)


@pytest.fixture
def document_service(mock_vector_db_service, mock_llm_service):
    return DocumentService(mock_vector_db_service, mock_llm_service)


@pytest.mark.asyncio
async def test_upload_document_success(
    document_service, mock_vector_db_service, mock_llm_service
):
    # Given
    filename = "test.txt"
    file_content = b"Test content"
    mock_document_id = "mock_document_id"
    mock_chunks = [LangchainDocument(page_content="Test content")]
    mock_prepared_chunks = [{"id": "1", "vector": [0.1, 0.2, 0.3]}]

    with patch.object(
        DocumentService, "_generate_document_id", return_value=mock_document_id
    ):
        with patch.object(
            DocumentService, "_process_document", new_callable=AsyncMock
        ) as mock_process:
            mock_process.return_value = mock_chunks
            mock_vector_db_service.prepare_chunks.return_value = (
                mock_prepared_chunks
            )

            # When
            result = await document_service.upload_document(
                filename, file_content
            )

    # Then
    assert result == mock_document_id
    mock_vector_db_service.prepare_chunks.assert_called_once_with(
        mock_document_id, mock_chunks
    )
    mock_vector_db_service.upsert_vectors.assert_called_once_with(
        mock_prepared_chunks
    )


@pytest.mark.asyncio
async def test_upload_document_failure(
    document_service, mock_vector_db_service, mock_llm_service
):
    # Given
    filename = "test.txt"
    file_content = b"Test content"

    with patch.object(
        DocumentService, "_process_document", new_callable=AsyncMock
    ) as mock_process:
        mock_process.side_effect = Exception("Processing failed")

        # When
        result = await document_service.upload_document(filename, file_content)

    # Then
    assert result is None


@pytest.mark.asyncio
async def test_process_document(document_service, mock_llm_service):
    # Given
    file_path = "test.txt"
    mock_docs = [LangchainDocument(page_content="Test content")]

    with patch.object(
        DocumentService, "_load_document", new_callable=AsyncMock
    ) as mock_load:
        mock_load.return_value = mock_docs
        with patch.object(
            document_service.splitter, "split_documents"
        ) as mock_split:
            mock_split.return_value = mock_docs

            # When
            result = await document_service._process_document(file_path)

    # Then
    assert result == mock_docs
    mock_load.assert_called_once_with(file_path)
    mock_split.assert_called_once_with(mock_docs)


@pytest.mark.asyncio
async def test_load_document_success(document_service, mock_llm_service):
    # Given
    file_path = "test.txt"
    mock_loader = AsyncMock()
    mock_loader.load.return_value = [
        LangchainDocument(page_content="Test content")
    ]

    with patch.object(
        LoaderFactory, "create_loader", return_value=mock_loader
    ):
        # When
        result = await document_service._load_document(file_path)

    # Then
    assert len(result) == 1
    assert isinstance(result[0], LangchainDocument)
    assert result[0].page_content == "Test content"


@pytest.mark.asyncio
async def test_load_document_failure(document_service, mock_llm_service):
    # Given
    file_path = "test.txt"

    with patch.object(LoaderFactory, "create_loader", return_value=None):
        # When / Then
        with pytest.raises(ValueError):
            await document_service._load_document(file_path)


def test_generate_document_id(mock_vector_db_service, mock_llm_service):
    # Given
    document_service = DocumentService(
        mock_vector_db_service, mock_llm_service
    )

    # When
    result = document_service._generate_document_id()

    # Then
    assert isinstance(result, str)
    assert len(result) == 32  # UUID4 hex representation length
