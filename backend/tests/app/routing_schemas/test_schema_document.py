from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.document import Document
from app.schemas.document import (
    DeleteDocumentResponse,
    DocumentCreate,
    DocumentResponse,
)


class TestDocumentCreateSchema:
    def test_valid_document_create(self):
        # Given
        document_data = {
            "name": "Test Document",
            "author": "John Doe",
            "tag": "test",
            "page_count": 10,
        }

        # When
        document = DocumentCreate(**document_data)

        # Then
        assert document.name == "Test Document"
        assert document.author == "John Doe"
        assert document.tag == "test"
        assert document.page_count == 10

    def test_invalid_document_create_missing_field(self):
        # Given
        invalid_document_data = {
            "name": "Test Document",
            "author": "John Doe",
            "tag": "test",
            # Missing 'page_count' field
        }

        # When / Then
        with pytest.raises(ValidationError):
            DocumentCreate(**invalid_document_data)

    def test_invalid_document_create_wrong_type(self):
        # Given
        invalid_document_data = {
            "name": "Test Document",
            "author": "John Doe",
            "tag": "test",
            "page_count": "10",  # Should be an integer, not a string
        }

        # When / Then
        with pytest.raises(ValidationError) as exc_info:
            DocumentCreate(**invalid_document_data)

        # Additional assertion to check the error message
        assert "Input should be a valid integer" in str(exc_info.value)


class TestDocumentResponseSchema:
    def test_valid_document_response(self):
        # Given
        document_data = {
            "id": "doc123",
            "name": "Test Document",
            "author": "John Doe",
            "tag": "test",
            "page_count": 10,
            "created_at": datetime(2023, 4, 1, 12, 0, 0),
            "updated_at": datetime(2023, 4, 1, 12, 0, 0),
        }

        # When
        document = DocumentResponse(**document_data)

        # Then
        assert document.id == "doc123"
        assert document.name == "Test Document"
        assert document.author == "John Doe"
        assert document.tag == "test"
        assert document.page_count == 10

    def test_document_response_inherits_from_document_model(self):
        # Given / When
        document_response = DocumentResponse

        # Then
        assert issubclass(document_response, Document)


class TestDeleteDocumentResponseSchema:
    def test_valid_delete_document_response(self):
        # Given
        delete_response_data = {
            "id": "doc123",
            "status": "success",
            "message": "Document deleted successfully",
        }

        # When
        delete_response = DeleteDocumentResponse(**delete_response_data)

        # Then
        assert delete_response.id == "doc123"
        assert delete_response.status == "success"
        assert delete_response.message == "Document deleted successfully"

    def test_invalid_delete_document_response_missing_field(self):
        # Given
        invalid_delete_response_data = {
            "id": "doc123",
            "status": "success",
            # Missing 'message' field
        }

        # When / Then
        with pytest.raises(ValidationError):
            DeleteDocumentResponse(**invalid_delete_response_data)
