"""Tests for the PyPDF service"""

from typing import List
from unittest.mock import patch

import pytest
from langchain.schema import Document as LangchainDocument

from app.services.loaders.pypdf_service import PDFLoader


@pytest.fixture
def mock_pypdf_loader():
    with patch("app.services.loaders.pypdf_service.PyPDFLoader") as mock:
        yield mock


@pytest.mark.asyncio
async def test_pdf_loader_load(mock_pypdf_loader):
    """
    Given: A PDFLoader instance and a file path
    When: The load method is called
    Then: It should return a list of LangchainDocument objects
    """
    # Given
    file_path = "test_document.pdf"
    mock_documents = [
        LangchainDocument(page_content="Test content 1", metadata={"page": 1}),
        LangchainDocument(page_content="Test content 2", metadata={"page": 2}),
    ]
    mock_pypdf_loader.return_value.load.return_value = mock_documents

    pdf_loader = PDFLoader()

    # When
    result = await pdf_loader.load(file_path)

    # Then
    assert isinstance(result, List)
    assert all(isinstance(doc, LangchainDocument) for doc in result)
    assert len(result) == 2
    assert result[0].page_content == "Test content 1"
    assert result[1].page_content == "Test content 2"

    mock_pypdf_loader.assert_called_once_with(file_path)
    mock_pypdf_loader.return_value.load.assert_called_once()


@pytest.mark.asyncio
async def test_pdf_loader_empty_document(mock_pypdf_loader):
    """
    Given: A PDFLoader instance and a file path to an empty document
    When: The load method is called
    Then: It should return an empty list
    """
    # Given
    file_path = "empty_document.pdf"
    mock_pypdf_loader.return_value.load.return_value = []

    pdf_loader = PDFLoader()

    # When
    result = await pdf_loader.load(file_path)

    # Then
    assert isinstance(result, List)
    assert len(result) == 0

    mock_pypdf_loader.assert_called_once_with(file_path)
    mock_pypdf_loader.return_value.load.assert_called_once()


@pytest.mark.asyncio
async def test_pdf_loader_exception_handling(mock_pypdf_loader):
    """
    Given: A PDFLoader instance and a file path that causes an exception
    When: The load method is called
    Then: It should raise the exception
    """
    # Given
    file_path = "non_existent.pdf"
    mock_pypdf_loader.return_value.load.side_effect = Exception(
        "File not found"
    )

    pdf_loader = PDFLoader()

    # When / Then
    with pytest.raises(Exception) as exc_info:
        await pdf_loader.load(file_path)

    assert str(exc_info.value) == "File not found"
    mock_pypdf_loader.assert_called_once_with(file_path)
    mock_pypdf_loader.return_value.load.assert_called_once()
