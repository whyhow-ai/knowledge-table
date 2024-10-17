"""Routing schemas for the graph API."""

from typing import Any, List

from pydantic import BaseModel

from app.models.graph import GraphChunk, Triple
from app.models.table import Cell, Column, Row


class PromptSchema(BaseModel):
    """Represents a prompt used to extract specific information, including rules and query."""

    entityType: str
    id: str
    query: str
    rules: List[Any]
    type: str


class ExportTriplesRequestSchema(BaseModel):
    """Schema for export triples request."""

    columns: List[Column]
    rows: List[Row]
    cells: List[Cell]


class ExportTriplesResponseSchema(BaseModel):
    """Schema for export triples response."""

    triples: List[Triple]
    chunks: List[GraphChunk]
