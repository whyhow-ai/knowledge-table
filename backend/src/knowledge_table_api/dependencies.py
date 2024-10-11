"""Dependencies for the application."""

from functools import lru_cache

from knowledge_table_api.config import Settings
from knowledge_table_api.services.llm_service import LLMFactory, LLMService
from knowledge_table_api.services.vector_index import VectorIndexFactory
from knowledge_table_api.services.vector_index.base import VectorIndex


@lru_cache()
def get_settings() -> Settings:
    """Get the settings for the application."""
    return Settings()


def get_llm_service() -> LLMService:
    """Get the LLM service for the application."""
    settings = get_settings()
    llm_service = LLMFactory.create_llm_service(settings.llm_provider)
    if llm_service is None:
        raise ValueError(
            f"Failed to create LLM service for provider: {settings.llm_provider}"
        )
    return llm_service


def get_vector_index() -> VectorIndex:
    """Get the vector index for the application."""
    settings = get_settings()
    vector_index = VectorIndexFactory.create_vector_index(settings.vector_db)
    if vector_index is None:
        raise ValueError(
            f"Invalid value for vector database : {settings.vector_db}"
        )
    return vector_index
