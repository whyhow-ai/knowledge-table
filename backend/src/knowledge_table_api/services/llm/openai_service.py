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

        # Initialize the OpenAI client
        openai_client = OpenAI(api_key=settings.openai_api_key)

        # Wrap the OpenAI client with instructor
        self.client = instructor.from_openai(openai_client)

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
            response_model=response_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response

    def get_embeddings(self) -> Any:
        """Get the embeddings for the language model."""
        return self.embeddings
