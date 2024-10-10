"""Factory for creating language model services."""

from typing import Optional

from .base import LLMService
from .openai_service import OpenAIService


class LLMFactory:
    """Factory for creating language model services."""

    @staticmethod
    def create_llm_service(provider: str = "openai") -> Optional[LLMService]:
        """Create a language model service."""
        if provider == "openai":
            return OpenAIService()
        # Add more providers here when needed
        return None
