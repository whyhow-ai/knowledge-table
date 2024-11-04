"""Query model."""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel


class EntitySource(BaseModel):
    """Entity source model."""

    type: Literal["column", "global"]
    id: str


class ResolvedEntity(BaseModel):
    """Resolved entity model."""

    original: Union[str, List[str]]
    resolved: Union[str, List[str]]
    source: EntitySource
    entityType: str


class TransformationDict(BaseModel):
    """Transformation dictionary model."""

    original: Union[str, List[str]]
    resolved: Union[str, List[str]]


class Rule(BaseModel):
    """Rule model."""

    type: Literal["must_return", "may_return", "max_length", "resolve_entity"]
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
    answer: Optional[Union[int, str, bool, List[int], List[str]]]
    chunks: List[Chunk]
    type: str


QueryType = Literal["decomposition", "hybrid", "simple_vector"]
FormatType = Literal["int", "str", "bool", "int_array", "str_array"]
