"""Unstructured loader service."""

from typing import List, Optional

from langchain.schema import Document
from langchain_unstructured import (
    UnstructuredLoader as LangchainUnstructuredLoader,
)

from app.services.loaders.base import LoaderService


class UnstructuredLoader(LoaderService):
    """Unstructured loader service."""

    def __init__(self, unstructured_api_key: Optional[str] = None):
        """Initialize the UnstructuredLoader."""
        self.unstructured_api_key = unstructured_api_key

    async def load(self, file_path: str) -> List[Document]:
        """Load document from file path."""
        loader = LangchainUnstructuredLoader(
            file_path, strategy="fast", mode="elements"
        )
        return loader.load()

    async def load_and_split(self, file_path: str) -> List[Document]:
        """Load and split document from file path."""
        loader = LangchainUnstructuredLoader(
            file_path, strategy="fast", mode="elements"
        )
        return loader.load_and_split()
