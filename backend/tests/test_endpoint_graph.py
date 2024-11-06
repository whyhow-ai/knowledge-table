# test_endpoint_graph.py
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status

from app.models.document import Document
from app.models.graph import GraphChunk, Node, Relation, Triple
from app.models.table import Column, Row, TablePrompt
from app.schemas.graph_api import ExportTriplesResponseSchema


@pytest.fixture
def mock_generate_schema():
    return AsyncMock()


@pytest.fixture
def mock_generate_triples():
    return AsyncMock()


def create_test_prompt():
    return TablePrompt(
        entityType="test",
        id="test_prompt",
        query="Test query",
        rules=[],
        type="test_type",
    )


def create_test_document():
    return Document(
        id="doc1",
        name="Doc 1",
        author="Author",
        tag="Tag",
        page_count=10,
    )


def test_export_triples_success(
    client, mock_llm_service, mock_generate_schema, mock_generate_triples
):
    request_data = {
        "columns": [
            Column(
                id="1",
                width=160,
                hidden=False,
                entityType="Disease",
                type="str",
                generate=True,
                query="Which diseases are mentioned in this article?",
                rules=[],
            ).model_dump(),
            Column(
                id="2",
                width=160,
                hidden=False,
                entityType="Protein",
                type="str",
                generate=True,
                query="Which treatments are mentioned in this article?",
                rules=[],
            ).model_dump(),
        ],
        "rows": [
            Row(
                id="3",
                sourceData={
                    "type": "document",
                    "document": create_test_document(),
                },
                hidden=False,
                cells={"1": "COVID-19", "2": "Vaccine"},
            ).model_dump()
        ],
        "chunks": {
            "3-1": [
                {
                    "page": 1,
                    "content": "COVID-19 is a disease.",
                },
                {
                    "page": 2,
                    "content": "Vaccine is a treatment.",
                },
                {
                    "page": 3,
                    "content": "Flu is a disease.",
                },
            ],
            "3-2": [
                {
                    "page": 1,
                    "content": "COVID-19 is a disease.",
                },
                {
                    "page": 2,
                    "content": "Vaccine is a treatment.",
                },
                {
                    "page": 3,
                    "content": "Flu is a disease.",
                },
            ],
        },
    }

    mock_generate_schema.return_value = {"schema": {"properties": {}}}

    mock_generate_triples.return_value = ExportTriplesResponseSchema(
        triples=[
            Triple(
                triple_id="1",
                head=Node(label="Person", name="Alice"),
                tail=Node(label="Age", name="30"),
                relation=Relation(name="hasAge"),
                chunk_ids=["1"],
            ),
            Triple(
                triple_id="2",
                head=Node(label="Person", name="Bob"),
                tail=Node(label="Age", name="25"),
                relation=Relation(name="hasAge"),
                chunk_ids=["2"],
            ),
        ],
        chunks=[
            GraphChunk(
                chunk_id="1",
                content="Alice is 30 years old.",
                page=1,
                triple_id="1",
            ),
            GraphChunk(
                chunk_id="2",
                content="Bob is 25 years old.",
                page=1,
                triple_id="2",
            ),
        ],
    )

    # Remove the patch for openai.OpenAI since it's mocked globally
    with (
        patch(
            "app.api.v1.endpoints.graph.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.api.v1.endpoints.graph.generate_schema", mock_generate_schema
        ),
        patch(
            "app.api.v1.endpoints.graph.generate_triples",
            mock_generate_triples,
        ),
    ):
        response = client.post(
            "/api/v1/graph/export-triples", json=request_data
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/json"

    response_data = json.loads(response.content)
    assert "triples" in response_data
    assert "chunks" in response_data
    assert len(response_data["triples"]) == 2
    assert len(response_data["chunks"]) == 2


def test_export_triples_validation_error(client):
    invalid_data = {
        "columns": ["Name", "Age"],
        # Missing "rows" and "cells"
    }

    with patch("openai.OpenAI", return_value=MagicMock()):
        response = client.post(
            "/api/v1/graph/export-triples", json=invalid_data
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()


def test_export_triples_json_decode_error(client):
    with patch("openai.OpenAI", return_value=MagicMock()):
        response = client.post(
            "/api/v1/graph/export-triples", content="invalid json"
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_detail = response.json()["detail"][0]
    assert error_detail["type"] == "json_invalid"
    assert "JSON decode error" in error_detail["msg"]


def test_export_triples_unexpected_error(
    client, mock_llm_service, mock_generate_schema
):
    request_data = {
        "columns": [
            Column(
                id="1",
                width=160,
                hidden=False,
                entityType="Disease",
                type="str",
                generate=True,
                query="Which diseases are mentioned in this article?",
                rules=[],
            ).model_dump(),
            Column(
                id="2",
                width=160,
                hidden=False,
                entityType="Protein",
                type="str",
                generate=True,
                query="Which treatments are mentioned in this article?",
                rules=[],
            ).model_dump(),
        ],
        "rows": [
            Row(
                id="3",
                sourceData={
                    "type": "document",
                    "document": create_test_document(),
                },
                hidden=False,
                cells={"1": "COVID-19", "2": "Vaccine"},
            ).model_dump()
        ],
        "chunks": {
            "3-1": [
                {
                    "page": 1,
                    "content": "COVID-19 is a disease.",
                },
                {
                    "page": 2,
                    "content": "Vaccine is a treatment.",
                },
                {
                    "page": 3,
                    "content": "Flu is a disease.",
                },
            ],
            "3-2": [
                {
                    "page": 1,
                    "content": "COVID-19 is a disease.",
                },
                {
                    "page": 2,
                    "content": "Vaccine is a treatment.",
                },
                {
                    "page": 3,
                    "content": "Flu is a disease.",
                },
            ],
        },
    }

    mock_generate_schema.side_effect = Exception("Unexpected error")

    with (
        patch(
            "app.api.v1.endpoints.graph.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.api.v1.endpoints.graph.generate_schema", mock_generate_schema
        ),
    ):
        response = client.post(
            "/api/v1/graph/export-triples", json=request_data
        )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Unexpected error" in response.json()["detail"]
