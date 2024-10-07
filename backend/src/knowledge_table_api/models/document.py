"""Document model."""

from pydantic import BaseModel


class Document(BaseModel):
    """Document model."""

    id: str
    name: str
    author: str
    tag: str
    page_count: int
