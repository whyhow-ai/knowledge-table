"""Unstructured loader service."""

import logging
import warnings
from typing import List, Optional

from langchain.schema import Document
from langchain_unstructured import (
    UnstructuredLoader as LangchainUnstructuredLoader,
)

from knowledge_table_api.services.loaders.base import LoaderService

logger = logging.getLogger(__name__)


class UnstructuredLoader(LoaderService):
    """Unstructured loader service."""

    def __init__(self, unstructured_api_key: Optional[str] = None):
        """Initialize the UnstructuredLoader."""
        self.unstructured_api_key = unstructured_api_key
        if not self.unstructured_api_key:
            warning_message = (
                "Unstructured API key is not set. "
                "This may limit functionality or performance. "
                "Set UNSTRUCTURED_API_KEY in your environment or .env file."
            )
            warnings.warn(warning_message, UserWarning)
            logger.warning(warning_message)

    async def load(self, file_path: str) -> List[Document]:
        """Load document from file path."""
        loader = LangchainUnstructuredLoader(
            file_path, unstructured_api_key=self.unstructured_api_key
        )
        return loader.load()
