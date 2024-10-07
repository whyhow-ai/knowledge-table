"""Query model."""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel


class Rule(BaseModel):
    """Rule model."""

    type: Literal["must_return", "may_return", "max_length"]
    options: Optional[List[str]] = None
    length: Optional[int] = None


class QueryPrompt(BaseModel):
    """Query prompt model."""

    id: str
    query: str
    type: Literal["int", "str", "bool", "int_array", "str_array"]
    entity_type: str
    rules: Optional[List[Rule]] = None


class QueryRequest(BaseModel):
    """Query request model."""

    document_id: str
    previous_answer: Optional[Union[int, str, bool, List[int], List[str]]] = (
        None
    )
    prompt: QueryPrompt
    rag_type: Optional[Literal["vector", "hybrid", "decomposed"]] = "hybrid"


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


class VectorResponse(BaseModel):
    """Vector response model."""

    message: str
    chunks: List[Chunk]
