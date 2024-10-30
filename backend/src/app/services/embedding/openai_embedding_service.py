"""OpenAI embedding service implementation."""

import logging
from typing import List

from openai import OpenAI

from app.core.config import Settings
from app.services.embedding.base import EmbeddingService

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService(EmbeddingService):
    """OpenAI embedding service implementation."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required but not set")

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for text."""
        if self.client is None:
            logger.warning(
                "OpenAI client is not initialized. Skipping embeddings."
            )
            return []

        return [
            embedding.embedding
            for embedding in self.client.embeddings.create(
                input=texts, model=self.model
            ).data
        ]
