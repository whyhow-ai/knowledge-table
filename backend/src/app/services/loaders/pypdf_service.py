"""PyPDF loader service."""

from typing import List

from langchain.schema import Document as LangchainDocument
from langchain_community.document_loaders import PyPDFLoader

from app.services.loaders.base import LoaderService


class PDFLoader(LoaderService):
    """PDF loader service."""

    async def load(self, file_path: str) -> List[LangchainDocument]:
        """Load document from file path."""
        loader = PyPDFLoader(file_path)
        return loader.load()
