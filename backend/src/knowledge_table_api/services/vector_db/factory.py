"""The factory for the vector database services."""

import logging
from typing import Optional

from knowledge_table_api.core.config import Settings
from knowledge_table_api.services.llm.base import LLMService
from knowledge_table_api.services.vector_db.base import VectorDBService
from knowledge_table_api.services.vector_db.milvus_service import MilvusService

logger = logging.getLogger(__name__)


class VectorDBFactory:
    """The factory for the vector database services."""

    @staticmethod
    def create_vector_db_service(
        provider: str, llm_service: LLMService, settings: Settings
    ) -> Optional[VectorDBService]:
        """Create the vector database service."""
        if provider.lower() == "milvus-lite":
            return MilvusService(llm_service, settings)
        # Add other vector database providers here
        return None
