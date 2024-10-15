"""Unstructured loader service."""

from typing import List

from langchain.schema import Document
from langchain_unstructured import (
    UnstructuredLoader as LangchainUnstructuredLoader,
)

from app.core.config import Settings
from app.services.loaders.base import LoaderService


class UnstructuredLoader(LoaderService):
    """Unstructured loader service."""

    def __init__(self, settings: Settings):
        """Initialize the UnstructuredLoader."""
        self.settings = settings

    async def load(self, file_path: str) -> List[Document]:
        """Load document from file path."""
        loader = LangchainUnstructuredLoader(
            file_path, api_key=self.settings.unstructured_api_key
        )
        return loader.load()
