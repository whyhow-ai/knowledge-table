"""The base class for the vector database services."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from langchain.schema import Document as LangchainDocument

from app.models.query import Rule
from app.schemas.query import VectorResponse


class VectorDBService(ABC):
    """The base class for the vector database services."""

    @abstractmethod
    async def upsert_vectors(
        self, vectors: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Upsert the vectors into the vector database."""
        pass

    @abstractmethod
    async def vector_search(
        self, queries: List[str], document_id: str
    ) -> VectorResponse:
        """Perform a vector search."""
        pass

    # Update other methods if they also return VectorResponse
    @abstractmethod
    async def keyword_search(
        self, query: str, document_id: str, keywords: List[str]
    ) -> VectorResponse:
        """Perform a keyword search."""
        pass

    @abstractmethod
    async def hybrid_search(
        self, query: str, document_id: str, rules: List[Rule]
    ) -> VectorResponse:
        """Perform a hybrid search."""
        pass

    @abstractmethod
    async def decomposed_search(
        self, query: str, document_id: str, rules: List[Rule]
    ) -> Dict[str, Any]:
        """Decomposition query."""
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> Dict[str, str]:
        """Delete the document from the vector database."""
        pass

    @abstractmethod
    async def ensure_collection_exists(self) -> None:
        """Ensure the collection exists in the vector database."""
        pass

    @abstractmethod
    async def prepare_chunks(
        self, document_id: str, chunks: List[LangchainDocument]
    ) -> List[Dict[str, Any]]:
        """Prepare chunks for insertion into the vector database."""
        pass
