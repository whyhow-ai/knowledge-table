# tests/test_endpoint_graph.py
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.models.document import Document
from app.models.graph import GraphChunk, Node, Relation, Triple
from app.models.table import Cell, Column, Prompt, Row
from app.schemas.graph_api import ExportTriplesResponseSchema
from app.services.llm.openai_service import OpenAIService


@pytest.fixture
def mock_openai_client():
    mock_client = MagicMock()
    # Set up mock behaviors if necessary
    return mock_client


@pytest.fixture
def mock_llm_service(mock_openai_client):
    mock_settings = Settings(openai_api_key=None)  # API key is None
    llm_service = OpenAIService(mock_settings, client=mock_openai_client)
    return llm_service


@pytest.fixture
def mock_generate_schema():
    return AsyncMock()


@pytest.fixture
def mock_generate_triples():
    return AsyncMock()


@pytest.fixture
def client():
    with patch("app.core.dependencies.get_settings") as mock_get_settings:
        mock_get_settings.return_value = Settings(openai_api_key=None)
        from app.main import app

        with TestClient(app) as test_client:
            yield test_client


def create_test_prompt():
    return Prompt(
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
                id="Name",
                name="Name",
                prompt=create_test_prompt(),
                hidden=False,
            ).model_dump(),
            Column(
                id="Age",
                name="Age",
                prompt=create_test_prompt(),
                hidden=False,
            ).model_dump(),
        ],
        "rows": [
            Row(
                id="1",
                document=create_test_document(),
                hidden=False,
            ).model_dump(),
            Row(
                id="2",
                document=create_test_document(),
                hidden=False,
            ).model_dump(),
        ],
        "cells": [
            Cell(
                columnId="Name",
                rowId="1",
                answer={"value": "Alice"},
                dirty=False,
            ).model_dump(),
            Cell(
                columnId="Age", rowId="1", answer={"value": "30"}, dirty=False
            ).model_dump(),
            Cell(
                columnId="Name",
                rowId="2",
                answer={"value": "Bob"},
                dirty=False,
            ).model_dump(),
            Cell(
                columnId="Age", rowId="2", answer={"value": "25"}, dirty=False
            ).model_dump(),
        ],
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
        patch("openai.OpenAI", return_value=mock_llm_service.client),
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
                id="Name",
                name="Name",
                prompt=create_test_prompt(),
                hidden=False,
            ).model_dump(),
            Column(
                id="Age",
                name="Age",
                prompt=create_test_prompt(),
                hidden=False,
            ).model_dump(),
        ],
        "rows": [
            Row(
                id="1",
                document=create_test_document(),
                hidden=False,
            ).model_dump(),
            Row(
                id="2",
                document=create_test_document(),
                hidden=False,
            ).model_dump(),
        ],
        "cells": [
            Cell(
                columnId="Name",
                rowId="1",
                answer={"value": "Alice"},
                dirty=False,
            ).model_dump(),
            Cell(
                columnId="Age", rowId="1", answer={"value": "30"}, dirty=False
            ).model_dump(),
            Cell(
                columnId="Name",
                rowId="2",
                answer={"value": "Bob"},
                dirty=False,
            ).model_dump(),
            Cell(
                columnId="Age", rowId="2", answer={"value": "25"}, dirty=False
            ).model_dump(),
        ],
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
        patch("openai.OpenAI", return_value=mock_llm_service.client),
    ):
        response = client.post(
            "/api/v1/graph/export-triples", json=request_data
        )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Unexpected error" in response.json()["detail"]
