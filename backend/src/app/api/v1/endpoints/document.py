"""Document router."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.dependencies import get_document_service
from app.models.document import Document
from app.schemas.document_api import (
    DeleteDocumentResponseSchema,
    DocumentResponseSchema,
)
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Document"])


@router.post(
    "",
    response_model=DocumentResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document_endpoint(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponseSchema:
    """
    Upload a document and process it.

    Parameters
    ----------
    file : UploadFile
        The file to be uploaded and processed.
    document_service : DocumentService
        The document service for processing the file.

    Returns
    -------
    DocumentResponse
        The processed document information.

    Raises
    ------
    HTTPException
        If the file name is missing or if an error occurs during processing.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is missing",
        )

    logger.info(
        f"Endpoint received file: {file.filename}, content type: {file.content_type}"
    )

    try:
        document_id = await document_service.upload_document(
            file.filename, await file.read()
        )

        if document_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing the document",
            )

        # TODO: Fetch actual document details from a database
        document = Document(
            id=document_id,
            name=file.filename,
            author="author_name",  # TODO: Determine this dynamically
            tag="document_tag",  # TODO: Determine this dynamically
            page_count=10,  # TODO: Determine this dynamically
        )
        return DocumentResponseSchema(**document.model_dump())

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


@router.delete("/{document_id}", response_model=DeleteDocumentResponseSchema)
async def delete_document_endpoint(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> DeleteDocumentResponseSchema:
    """
    Delete a document.

    Parameters
    ----------
    document_id : str
        The ID of the document to be deleted.
    document_service : DocumentService
        The document service for deleting the document.

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
        result = await document_service.delete_document(document_id)
        if result:
            return DeleteDocumentResponseSchema(
                id=document_id,
                status="success",
                message="Document deleted successfully",
            )
        else:
            return DeleteDocumentResponseSchema(
                id=document_id,
                status="error",
                message="Failed to delete document",
            )
    except ValueError as ve:
        logger.error(f"ValueError in delete_document_endpoint: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in delete_document_endpoint: {e}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred"
        )
