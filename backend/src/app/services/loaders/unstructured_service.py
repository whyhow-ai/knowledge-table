"""Unstructured loader service."""

from typing import List, Optional

from langchain.schema import Document
from langchain_community.document_loaders import UnstructuredFileLoader

from app.services.loaders.base import LoaderService


class UnstructuredDependencyError(ImportError):
    """Raised when the unstructured dependency is not installed."""


class UnstructuredLoader(LoaderService):
    """Unstructured loader service."""

    def __init__(self, unstructured_api_key: Optional[str] = None):
        """Initialize the UnstructuredLoader."""
        self.unstructured_api_key = unstructured_api_key

    @staticmethod
    def _check_unstructured_dependency() -> None:
        """Check if the unstructured dependency is installed."""
        try:
            import langchain_community.document_loaders.unstructured  # noqa: F401
            import unstructured  # noqa: F401
        except ImportError:
            raise UnstructuredDependencyError(
                "The unstructured package is not installed. "
                "Please install it with `pip install '.[unstructured]'` "
                "to use the UnstructuredService."
            )

    async def load(self, file_path: str) -> List[Document]:
        """Load document from file path."""
        self._check_unstructured_dependency()
        loader = UnstructuredFileLoader(
            file_path, unstructured_api_key=self.unstructured_api_key
        )
        return loader.load()

    async def load_and_split(self, file_path: str) -> List[Document]:
        """Load and split document from file path."""
        self._check_unstructured_dependency()
        loader = UnstructuredFileLoader(
            file_path, unstructured_api_key=self.unstructured_api_key
        )
        return loader.load_and_split()
