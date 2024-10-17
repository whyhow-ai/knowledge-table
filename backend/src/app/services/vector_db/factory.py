"""The factory for the vector database services."""

import logging
from typing import Optional

from app.core.config import Settings
from app.services.llm.base import LLMService
from app.services.vector_db.base import VectorDBService
from app.services.vector_db.milvus_service import MilvusService

logger = logging.getLogger(__name__)


class VectorDBFactory:
    """The factory for the vector database services."""

    @staticmethod
    def create_vector_db_service(
        llm_service: LLMService, settings: Settings
    ) -> Optional[VectorDBService]:
        """Create the vector database service."""
        logger.info(
            f"Creating vector database service with provider: {settings.vector_db_provider}"
        )
        if settings.vector_db_provider == "milvus":
            return MilvusService(llm_service, settings)
        # Add other vector database providers here
        logger.warning(
            f"Unsupported vector database provider: {settings.vector_db_provider}"
        )
        return None
