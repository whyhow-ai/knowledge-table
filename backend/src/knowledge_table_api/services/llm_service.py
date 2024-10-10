"""The service for the language model."""

from abc import ABC, abstractmethod
from typing import Any, Optional

import instructor

from knowledge_table_api.config import settings


class LLMService(ABC):
    """Abstract base class for language model services."""

    @abstractmethod
    async def generate_completion(
        self, prompt: str, response_model: Any
    ) -> Any:
        """Generate a completion from the language model."""
        pass

    @abstractmethod
    def get_embeddings(self) -> Any:
        """Get the embeddings for the language model."""
        pass


class OpenAIService(LLMService):
    """Service for interacting with OpenAI models."""

    def __init__(self) -> None:
        from langchain_openai import OpenAIEmbeddings
        from openai import OpenAI

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


class LLMFactory:
    """Factory for creating language model services."""

    @staticmethod
    def create_llm_service(provider: str = "openai") -> Optional[LLMService]:
        """Create a language model service."""
        if provider == "openai":
            return OpenAIService()
        # Add more providers here when needed
        return None
