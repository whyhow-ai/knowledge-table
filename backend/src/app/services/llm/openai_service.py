"""Service for interacting with OpenAI models."""

import asyncio
import logging
from typing import Any, List

from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from app.core.config import settings
from app.services.llm.base import LLMService

logger = logging.getLogger(__name__)


class OpenAIService(LLMService):
    """Service for interacting with OpenAI models."""

    def __init__(self) -> None:
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=settings.openai_api_key)

        # Initialize the embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            dimensions=settings.dimensions,
        )

    async def generate_completion(
        self, prompt: str, response_model: Any
    ) -> Any:
        """Generate a completion from the language model."""
        response = self.client.beta.chat.completions.parse(
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
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, self._get_embeddings_sync, text
        )
        return embeddings

    def _get_embeddings_sync(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)

    async def decompose_query(self, query: str) -> dict[str, Any]:
        """Decompose the query into smaller sub-queries."""
        return {"sub_queries": [query]}
