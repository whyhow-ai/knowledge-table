"""Abstract base class for language model services."""

from abc import ABC, abstractmethod
from typing import Any


class LLMService(ABC):
    """Abstract base class for language model services."""

    @abstractmethod
    async def generate_completion(
        self, prompt: str, response_model: Any
    ) -> Any:
        """Generate a completion from the language model."""
        pass

    @abstractmethod
    async def get_embeddings(self, text: str) -> list[float]:
        """Get the embeddings for the given text."""
        pass
