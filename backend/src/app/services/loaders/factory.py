"""Loader factory."""

import logging
from typing import Optional

from app.core.config import settings
from app.services.loaders.base import LoaderService
from app.services.loaders.pypdf_service import PDFLoader
from app.services.loaders.unstructured_service import UnstructuredLoader

logger = logging.getLogger(__name__)


class LoaderFactory:
    """The factory for the loader services."""

    @staticmethod
    def create_loader() -> Optional[LoaderService]:
        """Create a loader service."""
        loader_type = settings.loader
        logger.info(f"Creating loader of type: {loader_type}")

        try:
            if loader_type == "unstructured":
                logger.info("Using UnstructuredLoader")
                return UnstructuredLoader()
            elif loader_type == "pypdf":
                logger.info("Using PyPDFLoader")
                return PDFLoader()
            else:
                logger.warning(f"No loader found for type: {loader_type}")
                return None
        except Exception as e:
            logger.exception(f"Error creating loader: {str(e)}")
            return None
