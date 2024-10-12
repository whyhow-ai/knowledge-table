"""Tests for the document model"""

import pytest
from pydantic import ValidationError

from app.models.document import Document


def test_valid_document():
    """Test creating a valid Document instance."""
    doc = Document(
        id="doc123",
        name="Test Document",
        author="John Doe",
        tag="test",
        page_count=10,
    )
    assert doc.id == "doc123"
    assert doc.name == "Test Document"
    assert doc.author == "John Doe"
    assert doc.tag == "test"
    assert doc.page_count == 10


def test_invalid_document_missing_fields():
    """Test that creating a Document with missing fields raises a ValidationError."""
    with pytest.raises(ValidationError):
        Document(
            id="doc123",
            name="Test Document",
            # Missing author, tag, and page_count
        )


def test_invalid_document_wrong_types():
    """Test that creating a Document with wrong field types raises a ValidationError."""
    with pytest.raises(ValidationError):
        Document(
            id="doc123",
            name="Test Document",
            author="John Doe",
            tag="test",
            page_count="not a number",  # Should be an integer
        )


def test_document_model_to_dict():
    """Test that a Document instance can be converted to a dictionary."""
    doc = Document(
        id="doc123",
        name="Test Document",
        author="John Doe",
        tag="test",
        page_count=10,
    )
    doc_dict = doc.model_dump()
    assert isinstance(doc_dict, dict)
    assert doc_dict == {
        "id": "doc123",
        "name": "Test Document",
        "author": "John Doe",
        "tag": "test",
        "page_count": 10,
    }


def test_document_model_from_dict():
    """Test that a Document instance can be created from a dictionary."""
    doc_dict = {
        "id": "doc123",
        "name": "Test Document",
        "author": "John Doe",
        "tag": "test",
        "page_count": 10,
    }
    doc = Document(**doc_dict)
    assert doc.id == "doc123"
    assert doc.name == "Test Document"
    assert doc.author == "John Doe"
    assert doc.tag == "test"
    assert doc.page_count == 10
