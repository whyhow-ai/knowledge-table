"""Dependencies for the application."""

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.services.document_service import DocumentService
from app.services.llm.base import LLMService
from app.services.llm.factory import LLMFactory
from app.services.vector_db.base import VectorDBService
from app.services.vector_db.factory import VectorDBFactory


def get_llm_service(settings: Settings = Depends(get_settings)) -> LLMService:
    """Get the LLM service for the application."""
    llm_service = LLMFactory.create_llm_service(settings)
    if llm_service is None:
        raise ValueError(
            f"Failed to create LLM service for provider: {settings.llm_provider}"
        )
    return llm_service


def get_vector_db_service(
    settings: Settings = Depends(get_settings),
    llm_service: LLMService = Depends(get_llm_service),
) -> VectorDBService:
    """Get the vector database service for the application."""
    vector_db_service = VectorDBFactory.create_vector_db_service(
        llm_service, settings
    )
    if vector_db_service is None:
        raise ValueError(
            f"Failed to create vector database service for provider: {settings.vector_db_provider}"
        )
    return vector_db_service


def get_document_service(
    settings: Settings = Depends(get_settings),
    vector_db_service: VectorDBService = Depends(get_vector_db_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> DocumentService:
    """Get the document service for the application."""
    return DocumentService(vector_db_service, llm_service, settings)
