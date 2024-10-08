"""Graph model."""

from typing import Any, Dict, List, Union

from pydantic import BaseModel


class Chunk(BaseModel):
    """Represents a chunk of content with associated metadata."""

    chunk_id: str
    content: str
    page: Union[int, str]
    triple_id: str


class Answer(BaseModel):
    """Represents an answer in a table cell with associated metadata and content chunks."""

    answer: Union[str, bool, int, float, List[str], List[int], List[float]]
    chunks: List[Dict[str, Any]]
    document_id: str
    id: str
    prompt_id: str
    type: str


class Cell(BaseModel):
    """Represents a cell in the table containing an answer and related information."""

    answer: Answer
    columnId: str
    dirty: bool
    rowId: str


class Prompt(BaseModel):
    """Represents a prompt used to extract specific information, including rules and query."""

    entityType: str
    id: str
    query: str
    rules: List[Any]
    type: str


class Column(BaseModel):
    """Represents a column in the table with its associated prompt and visibility settings."""

    hidden: bool
    id: str
    prompt: Prompt
    width: int


class Document(BaseModel):
    """Represents a document in the system with a name and an ID."""

    id: str
    name: str


class Node(BaseModel):
    """Represents a node in the knowledge graph with a label and name."""

    label: str
    name: str


class Relation(BaseModel):
    """Represents a relationship between two nodes in the knowledge graph."""

    name: str


class Row(BaseModel):
    """Represents a row in the table, associated with a document and visibility status."""

    document: Document
    hidden: bool
    id: str


class Table(BaseModel):
    """Represents a table consisting of rows, columns, and cells."""

    columns: List[Column]
    rows: List[Row]
    cells: List[Cell]


class Triple(BaseModel):
    """Represents a triple in the knowledge graph, consisting of a head, tail, and relation."""

    triple_id: str
    head: Node
    tail: Node
    relation: Relation
    chunk_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the Triple object into a dictionary."""
        return {
            "triple_id": self.triple_id,
            "head": self.head.model_dump(),
            "tail": self.tail.model_dump(),
            "relation": self.relation.model_dump(),
            "chunk_ids": self.chunk_ids,
        }


class ExportData(BaseModel):
    """Represents the exported data containing triples and content chunks."""

    triples: List[Triple]
    chunks: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the ExportData object into a dictionary."""
        return {
            "triples": [triple.to_dict() for triple in self.triples],
            "chunks": self.chunks,
        }
