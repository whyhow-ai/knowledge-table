"""Document router."""

from fastapi import APIRouter, File, UploadFile

from knowledge_table_api.models.document import Document
from knowledge_table_api.services.document import upload_document
from knowledge_table_api.services.vector import delete_document

router = APIRouter(tags=["Document"], prefix="/document")


@router.post("", response_model=Document)
async def upload_document_endpoint(
    file: UploadFile = File(...),
) -> Document | dict[str, str]:
    """Upload a document and process it."""
    if file.filename is None:
        return {"message": "File name is missing"}
    document_id = await upload_document(
        file.content_type, file.filename, await file.read()
    )
    if document_id is None:
        return {"message": "An error occurred while processing the document"}

    document = Document(
        id=document_id,
        name=file.filename,
        author="author_name",
        tag="document_tag",
        page_count=10,
    )
    return document


@router.delete("/{document_id}", response_model=dict)
async def delete_document_endpoint(document_id: str) -> dict[str, str]:
    """Delete a document."""
    delete_document_response = await delete_document(document_id)

    # Delete the document
    return {
        "id": document_id,
        "status": delete_document_response["status"],
        "message": delete_document_response["message"],
    }
