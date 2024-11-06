"""Graph model."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict


class Node(BaseModel):
    """Represents a node in the knowledge graph with a label and name."""

    label: str
    name: str
    properties: Optional[Dict[str, Any]] = None


class Relation(BaseModel):
    """Represents a relationship between two nodes in the knowledge graph."""

    name: str


class Triple(BaseModel):
    """Represents a triple in the knowledge graph, consisting of a head, tail, and relation."""

    triple_id: str
    head: Node
    tail: Node
    relation: Relation
    chunk_ids: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)


class GraphChunk(BaseModel):
    """Represents a chunk of content with associated metadata."""

    chunk_id: str
    content: str
    page: Union[int, str]
    triple_id: str
