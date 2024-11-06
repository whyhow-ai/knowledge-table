"""The factory for the vector database services."""

import logging
from typing import Optional

from app.core.config import Settings
from app.services.embedding.base import EmbeddingService
from app.services.llm.base import CompletionService
from app.services.vector_db.base import VectorDBService
from app.services.vector_db.milvus_service import MilvusService
from app.services.vector_db.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class VectorDBFactory:
    """The factory for the vector database services."""

    @staticmethod
    def create_vector_db_service(
        embedding_service: EmbeddingService,
        llm_service: CompletionService,
        settings: Settings,
    ) -> Optional[VectorDBService]:
        """Create the vector database service."""
        logger.info(
            f"Creating vector database service with provider: {settings.vector_db_provider}"
        )
        provider = settings.vector_db_provider.lower()
        if provider == "milvus":
            return MilvusService(embedding_service, llm_service, settings)
        elif provider == "qdrant":
            return QdrantService(embedding_service, llm_service, settings)
        # Add other vector database providers here
        logger.warning(
            f"Unsupported vector database provider: {settings.vector_db_provider}"
        )
        return None
