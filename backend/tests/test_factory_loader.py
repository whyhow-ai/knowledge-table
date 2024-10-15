import pytest

from app.core.config import Settings
from app.services.loaders.factory import LoaderFactory
from app.services.loaders.pypdf_service import PDFLoader
from app.services.loaders.unstructured_service import UnstructuredLoader


def test_create_pypdf_loader():
    settings = Settings(loader="pypdf")
    loader = LoaderFactory.create_loader(settings)
    assert isinstance(loader, PDFLoader)


def test_create_unstructured_loader():
    settings = Settings(loader="unstructured", unstructured_api_key="test_key")
    loader = LoaderFactory.create_loader(settings)
    assert isinstance(loader, UnstructuredLoader)


def test_create_unstructured_loader_without_api_key():
    settings = Settings(loader="unstructured", unstructured_api_key=None)
    with pytest.raises(ValueError, match="Unstructured API key is required"):
        LoaderFactory.create_loader(settings)


def test_create_unknown_loader():
    settings = Settings(loader="unknown")
    loader = LoaderFactory.create_loader(settings)
    assert loader is None
