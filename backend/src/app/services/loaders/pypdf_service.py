"""PyPDF loader service."""

import os
from typing import List, Union

from langchain.schema import Document as LangchainDocument
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from app.services.loaders.base import LoaderService


class PDFLoader(LoaderService):
    """PDF and Text loader service."""

    async def load(self, file_path: str) -> List[LangchainDocument]:
        """Load document from file path."""
        file_extension = os.path.splitext(file_path)[1].lower()

        loader: Union[PyPDFLoader, TextLoader]

        if file_extension == ".pdf":
            loader = PyPDFLoader(file_path)
        elif file_extension == ".txt":
            loader = TextLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")

        return loader.load()
