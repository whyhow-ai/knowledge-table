"""Graph model."""

from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any

class Chunk(BaseModel):
    chunk_id: str
    content: str
    page: Union[int, str]
    triple_id: str

class Answer(BaseModel):
    answer: Union[str, bool, int, float, List[str], List[int], List[float]]
    chunks: List[Dict[str, Any]] 
    document_id: str
    id: str
    prompt_id: str
    type: str

class Cell(BaseModel):
    answer: Answer
    columnId: str
    dirty: bool
    rowId: str

class Prompt(BaseModel):
    entityType: str
    id: str
    query: str
    rules: List[Any]
    type: str

class Column(BaseModel):
    hidden: bool
    id: str
    prompt: Prompt
    width: int

class Document(BaseModel):
    id: str
    name: str

class Node(BaseModel):
    label: str
    name: str

class Relation(BaseModel):
    name: str

class Row(BaseModel):
    document: Document
    hidden: bool
    id: str

class Table(BaseModel):
    columns: List[Column]
    rows: List[Row]
    cells: List[Cell]

class Triple(BaseModel):
    triple_id: str
    head: Node
    tail: Node
    relation: Relation
    chunk_ids: List[str]

    def to_dict(self):
        return {
            "triple_id": self.triple_id,
            "head": self.head.model_dump(),
            "tail": self.tail.model_dump(),
            "relation": self.relation.model_dump(),
            "chunk_ids": self.chunk_ids
        }

class ExportData(BaseModel):
    triples: List[Triple]
    chunks: List[dict]

    def to_dict(self):
        return {
            "triples": [triple.to_dict() for triple in self.triples],
            "chunks": self.chunks
        }