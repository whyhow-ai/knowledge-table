"""Document schemas for API requests and responses."""

from typing import Annotated

from pydantic import BaseModel, Field

from app.models.document import Document


class DocumentCreateSchema(BaseModel):
    """Schema for creating a new document."""

    name: str
    author: str
    tag: str
    page_count: Annotated[
        int, Field(strict=True, gt=0)
    ]  # This ensures page_count is a non-negative integer


class DocumentResponseSchema(Document):
    """Schema for document response, inheriting from the Document model."""

    pass


class DeleteDocumentResponseSchema(BaseModel):
    """Schema for delete document response."""

    id: str
    status: str
    message: str
