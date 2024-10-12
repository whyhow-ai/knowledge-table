"""Tests for the graph model"""

import pytest
from pydantic import ValidationError

from app.models.graph import (
    Chunk,
    Document,
    ExportData,
    Node,
    Relation,
    Triple,
)


def test_chunk_model():
    """Test the Chunk model."""
    chunk = Chunk(
        chunk_id="c1", content="Test content", page=1, triple_id="t1"
    )
    assert chunk.chunk_id == "c1"
    assert chunk.content == "Test content"
    assert chunk.page == 1
    assert chunk.triple_id == "t1"

    # Test with page as string
    chunk_str_page = Chunk(
        chunk_id="c2", content="Test content 2", page="ii", triple_id="t2"
    )
    assert chunk_str_page.page == "ii"

    # Test invalid chunk (missing required field)
    with pytest.raises(ValidationError):
        Chunk(content="Test content", page=1, triple_id="t1")


def test_document_model():
    """Test the Document model."""
    doc = Document(id="d1", name="Test Document")
    assert doc.id == "d1"
    assert doc.name == "Test Document"

    # Test invalid document (missing required field)
    with pytest.raises(ValidationError):
        Document(id="d1")


def test_node_model():
    """Test the Node model."""
    node = Node(label="Person", name="John Doe")
    assert node.label == "Person"
    assert node.name == "John Doe"

    # Test invalid node (missing required field)
    with pytest.raises(ValidationError):
        Node(label="Person")


def test_relation_model():
    """Test the Relation model."""
    relation = Relation(name="KNOWS")
    assert relation.name == "KNOWS"

    # Test invalid relation (missing required field)
    with pytest.raises(ValidationError):
        Relation()


def test_triple_model():
    """Test the Triple model."""
    head = Node(label="Person", name="John")
    tail = Node(label="Person", name="Jane")
    relation = Relation(name="KNOWS")
    triple = Triple(
        triple_id="t1",
        head=head,
        tail=tail,
        relation=relation,
        chunk_ids=["c1", "c2"],
    )
    assert triple.triple_id == "t1"
    assert triple.head == head
    assert triple.tail == tail
    assert triple.relation == relation
    assert triple.chunk_ids == ["c1", "c2"]

    # Test invalid triple (missing required field)
    with pytest.raises(ValidationError):
        Triple(head=head, tail=tail, relation=relation, chunk_ids=["c1", "c2"])


def test_export_data_model():
    """Test the ExportData model."""
    head = Node(label="Person", name="John")
    tail = Node(label="Person", name="Jane")
    relation = Relation(name="KNOWS")
    triple = Triple(
        triple_id="t1",
        head=head,
        tail=tail,
        relation=relation,
        chunk_ids=["c1", "c2"],
    )
    chunk = Chunk(
        chunk_id="c1", content="Test content", page=1, triple_id="t1"
    )

    export_data = ExportData(triples=[triple], chunks=[chunk.model_dump()])
    assert len(export_data.triples) == 1
    assert len(export_data.chunks) == 1
    assert export_data.triples[0] == triple
    assert export_data.chunks[0] == chunk.model_dump()

    # Test invalid export data (missing required field)
    with pytest.raises(ValidationError):
        ExportData(triples=[triple])


def test_model_conversions():
    """Test converting models to and from dictionaries."""
    # Create instances of all models
    chunk = Chunk(
        chunk_id="c1", content="Test content", page=1, triple_id="t1"
    )
    document = Document(id="d1", name="Test Document")
    node = Node(label="Person", name="John Doe")
    relation = Relation(name="KNOWS")
    triple = Triple(
        triple_id="t1",
        head=node,
        tail=Node(label="Person", name="Jane Doe"),
        relation=relation,
        chunk_ids=["c1"],
    )
    export_data = ExportData(triples=[triple], chunks=[chunk.model_dump()])

    # Test converting to dict and back for each model
    for model in [chunk, document, node, relation, triple, export_data]:
        model_dict = model.model_dump()
        assert isinstance(model_dict, dict)

        # Recreate the model from the dict
        recreated_model = type(model)(**model_dict)
        assert recreated_model == model


def test_from_attributes():
    """Test creating models from attributes (for models with from_attributes=True)."""

    class DummyORM:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

        def to_dict(self):
            return {
                k: v for k, v in self.__dict__.items() if not k.startswith("_")
            }

    # Test Triple
    orm_triple = DummyORM(
        triple_id="t1",
        head=DummyORM(label="Person", name="John"),
        tail=DummyORM(label="Person", name="Jane"),
        relation=DummyORM(name="KNOWS"),
        chunk_ids=["c1", "c2"],
    )

    # Convert DummyORM to dict
    triple_dict = {
        "triple_id": orm_triple.triple_id,
        "head": orm_triple.head.to_dict(),
        "tail": orm_triple.tail.to_dict(),
        "relation": orm_triple.relation.to_dict(),
        "chunk_ids": orm_triple.chunk_ids,
    }

    triple = Triple.model_validate(triple_dict)
    assert triple.triple_id == "t1"
    assert triple.head.name == "John"
    assert triple.tail.name == "Jane"
    assert triple.relation.name == "KNOWS"
    assert triple.chunk_ids == ["c1", "c2"]

    # Test ExportData
    orm_export_data = DummyORM(
        triples=[orm_triple],
        chunks=[
            {"chunk_id": "c1", "content": "Test", "page": 1, "triple_id": "t1"}
        ],
    )

    # Convert DummyORM to dict
    export_data_dict = {
        "triples": [triple_dict],
        "chunks": orm_export_data.chunks,
    }

    export_data = ExportData.model_validate(export_data_dict)
    assert len(export_data.triples) == 1
    assert len(export_data.chunks) == 1
    assert export_data.triples[0].triple_id == "t1"
    assert export_data.chunks[0]["chunk_id"] == "c1"
