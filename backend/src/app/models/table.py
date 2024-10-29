"""Table models for API requests and responses."""

from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field

from app.models.document import Document
from app.models.query_core import Rule


class Prompt(BaseModel):
    """Represents a prompt in a column."""

    entityType: str
    id: str
    query: str
    rules: List[Rule]
    type: str


class TablePrompt(BaseModel):
    """Represents a prompt in a column."""

    entityType: str
    query: str
    rules: List[Rule]
    type: str


class Cell(BaseModel):
    """Represents a cell in a table."""

    answer: Union[str, List[str]]
    columnId: str
    dirty: Union[bool, str]
    rowId: str


class TableCell(BaseModel):
    """Represents a cell in a table."""

    answer: Dict[str, Any]
    columnId: str
    dirty: Union[bool, str]
    rowId: str


class Chunk(BaseModel):
    """Chunk model."""

    content: str
    page: int


class Row(BaseModel):
    """Represents a row in a table."""

    id: str
    sourceData: Union[Dict[str, Any], str] = Field(default_factory=dict)
    hidden: Union[bool, str]
    cells: Dict[str, Union[str, List[str]]]


class Column(BaseModel):
    """Represents a column in a table."""

    id: str
    hidden: Union[bool, str]
    entityType: str
    type: str
    generate: Union[bool, str]
    query: str
    rules: List[Rule]


class TableColumn(BaseModel):
    """Represents a column in a table."""

    id: str
    prompt: TablePrompt
    hidden: Union[bool, str]


class TableRow(BaseModel):
    """Represents a row in a table."""

    id: str
    document: Document
    hidden: Union[bool, str]


class Table(BaseModel):
    """Represents a table."""

    columns: List[TableColumn]
    rows: List[TableRow]
    cells: List[TableCell]
