"""Factory for creating vector embedding services."""

from typing import Optional

from .base import VectorIndex
from .milvus import MilvusIndex
from .qdrant import QdrantIndex


class VectorIndexFactory:
    """Factory for creating vector embedding services."""

    @staticmethod
    def create_vector_index(provider: str = "milvus") -> Optional[VectorIndex]:
        """Create a language model service."""
        if provider == "milvus-lite":
            return MilvusIndex()
        elif provider == "qdrant":
            return QdrantIndex()
        return None
