"""Loader factory."""

import logging
from typing import Optional

from knowledge_table_api.core.config import Settings
from knowledge_table_api.services.loaders.base import LoaderService
from knowledge_table_api.services.loaders.pypdf_service import PDFLoader
from knowledge_table_api.services.loaders.unstructured_service import (
    UnstructuredLoader,
)

logger = logging.getLogger(__name__)


class LoaderFactory:
    """The factory for the loader services."""

    @staticmethod
    def create_loader(settings: Settings) -> Optional[LoaderService]:
        """Create the loader service."""
        logger.info(f"Creating loader of type: {settings.loader}")
        if settings.loader == "unstructured":
            logger.info("Using UnstructuredLoader")
            return UnstructuredLoader()
        elif settings.loader == "pypdf":
            logger.info("Using PyPDFLoader")
            return PDFLoader()
        else:
            logger.warning(f"No loader found for type: {settings.loader}")
            return None
