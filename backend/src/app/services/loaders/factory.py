"""Loader factory."""

import logging
from typing import Optional

from app.core.config import Settings
from app.services.loaders.base import LoaderService
from app.services.loaders.pypdf_service import PDFLoader

logger = logging.getLogger(__name__)

# Attempt to import UnstructuredLoader, but don't raise an error if it fails
try:
    from app.services.loaders.unstructured_service import UnstructuredLoader

    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False
    logger.warning(
        "UnstructuredLoader is not available. Install the 'unstructured' extra to use it."
    )


class LoaderFactory:
    """The factory for the loader services."""

    @staticmethod
    def create_loader(settings: Settings) -> Optional[LoaderService]:
        """Create a loader service."""
        loader_type = settings.loader
        logger.info(f"Creating loader of type: {loader_type}")

        if loader_type == "unstructured":
            if not UNSTRUCTURED_AVAILABLE:
                logger.warning(
                    "The 'unstructured' package is not installed. "
                    "Please install it using 'pip install .[unstructured]' to use the UnstructuredLoader."
                )
                return None
            if not settings.unstructured_api_key:
                raise ValueError(
                    "Unstructured API key is required when using the unstructured loader"
                )
            logger.info("Using UnstructuredLoader")
            return UnstructuredLoader(settings=settings)
        elif loader_type == "pypdf":
            logger.info("Using PyPDFLoader")
            return PDFLoader()
        else:
            logger.warning(f"No loader found for type: {loader_type}")
            return None
