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
        if settings.openai_api_key:
            self.embeddings = OpenAIEmbeddings(
                model=self.settings.embedding_model
            )
        else:
            self.embeddings = None  # type: ignore
            logger.warning(
                "OpenAI API key is not set. LLM features will be disabled."
            )

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for text."""
        if self.embeddings is None:
            logger.warning(
                "OpenAI client is not initialized. Skipping embeddings."
            )
            return []

        return self.embeddings.embed_documents(texts)
