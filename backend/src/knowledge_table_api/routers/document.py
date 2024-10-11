"""Document router."""

import logging
from typing import Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from knowledge_table_api.dependencies import get_vector_index
from knowledge_table_api.models.document import Document
from knowledge_table_api.services.document import upload_document
from knowledge_table_api.services.vector_index.base import VectorIndex

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Document"], prefix="/document")


@router.post("", response_model=Document, status_code=status.HTTP_201_CREATED)
async def upload_document_endpoint(
    file: UploadFile = File(...),
) -> Document:
    """
    Upload a document and process it.

    Parameters
    ----------
    file : UploadFile
        The file to be uploaded and processed.

    Returns
    -------
    Document
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

    content_type = file.content_type
    filename = file.filename

    logger.info(
        f"Endpoint received file: {filename}, content type: {content_type}"
    )

    try:
        document_id = await upload_document(
            content_type, filename, await file.read()
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
    return document


@router.delete("/{document_id}", response_model=Dict[str, str])
async def delete_document_endpoint(
    document_id: str,
    vector_index: VectorIndex = Depends(get_vector_index),
) -> Dict[str, str]:
    """
    Delete a document.

    Parameters
    ----------
    document_id : str
        The ID of the document to be deleted.

    Returns
    -------
    Dict[str, str]
        A dictionary containing the deletion status and message.

    Raises
    ------
    HTTPException
        If an error occurs during the deletion process.
    """
    try:
        delete_document_response = await vector_index.delete_document(
            document_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return {
        "id": document_id,
        "status": delete_document_response["status"],
        "message": delete_document_response["message"],
    }
