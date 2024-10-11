"""Dependencies for the application."""

from functools import lru_cache

from knowledge_table_api.core.config import Settings
from knowledge_table_api.services.document_service import DocumentService
from knowledge_table_api.services.llm.factory import LLMFactory
from knowledge_table_api.services.llm_service import LLMService
from knowledge_table_api.services.vector_db.base import VectorDBService
from knowledge_table_api.services.vector_db.factory import VectorDBFactory


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


def get_vectordb_service() -> VectorDBService:
    """Get the vector database service for the application."""
    settings = get_settings()
    llm_service = get_llm_service()
    vectordb_service = VectorDBFactory.create_vector_db_service(
        settings.vector_db_provider, llm_service, settings
    )
    if vectordb_service is None:
        raise ValueError(
            f"Failed to create vector database service for provider: {settings.vector_db_provider}"
        )
    return vectordb_service


def get_document_service() -> DocumentService:
    """Get the document service for the application."""
    settings = get_settings()
    vector_db_service = get_vectordb_service()
    return DocumentService(settings, vector_db_service)
