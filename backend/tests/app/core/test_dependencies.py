"""Tests for the dependencies module"""

import pytest
from unittest.mock import Mock, patch
from app.core.dependencies import get_settings, get_llm_service, get_vectordb_service, get_document_service
from app.core.config import Settings
from app.services.llm_service import LLMService
from app.services.vector_db.base import VectorDBService
from app.services.document_service import DocumentService

def test_get_settings():
    """Test that get_settings returns a Settings instance."""
    # GIVEN: The get_settings function is available

    # WHEN: get_settings is called
    settings = get_settings()

    # THEN: It should return a Settings instance
    assert isinstance(settings, Settings)

@patch('app.core.dependencies.LLMFactory')
def test_get_llm_service(mock_llm_factory):
    """Test that get_llm_service returns a LLMService instance."""
    # GIVEN: A mock LLM service is created
    mock_llm_service = Mock(spec=LLMService)
    mock_llm_factory.create_llm_service.return_value = mock_llm_service

    # WHEN: get_llm_service is called
    llm_service = get_llm_service()

    # THEN: It should return the mock LLM service and call the factory once
    assert llm_service == mock_llm_service
    mock_llm_factory.create_llm_service.assert_called_once()

@patch('app.core.dependencies.LLMFactory')
def test_get_llm_service_error(mock_llm_factory):
    """Test that get_llm_service raises ValueError when LLM service creation fails."""
    # GIVEN: The LLM factory returns None
    mock_llm_factory.create_llm_service.return_value = None

    # WHEN/THEN: get_llm_service is called, it should raise a ValueError
    with pytest.raises(ValueError):
        get_llm_service()

@patch('app.core.dependencies.VectorDBFactory')
@patch('app.core.dependencies.get_llm_service')
def test_get_vectordb_service(mock_get_llm_service, mock_vectordb_factory):
    """Test that get_vectordb_service returns a VectorDBService instance."""
    # GIVEN: Mock LLM and VectorDB services are created
    mock_llm_service = Mock(spec=LLMService)
    mock_get_llm_service.return_value = mock_llm_service
    mock_vectordb_service = Mock(spec=VectorDBService)
    mock_vectordb_factory.create_vector_db_service.return_value = mock_vectordb_service

    # WHEN: get_vectordb_service is called
    vectordb_service = get_vectordb_service()

    # THEN: It should return the mock VectorDB service and call the necessary functions
    assert vectordb_service == mock_vectordb_service
    mock_get_llm_service.assert_called_once()
    mock_vectordb_factory.create_vector_db_service.assert_called_once()

@patch('app.core.dependencies.VectorDBFactory')
@patch('app.core.dependencies.get_llm_service')
def test_get_vectordb_service_error(mock_get_llm_service, mock_vectordb_factory):
    """Test that get_vectordb_service raises ValueError when VectorDB service creation fails."""
    # GIVEN: The VectorDB factory returns None
    mock_llm_service = Mock(spec=LLMService)
    mock_get_llm_service.return_value = mock_llm_service
    mock_vectordb_factory.create_vector_db_service.return_value = None

    # WHEN/THEN: get_vectordb_service is called, it should raise a ValueError
    with pytest.raises(ValueError):
        get_vectordb_service()

@patch('app.core.dependencies.get_vectordb_service')
def test_get_document_service(mock_get_vectordb_service):
    """Test that get_document_service returns a DocumentService instance."""
    # GIVEN: A mock VectorDB service is created
    mock_vectordb_service = Mock(spec=VectorDBService)
    mock_get_vectordb_service.return_value = mock_vectordb_service

    # WHEN: get_document_service is called
    document_service = get_document_service()

    # THEN: It should return a DocumentService instance and call get_vectordb_service once
    assert isinstance(document_service, DocumentService)
    mock_get_vectordb_service.assert_called_once()