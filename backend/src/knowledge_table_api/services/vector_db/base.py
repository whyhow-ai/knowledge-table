"""The base class for the vector database services."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from knowledge_table_api.models.query import Rule
from knowledge_table_api.routing_schemas.query import VectorResponse


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
    ) -> dict[str, Any]:
        """Search the vectors in the vector database."""
        pass

    @abstractmethod
    async def keyword_search(
        self, query: str, document_id: str, keywords: list[str]
    ) -> dict[str, Any]:
        """Search the keywords in the vector database."""
        pass

    @abstractmethod
    async def hybrid_search(
        self, query: str, document_id: str, rules: list[Rule]
    ) -> VectorResponse:
        """Search the vectors in the vector database."""
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> Dict[str, str]:
        """Delete the document from the vector database."""
        pass
