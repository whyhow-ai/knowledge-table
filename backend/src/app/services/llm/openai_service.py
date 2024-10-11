"""Service for interacting with OpenAI models."""

from typing import Any

from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from app.core.config import settings

from .base import LLMService


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
        response = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_model,
        )
        return response

    async def get_embeddings(self, text: str) -> list[float]:
        """Generate embeddings for the given text."""
        embedding = self.embeddings.embed_query(text)
        return embedding
