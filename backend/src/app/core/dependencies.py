"""Dependencies for the application."""

from functools import lru_cache

from fastapi import Depends

from app.core.config import Settings, settings
from app.services.document_service import DocumentService
from app.services.llm.factory import LLMFactory
from app.services.llm_service import LLMService
from app.services.vector_db.base import VectorDBService
from app.services.vector_db.factory import VectorDBFactory


@lru_cache()
def get_settings() -> Settings:
    """Get the settings for the application."""
    return settings


def get_llm_service() -> LLMService:
    """Get the LLM service for the application."""
    llm_service = LLMFactory.create_llm_service(settings.llm_provider)
    if llm_service is None:
        raise ValueError(
            f"Failed to create LLM service for provider: {settings.llm_provider}"
        )
    return llm_service


def get_vectordb_service() -> VectorDBService:
    """Get the vector database service for the application."""
    llm_service = get_llm_service()
    vectordb_service = VectorDBFactory.create_vector_db_service(
        settings.vector_db_provider, llm_service
    )
    if vectordb_service is None:
        raise ValueError(
            f"Failed to create vector database service for provider: {settings.vector_db_provider}"
        )
    return vectordb_service


def get_document_service(
    vector_db_service: VectorDBService = Depends(get_vectordb_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> DocumentService:
    """Get the document service for the application."""
    return DocumentService(vector_db_service, llm_service)
