"""Factory for creating language model services."""

import logging
from typing import Optional

from app.services.llm.base import LLMService
from app.services.llm.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating language model services."""

    @staticmethod
    def create_llm_service(provider: str = "openai") -> Optional[LLMService]:
        """Create a language model service."""
        logger.info(f"Creating LLM service for provider: {provider}")
        if provider == "openai":
            return OpenAIService()
        # Add more providers here when needed
        return None
