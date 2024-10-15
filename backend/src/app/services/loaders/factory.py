"""Loader factory."""

import logging
from typing import Optional

from app.core.config import Settings
from app.services.loaders.base import LoaderService
from app.services.loaders.pypdf_service import PDFLoader
from app.services.loaders.unstructured_service import UnstructuredLoader

logger = logging.getLogger(__name__)


class LoaderFactory:
    """The factory for the loader services."""

    @staticmethod
    def create_loader(settings: Settings) -> Optional[LoaderService]:
        """Create a loader service."""
        loader_type = settings.loader
        logger.info(f"Creating loader of type: {loader_type}")

        try:
            if loader_type == "unstructured":
                if not settings.unstructured_api_key:
                    raise ValueError(
                        "Unstructured API key is required when using the unstructured loader"
                    )
                logger.info("Using UnstructuredLoader")
                return UnstructuredLoader(
                    unstructured_api_key=settings.unstructured_api_key
                )
            elif loader_type == "pypdf":
                logger.info("Using PyPDFLoader")
                return PDFLoader()
            else:
                logger.warning(f"No loader found for type: {loader_type}")
                return None
        except ValueError as ve:
            logger.error(f"Error creating loader: {str(ve)}")
            raise  # Re-raise the ValueError
        except Exception as e:
            logger.exception(f"Error creating loader: {str(e)}")
            return None
