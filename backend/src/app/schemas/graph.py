"""Routing schemas for the graph API."""

from typing import Any, Dict, List, Union

from pydantic import BaseModel


class Prompt(BaseModel):
    """Represents a prompt used to extract specific information, including rules and query."""

    entityType: str
    id: str
    query: str
    rules: List[Any]
    type: str


class Cell(BaseModel):
    """Represents a cell in a table."""

    answer: Dict[str, Any]
    columnId: str
    dirty: Union[bool, str]
    rowId: str


class Column(BaseModel):
    """Represents a column in a table."""

    id: str
    prompt: Prompt
    width: Union[int, str]
    hidden: Union[bool, str]


class Document(BaseModel):
    """Represents a document."""

    id: str
    name: str
    author: str
    tag: str
    page_count: Union[int, str]


class Row(BaseModel):
    """Represents a row in a table."""

    id: str
    document: Document
    hidden: Union[bool, str]


class Table(BaseModel):
    """Represents a table."""

    columns: List[Column]
    rows: List[Row]
    cells: List[Cell]


class ExportTriplesRequest(BaseModel):
    """Schema for export triples request."""

    columns: List[Column]
    rows: List[Row]
    cells: List[Cell]


class ExportTriplesResponse(BaseModel):
    """Schema for export triples response."""

    triples: List[Dict[str, Any]]
    chunks: List[Dict[str, Any]]
