"""Unstructured loader service."""

from typing import TYPE_CHECKING, List

from app.core.config import Settings
from app.services.loaders.base import LoaderService

if TYPE_CHECKING:
    from langchain.schema import Document

try:
    from langchain_unstructured import (
        UnstructuredLoader as LangchainUnstructuredLoader,
    )

    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False


class UnstructuredLoader(LoaderService):
    """Unstructured loader service."""

    def __init__(self, settings: Settings):
        """Initialize the UnstructuredLoader."""
        if not UNSTRUCTURED_AVAILABLE:
            raise ImportError(
                "The 'unstructured' package is not installed. "
                "Please install it using 'pip install .[unstructured]' to use the UnstructuredLoader."
            )
        self.settings = settings

    async def load(self, file_path: str) -> List["Document"]:
        """Load document from file path."""
        if not UNSTRUCTURED_AVAILABLE:
            raise ImportError(
                "The 'unstructured' package is not installed. "
                "Please install it using 'pip install .[unstructured]' to use the UnstructuredLoader."
            )
        loader = LangchainUnstructuredLoader(
            file_path, api_key=self.settings.unstructured_api_key
        )
        return loader.load()
