"""Tests for the loader factory"""

from unittest.mock import patch

import pytest

from app.services.loaders.factory import LoaderFactory
from app.services.loaders.pypdf_service import PDFLoader
from app.services.loaders.unstructured_service import UnstructuredLoader


@pytest.fixture
def mock_settings():
    with patch("app.services.loaders.factory.settings") as mock_settings:
        yield mock_settings


@pytest.fixture
def mock_logger():
    with patch("app.services.loaders.factory.logger") as mock_logger:
        yield mock_logger


def test_create_loader_unstructured(mock_settings, mock_logger):
    """
    Given: The loader type is set to "unstructured" in settings
    When: create_loader is called
    Then: An UnstructuredLoader instance should be returned
    """
    mock_settings.loader = "unstructured"

    loader = LoaderFactory.create_loader()

    assert isinstance(loader, UnstructuredLoader)
    mock_logger.info.assert_any_call("Creating loader of type: unstructured")
    mock_logger.info.assert_any_call("Using UnstructuredLoader")


def test_create_loader_pypdf(mock_settings, mock_logger):
    """
    Given: The loader type is set to "pypdf" in settings
    When: create_loader is called
    Then: A PDFLoader instance should be returned
    """
    mock_settings.loader = "pypdf"

    loader = LoaderFactory.create_loader()

    assert isinstance(loader, PDFLoader)
    assert mock_logger.info.call_count == 2
    mock_logger.info.assert_any_call("Creating loader of type: pypdf")
    mock_logger.info.assert_any_call("Using PyPDFLoader")


def test_create_loader_unknown(mock_settings, mock_logger):
    """
    Given: The loader type is set to an unknown value in settings
    When: create_loader is called
    Then: None should be returned
    """
    mock_settings.loader = "unknown"

    loader = LoaderFactory.create_loader()

    assert loader is None
    mock_logger.info.assert_called_once_with(
        "Creating loader of type: unknown"
    )
    mock_logger.warning.assert_called_once_with(
        "No loader found for type: unknown"
    )


@patch("app.services.loaders.factory.UnstructuredLoader")
def test_unstructured_loader_instantiation(
    mock_unstructured_loader, mock_settings
):
    """
    Given: The loader type is set to "unstructured" in settings
    When: create_loader is called
    Then: UnstructuredLoader should be instantiated
    """
    mock_settings.loader = "unstructured"

    LoaderFactory.create_loader()

    mock_unstructured_loader.assert_called_once()


@patch("app.services.loaders.factory.PDFLoader")
def test_pdf_loader_instantiation(mock_pdf_loader, mock_settings):
    """
    Given: The loader type is set to "pypdf" in settings
    When: create_loader is called
    Then: PDFLoader should be instantiated
    """
    mock_settings.loader = "pypdf"

    LoaderFactory.create_loader()

    mock_pdf_loader.assert_called_once()


def test_create_loader_exception_handling(mock_settings, mock_logger):
    """
    Given: An exception occurs during loader creation
    When: create_loader is called
    Then: The exception should be logged and None should be returned
    """
    mock_settings.loader = "unstructured"

    with patch(
        "app.services.loaders.factory.UnstructuredLoader",
        side_effect=Exception("Test exception"),
    ):
        loader = LoaderFactory.create_loader()

    assert loader is None
    mock_logger.exception.assert_called_once_with(
        "Error creating loader: Test exception"
    )
