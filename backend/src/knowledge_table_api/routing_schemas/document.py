"""Document schemas for API requests and responses."""

from pydantic import BaseModel

from knowledge_table_api.models.document import Document


class DocumentCreate(BaseModel):
    """Schema for creating a new document."""

    name: str
    author: str
    tag: str
    page_count: int


class DocumentResponse(Document):
    """Schema for document response, inheriting from the Document model."""

    pass


class DeleteDocumentResponse(BaseModel):
    """Schema for delete document response."""

    id: str
    status: str
    message: str
