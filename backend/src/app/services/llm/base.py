"""Abstract base class for language model services."""

from abc import ABC, abstractmethod
from typing import Any, List


class LLMService(ABC):
    """Abstract base class for language model services."""

    @abstractmethod
    async def generate_completion(
        self, prompt: str, response_model: Any
    ) -> Any:
        """Generate a completion from the language model."""
        pass

    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get the embeddings for the given text."""
        pass

    @abstractmethod
    async def decompose_query(self, query: str) -> dict[str, Any]:
        """Decompose the query into smaller sub-queries."""
        pass
