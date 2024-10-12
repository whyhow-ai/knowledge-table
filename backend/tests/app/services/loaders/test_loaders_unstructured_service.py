from typing import List
from unittest.mock import patch

import pytest
from langchain.schema import Document

from app.services.loaders.unstructured_service import UnstructuredLoader


@pytest.fixture
def mock_unstructured_file_loader():
    with patch(
        "app.services.loaders.unstructured_service.UnstructuredFileLoader"
    ) as mock:
        yield mock


@pytest.mark.asyncio
async def test_load_method(mock_unstructured_file_loader):
    file_path = "test_document.txt"
    mock_documents = [
        Document(
            page_content="Test content 1", metadata={"source": file_path}
        ),
        Document(
            page_content="Test content 2", metadata={"source": file_path}
        ),
    ]
    mock_unstructured_file_loader.return_value.load.return_value = (
        mock_documents
    )

    loader = UnstructuredLoader()
    with patch.object(UnstructuredLoader, "_check_unstructured_dependency"):
        result = await loader.load(file_path)

    assert isinstance(result, List)
    assert all(isinstance(doc, Document) for doc in result)
    assert len(result) == 2
    assert result[0].page_content == "Test content 1"
    assert result[1].page_content == "Test content 2"

    mock_unstructured_file_loader.assert_called_once_with(
        file_path, unstructured_api_key=None
    )
    mock_unstructured_file_loader.return_value.load.assert_called_once()


@pytest.mark.asyncio
async def test_load_and_split_method(mock_unstructured_file_loader):
    file_path = "test_document.txt"
    mock_documents = [
        Document(
            page_content="Test content 1", metadata={"source": file_path}
        ),
        Document(
            page_content="Test content 2", metadata={"source": file_path}
        ),
        Document(
            page_content="Test content 3", metadata={"source": file_path}
        ),
    ]
    mock_unstructured_file_loader.return_value.load_and_split.return_value = (
        mock_documents
    )

    loader = UnstructuredLoader()
    with patch.object(UnstructuredLoader, "_check_unstructured_dependency"):
        result = await loader.load_and_split(file_path)

    assert isinstance(result, List)
    assert all(isinstance(doc, Document) for doc in result)
    assert len(result) == 3
    assert result[0].page_content == "Test content 1"
    assert result[1].page_content == "Test content 2"
    assert result[2].page_content == "Test content 3"

    mock_unstructured_file_loader.assert_called_once_with(
        file_path, unstructured_api_key=None
    )
    mock_unstructured_file_loader.return_value.load_and_split.assert_called_once()


@pytest.mark.asyncio
async def test_load_with_api_key(mock_unstructured_file_loader):
    api_key = "test_api_key"
    file_path = "test_document.txt"
    loader = UnstructuredLoader(unstructured_api_key=api_key)
    with patch.object(UnstructuredLoader, "_check_unstructured_dependency"):
        await loader.load(file_path)

    mock_unstructured_file_loader.assert_called_once_with(
        file_path, unstructured_api_key=api_key
    )
