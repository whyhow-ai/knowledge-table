"""Graph model."""

from typing import Any, Dict, List, Union

from pydantic import BaseModel


class Chunk(BaseModel):
    """Represents a chunk of content with associated metadata."""

    chunk_id: str
    content: str
    page: Union[int, str]
    triple_id: str


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
