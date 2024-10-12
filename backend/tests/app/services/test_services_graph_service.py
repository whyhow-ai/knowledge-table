from unittest.mock import AsyncMock, patch

import pytest
from whyhow import Node, Relation, Triple

from app.models.graph import ExportData
from app.models.llm import SchemaRelationship, SchemaResponseModel
from app.schemas.graph import Cell, Column, Document, Prompt, Row, Table
from app.services.graph_service import (
    create_triple_for_row,
    generate_chunks_for_triple,
    generate_chunks_for_triples,
    generate_triples,
    generate_triples_for_relationship,
    get_cell_value,
    get_label,
    parse_table,
    process_table_and_generate_triples,
)


@pytest.fixture
def mock_table_data():
    return Table(
        rows=[
            Row(
                id="1",
                document=Document(
                    id="doc1",
                    name="Document 1",
                    author="Author",
                    tag="Tag",
                    page_count=10,
                ),
                hidden=False,
            )
        ],
        columns=[
            Column(
                id="col1",
                prompt=Prompt(
                    entityType="Entity1",
                    id="prompt1",
                    query="Query1",
                    rules=[],
                    type="Type1",
                ),
                width=100,
                hidden=False,
            ),
            Column(
                id="col2",
                prompt=Prompt(
                    entityType="Entity2",
                    id="prompt2",
                    query="Query2",
                    rules=[],
                    type="Type2",
                ),
                width=100,
                hidden=False,
            ),
        ],
        cells=[
            Cell(
                rowId="1",
                columnId="col1",
                answer={
                    "answer": "Answer1",
                    "chunks": [{"content": "Chunk1", "page": 1}],
                },
                dirty=False,
            ),
            Cell(
                rowId="1",
                columnId="col2",
                answer={
                    "answer": "Answer2",
                    "chunks": [{"content": "Chunk2", "page": 1}],
                },
                dirty=False,
            ),
        ],
    )


@pytest.mark.asyncio
async def test_parse_table(mock_table_data):
    # When
    result = await parse_table(mock_table_data)

    # Then
    assert "table_data" in result
    assert len(result["table_data"]) == 1
    assert result["table_data"][0]["document_name"] == "Document 1"
    assert result["table_data"][0]["document_id"] == "doc1"
    assert len(result["table_data"][0]["answers"]) == 2
    assert result["table_data"][0]["answers"][0]["entity_type"] == "Entity1"
    assert result["table_data"][0]["answers"][0]["answer"] == "Answer1"


@pytest.mark.asyncio
async def test_generate_triples(mock_table_data):
    # Given
    schema = SchemaResponseModel(
        relationships=[
            SchemaRelationship(
                head="Entity1", relation="relates_to", tail="Entity2"
            )
        ]
    )

    # When
    result = await generate_triples(schema, mock_table_data)

    # Then
    assert "triples" in result
    assert "chunks" in result
    assert len(result["triples"]) == 1
    assert len(result["chunks"]) > 0


def test_generate_triples_for_relationship(mock_table_data):
    # Given
    relationship = SchemaRelationship(
        head="Entity1", relation="relates_to", tail="Entity2"
    )

    # When
    result = generate_triples_for_relationship(relationship, mock_table_data)

    # Then
    assert len(result) == 1
    assert isinstance(result[0], Triple)


def test_create_triple_for_row(mock_table_data):
    # Given
    relationship = SchemaRelationship(
        head="Entity1", relation="relates_to", tail="Entity2"
    )
    row = mock_table_data.rows[0]

    # When
    result = create_triple_for_row(relationship, row, mock_table_data)

    # Then
    assert isinstance(result, Triple)
    assert result.head.label == "Entity1"
    assert result.tail.label == "Entity2"
    assert result.relation.name == "relates_to"


def test_get_cell_value(mock_table_data):
    # Given
    entity_type = "Entity1"
    row = mock_table_data.rows[0]

    # When
    result = get_cell_value(entity_type, row, mock_table_data)

    # Then
    assert result == "Answer1"


def test_get_label():
    # Given
    entity_type = "Document"

    # When
    result = get_label(entity_type)

    # Then
    assert result == "Document"

    # Given
    entity_type = "OtherEntity"

    # When
    result = get_label(entity_type)

    # Then
    assert result == "OtherEntity"


def test_generate_chunks_for_triples(mock_table_data):
    # Given
    triples = [
        Triple(
            triple_id="t1",
            head=Node(label="Entity1", name="Answer1"),
            tail=Node(label="Entity2", name="Answer2"),
            relation=Relation(name="relates_to"),
            chunk_ids=[],
        )
    ]

    # When
    result = generate_chunks_for_triples(triples, mock_table_data)

    # Then
    assert len(result) == 2
    assert "chunk_id" in result[0]
    assert "content" in result[0]
    assert "page" in result[0]
    assert "triple_id" in result[0]


def test_generate_chunks_for_triple(mock_table_data):
    # Given
    triple = Triple(
        triple_id="t1",
        head=Node(label="Entity1", name="Answer1"),
        tail=Node(label="Entity2", name="Answer2"),
        relation=Relation(name="relates_to"),
        chunk_ids=[],
    )

    # When
    result = generate_chunks_for_triple(triple, mock_table_data)

    # Then
    assert len(result) == 2
    assert "chunk_id" in result[0]
    assert "content" in result[0]
    assert "page" in result[0]
    assert "triple_id" in result[0]


@pytest.mark.asyncio
async def test_process_table_and_generate_triples(mock_table_data):
    # Given
    mock_llm_service = AsyncMock()
    mock_llm_service.generate_schema.return_value = {
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

    with patch(
        "app.services.graph_service.get_llm_service",
        return_value=mock_llm_service,
    ):
        with patch(
            "app.services.graph_service.generate_schema",
            new_callable=AsyncMock,
        ) as mock_generate_schema:
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

            # When
            result = await process_table_and_generate_triples(mock_table_data)

    # Then
    assert isinstance(result, ExportData)
    assert len(result.triples) > 0
    assert len(result.chunks) > 0
