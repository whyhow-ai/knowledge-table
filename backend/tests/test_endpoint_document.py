from unittest.mock import AsyncMock

import pytest
from fastapi import status

from app.api.v1.endpoints.document import get_document_service
from app.main import app
from app.services.document_service import DocumentService


@pytest.fixture
def mock_document_service():
    return AsyncMock(spec=DocumentService)


def test_upload_document_endpoint(client, mock_document_service):
    # Given
    file_name = "test_document.txt"
    file_content = b"Test file content"
    document_id = "test_document_id"

    mock_document_service.upload_document.return_value = document_id

    # Override the get_document_service dependency
    app.dependency_overrides[get_document_service] = (
        lambda: mock_document_service
    )

    # When
    response = client.post(
        "/api/v1/document",
        files={"file": (file_name, file_content)},
    )

    # Then
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": document_id,
        "name": file_name,
        "author": "author_name",
        "tag": "document_tag",
        "page_count": 10,
    }

    # Clean up dependency overrides
    app.dependency_overrides.clear()


def test_delete_document_endpoint(client, mock_document_service):
    # Given
    document_id = "test_document_id"
    mock_document_service.delete_document.return_value = True

    # Override the get_document_service dependency
    app.dependency_overrides[get_document_service] = (
        lambda: mock_document_service
    )

    # When
    response = client.delete(f"/api/v1/document/{document_id}")

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": document_id,
        "status": "success",
        "message": "Document deleted successfully",
    }

    # Clean up dependency overrides
    app.dependency_overrides.clear()
