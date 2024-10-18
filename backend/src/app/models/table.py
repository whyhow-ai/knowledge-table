"""Table models for API requests and responses."""

from typing import Any, Dict, List, Union

from pydantic import BaseModel

from app.models.document import Document
from app.models.query_core import Rule


class Prompt(BaseModel):
    """Represents a prompt."""

    entityType: str
    id: str
    query: str
    rules: List[Rule]
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
    hidden: Union[bool, str]


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
