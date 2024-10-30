"""OpenAI embedding service implementation."""

import logging
from typing import List

from langchain_openai import OpenAIEmbeddings

from app.core.config import Settings
from app.services.embedding.base import EmbeddingService

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService(EmbeddingService):
    """OpenAI embedding service implementation."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required but not set")
        
        self.embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.embedding_model
        )

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for text."""
        if self.embeddings is None:
            logger.warning(
                "OpenAI client is not initialized. Skipping embeddings."
            )
            return []

        return self.embeddings.embed_documents(texts)
