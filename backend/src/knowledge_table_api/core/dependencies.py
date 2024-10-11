"""Dependencies for the application."""

from functools import lru_cache

from pymilvus import MilvusClient

from knowledge_table_api.core.config import Settings
from knowledge_table_api.services.llm.factory import LLMFactory
from knowledge_table_api.services.llm_service import LLMService


@lru_cache()
def get_settings() -> Settings:
    """Get the settings for the application."""
    return Settings()


def get_milvus_client() -> MilvusClient:
    """Get the Milvus client for the application."""
    settings = get_settings()
    return MilvusClient(
        "./milvus_demo.db",
        token=f"{settings.milvus_db_username}:{settings.milvus_db_password}",
    )


def get_llm_service() -> LLMService:
    """Get the LLM service for the application."""
    settings = get_settings()
    llm_service = LLMFactory.create_llm_service(settings.llm_provider)
    if llm_service is None:
        raise ValueError(
            f"Failed to create LLM service for provider: {settings.llm_provider}"
        )
    return llm_service
