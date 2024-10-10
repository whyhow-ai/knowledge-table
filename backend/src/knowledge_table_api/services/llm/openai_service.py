"""Service for interacting with OpenAI models."""

from typing import Any

import instructor
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from knowledge_table_api.core.config import settings

from .base import LLMService


class OpenAIService(LLMService):
    """Service for interacting with OpenAI models."""

    def __init__(self) -> None:
        openai_client = OpenAI(api_key=settings.openai_api_key)
        self.client = instructor.from_openai(openai_client)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=settings.dimensions,
        )

    async def generate_completion(
        self, prompt: str, response_model: Any, model: str = "gpt-4o"
    ) -> Any:
        """Generate a completion from the language model."""
        response = self.client.chat.completions.create(
            model=model,
            response_model=response_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response

    def get_embeddings(self) -> Any:
        """Get the embeddings for the language model."""
        return self.embeddings
