from unittest.mock import patch

import pytest

from app.models.document import Document
from app.models.graph import GraphChunk, Node, Relation, Triple
from app.models.llm_responses import SchemaRelationship, SchemaResponseModel
from app.models.table import (
    Chunk,
    Table,
    TableCell,
    TableColumn,
    TablePrompt,
    TableRow,
)
from app.schemas.graph_api import ExportTriplesResponseSchema
from app.services.graph_service import (
    create_triple_for_row,
    generate_chunks_for_triple,
    generate_triples,
    generate_triples_for_relationship,
    get_cell_value,
    get_label,
    parse_table,
    process_table_and_generate_triples,
)


@pytest.fixture
def sample_table_data():
    return Table(
        rows=[
            TableRow(
                id="1",
                document=Document(
                    id="doc1",
                    name="Document 1",
                    author="Test Author",
                    tag="Test Tag",
                    page_count=10,
                ),
                hidden=False,
            )
        ],
        columns=[
            TableColumn(
                id="col1",
                prompt=TablePrompt(
                    id="prompt1",
                    entityType="Entity1",
                    type="text",
                    query="Query1",
                    rules=[],
                ),
                hidden=False,
            ),
            TableColumn(
                id="col2",
                prompt=TablePrompt(
                    id="prompt2",
                    entityType="Entity2",
                    type="text",
                    query="Query2",
                    rules=[],
                ),
                hidden=False,
            ),
        ],
        cells=[
            TableCell(
                rowId="1",
                columnId="col1",
                answer={
                    "answer": "Value1",
                    "chunks": [Chunk(content="Chunk1", page=1)],
                },
                dirty=False,
            ),
            TableCell(
                rowId="1",
                columnId="col2",
                answer={
                    "answer": "Value2",
                    "chunks": [Chunk(content="Chunk2", page=1)],
                },
                dirty=False,
            ),
        ],
    )


@pytest.mark.asyncio
async def test_parse_table(sample_table_data):
    result = await parse_table(sample_table_data)
    assert "table_data" in result
    assert len(result["table_data"]) == 1
    assert result["table_data"][0]["document_name"] == "Document 1"
    assert len(result["table_data"][0]["answers"]) == 2


@pytest.mark.asyncio
async def test_generate_triples(sample_table_data):
    schema = SchemaResponseModel(
        relationships=[
            SchemaRelationship(
                head="Entity1", relation="relates_to", tail="Entity2"
            )
        ]
    )
    result = await generate_triples(schema, sample_table_data)
    assert isinstance(result, ExportTriplesResponseSchema)
    assert len(result.triples) > 0
    assert len(result.chunks) > 0


def test_generate_triples_for_relationship(sample_table_data):
    relationship = SchemaRelationship(
        head="Entity1", relation="relates_to", tail="Entity2"
    )
    result = generate_triples_for_relationship(relationship, sample_table_data)
    assert len(result) == 1
    assert isinstance(result[0], Triple)


def test_create_triple_for_row(sample_table_data):
    relationship = SchemaRelationship(
        head="Entity1", relation="relates_to", tail="Entity2"
    )
    row = sample_table_data.rows[0]
    result = create_triple_for_row(relationship, row, sample_table_data)
    assert isinstance(result, Triple)


def test_get_cell_value(sample_table_data):
    row = sample_table_data.rows[0]
    result = get_cell_value("Entity1", row, sample_table_data)
    assert result == "Value1"


def test_get_label():
    assert get_label("Document") == "Document"
    assert get_label("Entity") == "Entity"


def test_generate_chunks_for_triple(sample_table_data):
    triple = Triple(
        triple_id="t1",
        head=Node(label="Entity1", name="Value1"),
        tail=Node(label="Entity2", name="Value2"),
        relation=Relation(name="relates_to"),
    )
    result = generate_chunks_for_triple(triple, sample_table_data)
    assert len(result) == 2
    assert isinstance(result[0], GraphChunk)
    assert result[0].chunk_id.startswith("t1_")
    assert result[1].chunk_id.startswith("t1_")


@pytest.mark.asyncio
@patch("app.services.graph_service.get_llm_service")
@patch("app.services.graph_service.generate_schema")
async def test_process_table_and_generate_triples(
    mock_generate_schema,
    mock_get_llm_service,
    sample_table_data,
    mock_llm_service,
):
    mock_get_llm_service.return_value = mock_llm_service
    mock_generate_schema.return_value = {
        "schema": {
            "relationships": [
                {
                    "head": "Entity1",
                    "relation": "relates_to",
                    "tail": "Entity2",
                }
            ]
        }
    }

    result = await process_table_and_generate_triples(sample_table_data)
    assert isinstance(result, ExportTriplesResponseSchema)
    assert len(result.triples) == 1
    assert len(result.chunks) == 2


@pytest.mark.asyncio
@patch("app.services.graph_service.get_llm_service")
async def test_process_table_and_generate_triples_error(
    mock_get_llm_service, sample_table_data
):
    mock_get_llm_service.return_value = None
    result = await process_table_and_generate_triples(sample_table_data)
    assert isinstance(result, ExportTriplesResponseSchema)
    assert len(result.triples) == 0
    assert len(result.chunks) == 0
