"""Service for interacting with OpenAI models."""

import asyncio
import logging
from typing import Any, List, Optional

from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from app.core.config import get_settings, Settings
from app.services.llm.base import LLMService

logger = logging.getLogger(__name__)


class OpenAIService(LLMService):
    """Service for interacting with OpenAI models."""

    def __init__(self) -> None:
        self.client: Optional[OpenAI] = None
        self.embeddings: Optional[OpenAIEmbeddings] = None
        if settings.is_openai_available:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
                dimensions=settings.dimensions,
            )

    def is_available(self) -> bool:
        """Check if the LLM service is available."""
        return self.client is not None and self.embeddings is not None

    async def generate_completion(
        self, prompt: str, response_model: Any
    ) -> Any:
        """Generate a completion from the language model."""
        response = self.client.beta.chat.completions.parse(  # type: ignore[union-attr]
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_model,
        )

        logger.info(
            f"Generated response: {response.choices[0].message.parsed}"
        )
        return response.choices[0].message.parsed

    async def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for text."""
        if not self.is_available():
            logger.warning(
                "OpenAI service is not available. Returning dummy embeddings."
            )
            return [0.0] * settings.dimensions

        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, self._get_embeddings_sync, text
        )
        return embeddings

    def _get_embeddings_sync(self, text: str) -> List[float]:
        if self.embeddings is None:
            logger.warning(
                "OpenAI embeddings are not available. Returning dummy embeddings."
            )
            return [0.0] * settings.dimensions
        return self.embeddings.embed_query(text)

    async def decompose_query(self, query: str) -> dict[str, Any]:
        """Decompose the query into smaller sub-queries."""
        if not self.is_available():
            logger.warning(
                "OpenAI service is not available. Returning original query."
            )
            return {"sub_queries": [query]}

        # Implement the actual decomposition logic here when OpenAI is available
        return {"sub_queries": [query]}
