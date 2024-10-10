"""The factory for the vector database services."""

from typing import Optional

from knowledge_table_api.services.llm.base import LLMService

from .base import VectorDBService
from .milvus_service import MilvusService


class VectorDBFactory:
    """The factory for the vector database services."""

    @staticmethod
    def create_vector_db_service(
        llm_service: LLMService, provider: str = "milvus"
    ) -> Optional[VectorDBService]:
        """Create the vector database service."""
        if provider == "milvus":
            return MilvusService(llm_service)
        # Add more providers here when needed
        return None
