"""Document router."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.dependencies import get_llm_service
from app.models.document import Document
from app.schemas.document import DeleteDocumentResponse, DocumentResponse
from app.services.document_service import DocumentService
from app.services.llm.base import LLMService
from app.services.vector_db.factory import VectorDBFactory

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Document"], prefix="/document")


@router.post(
    "", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED
)
async def upload_document_endpoint(
    file: UploadFile = File(...),
    llm_service: LLMService = Depends(get_llm_service),
) -> DocumentResponse:
    """
    Upload a document and process it.

    Parameters
    ----------
    file : UploadFile
        The file to be uploaded and processed.
    settings : Settings
        The application settings.
    llm_service : LLMService
        The LLM service.

    Returns
    -------
    DocumentResponse
        The processed document information.

    Raises
    ------
    HTTPException
        If the file name is missing or if an error occurs during processing.
    """
    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is missing",
        )

    # Get file metadata
    content_type = file.content_type
    filename = file.filename

    logger.info(
        f"Endpoint received file: {filename}, content type: {content_type}"
    )

    try:
        # Create the vector database service
        vector_db_service = VectorDBFactory.create_vector_db_service(
            settings.vector_db_provider, llm_service
        )
        if vector_db_service is None:
            raise ValueError("Failed to create vector database service")

        # Create the document service
        document_service = DocumentService(vector_db_service)

        # Upload the document
        document_id = await document_service.upload_document(
            filename, await file.read()
        )
    except ValueError as ve:
        logger.error(f"ValueError in upload_document_endpoint: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Unexpected error in upload_document_endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    if document_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the document",
        )

    # TODO: Fetch actual document details from a database
    document = Document(
        id=document_id,
        name=filename,
        author="author_name",  # TODO: Determine this dynamically
        tag="document_tag",  # TODO: Determine this dynamically
        page_count=10,  # TODO: Determine this dynamically
    )
    return DocumentResponse(**document.dict())


@router.delete("/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document_endpoint(document_id: str) -> DeleteDocumentResponse:
    """
    Delete a document.

    Parameters
    ----------
    document_id : str
        The ID of the document to be deleted.

    Returns
    -------
    DeleteDocumentResponse
        A response containing the deletion status and message.

    Raises
    ------
    HTTPException
        If an error occurs during the deletion process.
    """
    try:

        # Create the LLM service
        llm_service = get_llm_service()

        # Create the vector database service
        vector_db_service = VectorDBFactory.create_vector_db_service(
            settings.vector_db_provider, llm_service
        )
        if vector_db_service is None:
            raise ValueError("Failed to create vector database service")

        # Delete the document
        delete_document_response = await vector_db_service.delete_document(
            document_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return DeleteDocumentResponse(
        id=document_id,
        status=delete_document_response["status"],
        message=delete_document_response["message"],
    )
