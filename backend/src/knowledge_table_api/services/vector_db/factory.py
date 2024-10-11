"""The factory for the vector database services."""

import logging
from typing import Optional

from knowledge_table_api.core.config import settings
from knowledge_table_api.services.llm.base import LLMService
from knowledge_table_api.services.vector_db.base import VectorDBService
from knowledge_table_api.services.vector_db.milvus_service import MilvusService

logger = logging.getLogger(__name__)


class VectorDBFactory:
    """The factory for the vector database services."""

    @staticmethod
    def create_vector_db_service(
        llm_service: LLMService,
    ) -> Optional[VectorDBService]:
        """Create the vector database service."""
        logger.info(
            f"Creating vector DB service with provider: {settings.vector_db}"
        )
        if settings.vector_db.lower() == "milvus-lite":
            return MilvusService(llm_service)
        # Add more providers here as needed
        logger.error(f"Unsupported vector DB provider: {settings.vector_db}")
        return None
