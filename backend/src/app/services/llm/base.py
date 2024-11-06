"""Abstract base class for language model completion services."""

from abc import ABC, abstractmethod
from typing import Any


class CompletionService(ABC):
    """Abstract base class for language model completion services."""

    @abstractmethod
    async def generate_completion(
        self, prompt: str, response_model: Any
    ) -> Any:
        """Generate a completion from the language model."""
        pass

    @abstractmethod
    async def decompose_query(self, query: str) -> dict[str, Any]:
        """Decompose the query into smaller sub-queries."""
        pass
