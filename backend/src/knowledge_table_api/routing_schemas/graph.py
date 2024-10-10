"""Graph schemas for API requests and responses."""

from typing import Any, Dict, List

from pydantic import BaseModel

from knowledge_table_api.models.graph import Document
from knowledge_table_api.routing_schemas.query import QueryPrompt


class Cell(BaseModel):
    """Schema for a cell in the table."""

    answer: Dict[str, Any]
    columnId: str
    dirty: bool
    rowId: str


class Column(BaseModel):
    """Schema for a column in the table."""

    hidden: bool
    id: str
    prompt: QueryPrompt
    width: int


class Row(BaseModel):
    """Schema for a row in the table."""

    document: Document
    hidden: bool
    id: str


class Table(BaseModel):
    """Schema for a table."""

    columns: List[Column]
    rows: List[Row]
    cells: List[Cell]


class ExportTriplesRequest(BaseModel):
    """Schema for export triples request."""

    table: Table


class ExportTriplesResponse(BaseModel):
    """Schema for export triples response."""

    triples: List[Dict[str, Any]]
    chunks: List[Dict[str, Any]]
