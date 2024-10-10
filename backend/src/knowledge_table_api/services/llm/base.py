"""Abstract base class for language model services."""

from abc import ABC, abstractmethod
from typing import Any


class LLMService(ABC):
    """Abstract base class for language model services."""

    @abstractmethod
    async def generate_completion(
        self, prompt: str, response_model: Any, model: str = "gpt-4o"
    ) -> Any:
        """Generate a completion from the language model."""
        pass

    @abstractmethod
    def get_embeddings(self) -> Any:
        """Get the embeddings for the language model."""
        pass
