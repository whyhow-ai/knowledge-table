"""Query schemas for API requests and responses."""

from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict

from app.models.query_core import Chunk, FormatType, Rule


class QueryPromptSchema(BaseModel):
    """Schema for the prompt part of the query request."""

    id: str
    entity_type: str
    query: str
    type: FormatType
    rules: list[Rule] = []


class QueryRequestSchema(BaseModel):
    """Query request schema."""

    document_id: str
    prompt: QueryPromptSchema

    model_config = ConfigDict(extra="allow")


class VectorResponseSchema(BaseModel):
    """Vector response schema."""

    message: str
    chunks: List[Chunk]
    keywords: Optional[List[str]] = None


class QueryResult(BaseModel):
    """Query result schema."""

    answer: Any
    chunks: List[Chunk]


class QueryResponseSchema(BaseModel):
    """Query response schema."""

    id: str
    document_id: str
    prompt_id: str
    answer: Optional[Any] = None
    chunks: List[Chunk]
    type: str


class QueryAnswer(BaseModel):
    """Query answer model."""

    id: str
    document_id: str
    prompt_id: str
    answer: Optional[Union[int, str, bool, List[int], List[str]]]
    type: str


class QueryAnswerResponse(BaseModel):
    """Query answer response model."""

    answer: QueryAnswer
    chunks: List[Chunk]


# Type for search responses (used in service layer)
SearchResponse = Union[dict[str, List[Chunk]], VectorResponseSchema]
