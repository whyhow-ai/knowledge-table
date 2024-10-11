"""Loader factory."""

from typing import Optional

from knowledge_table_api.core.config import Settings
from knowledge_table_api.services.loaders.base import LoaderService
from knowledge_table_api.services.loaders.pypdf_service import PDFLoader
from knowledge_table_api.services.loaders.unstructured_service import (
    UnstructuredLoader,
)


class LoaderFactory:
    """The factory for the loader services."""

    @staticmethod
    def create_loader(settings: Settings) -> Optional[LoaderService]:
        """Create the loader service."""
        if settings.loader == "pypdf":
            return PDFLoader()
        elif settings.loader == "unstructured":
            if settings.unstructured_api_key is None:
                raise ValueError("Unstructured API key is not set")
            return UnstructuredLoader(settings.unstructured_api_key)
        else:
            return None
