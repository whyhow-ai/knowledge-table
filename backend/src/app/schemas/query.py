"""Query schemas for API requests and responses."""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel

from app.models.query import Chunk, Rule


class QueryPrompt(BaseModel):
    """Query prompt schema."""

    id: str
    query: str
    type: Literal["int", "str", "bool", "int_array", "str_array"]
    entity_type: str
    rules: Optional[List[Rule]] = None


class QueryRequest(BaseModel):
    """Query request schema."""

    document_id: str
    previous_answer: Optional[Union[int, str, bool, List[int], List[str]]] = (
        None
    )
    prompt: QueryPrompt
    rag_type: Optional[Literal["vector", "hybrid", "decomposed"]] = "hybrid"


class VectorResponse(BaseModel):
    """Vector response schema."""

    message: str
    chunks: List[Chunk]
    keywords: Optional[List[str]] = None


class QueryResponse(BaseModel):
    """Query response schema."""

    id: str
    document_id: str
    prompt_id: str
    answer: Optional[Union[int, str, bool, List[int], List[str]]]
    chunks: List[Chunk]
    type: str
