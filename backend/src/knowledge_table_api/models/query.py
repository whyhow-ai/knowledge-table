"""Query model."""

from typing import List, Literal, Optional

from pydantic import BaseModel


class Rule(BaseModel):
    """Rule model."""

    type: Literal["must_return", "may_return", "max_length"]
    options: Optional[List[str]] = None
    length: Optional[int] = None


class Chunk(BaseModel):
    """Chunk model."""

    content: str
    page: int


class Answer(BaseModel):
    """Answer model."""

    id: str
    document_id: str
    prompt_id: str
    answer: int | str | bool | List[int] | List[str] | None
    chunks: List[Chunk]
    type: Literal["int", "str", "bool", "int_array", "str_array"]
