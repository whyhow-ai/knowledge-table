"""Factory for creating language model services."""

import logging
from typing import Optional

from app.core.config import Settings
from app.services.llm.base import LLMService
from app.services.llm.openai_service import OpenAIService

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating language model services."""

    @staticmethod
    def create_llm_service(settings: Settings) -> Optional[LLMService]:
        """Create a language model service."""
        logger.info(f"Creating LLM service for provider: {settings.llm_provider}")
        if settings.llm_provider == "openai":
            return OpenAIService()
        # Add more providers here when needed
        return None
