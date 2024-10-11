"""Unstructured loader service."""

from typing import List

from langchain.schema import Document as LangchainDocument
from langchain_community.document_loaders import UnstructuredFileLoader

from knowledge_table_api.services.loaders.base import LoaderService


class UnstructuredLoader(LoaderService):
    """Unstructured loader service."""

    def __init__(self, unstructured_api_key: str):
        """Initialize the UnstructuredLoader."""
        self.unstructured_api_key = unstructured_api_key

    async def load(self, file_path: str) -> List[LangchainDocument]:
        """Load document from file path."""
        if not self.unstructured_api_key:
            raise ValueError("UNSTRUCTURED_API_KEY is not set")
        loader = UnstructuredFileLoader(file_path)
        return loader.load()
