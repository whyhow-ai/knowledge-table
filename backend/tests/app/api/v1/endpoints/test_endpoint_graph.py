import logging
from unittest.mock import Mock, patch

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture(autouse=True)
def setup_logging(caplog):
    caplog.set_level(logging.INFO)
    logging.getLogger("app.api.v1.endpoints.graph").setLevel(logging.INFO)


@pytest.fixture
def valid_request_data():
    return {
        "cells": [
            {
                "answer": {"text": "test answer"},
                "columnId": "col1",
                "dirty": False,
                "rowId": "row1",
            }
        ],
        "columns": [
            {
                "id": "col1",
                "prompt": {
                    "entityType": "TestEntity",
                    "id": "prompt1",
                    "query": "Generate a summary",
                    "rules": ["rule1", "rule2"],
                    "type": "summary",
                },
                "width": 100,
                "hidden": False,
            }
        ],
        "rows": [
            {
                "id": "row1",
                "document": {
                    "id": "doc1",
                    "name": "Test Document",
                    "author": "Test Author",
                    "tag": "Test Tag",
                    "page_count": 10,
                },
                "hidden": False,
            }
        ],
    }


@pytest.fixture
def valid_response_data():
    return {
        "triples": [
            {
                "triple_id": "t1",
                "head": {"label": "Treatment", "name": "natalizumab"},
                "tail": {"label": "Disease", "name": "multiple sclerosis"},
                "relation": {"name": "treats"},
                "chunk_ids": ["chunk1", "chunk2"],
            }
        ],
        "chunks": [
            {
                "chunk_id": "chunk1",
                "content": "Sample content 1",
                "page": "1",
                "triple_id": "t1",
            },
            {
                "chunk_id": "chunk2",
                "content": "Sample content 2",
                "page": "2",
                "triple_id": "t1",
            },
        ],
    }


@pytest.mark.asyncio
@patch("app.api.v1.endpoints.graph.get_llm_service")
@patch("app.api.v1.endpoints.graph.generate_schema")
@patch("app.api.v1.endpoints.graph.generate_triples")
async def test_export_triples_success(
    mock_generate_triples,
    mock_generate_schema,
    mock_get_llm_service,
    valid_request_data,
    valid_response_data,
):
    # Given
    mock_get_llm_service.return_value = Mock()
    mock_generate_schema.return_value = {"schema": {"test": "schema"}}
    mock_generate_triples.return_value = valid_response_data

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/graph/export-triples", json=valid_request_data
        )

    # Then
    assert response.status_code == 200
    response_data = response.json()
    assert "triples" in response_data
    assert "chunks" in response_data
    assert len(response_data["triples"]) == 1
    assert len(response_data["chunks"]) == 2


@pytest.mark.asyncio
async def test_export_triples_validation_error(valid_request_data):
    # Given
    invalid_data = valid_request_data.copy()
    invalid_data["columns"][0]["prompt"].pop(
        "entityType"
    )  # Remove a required field

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/graph/export-triples", json=invalid_data
        )

    # Then
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    print("Error detail:", error_detail)  # Debug print

    # Check if the error matches our expectations
    assert len(error_detail) == 1, "Expected exactly one error"
    error = error_detail[0]

    assert error["type"] == "missing"
    assert error["loc"] == ["columns", 0, "prompt", "entityType"]
    assert error["msg"] == "Field required"
    assert "input" in error
    assert "url" in error

    print("Test passed successfully!")


@pytest.mark.asyncio
@patch("app.api.v1.endpoints.graph.get_llm_service")
@patch("app.api.v1.endpoints.graph.generate_schema")
@patch("app.api.v1.endpoints.graph.generate_triples")
async def test_export_triples_logging(
    mock_generate_triples,
    mock_generate_schema,
    mock_get_llm_service,
    valid_request_data,
    valid_response_data,
    caplog,
):
    # Given
    mock_get_llm_service.return_value = Mock()
    mock_generate_schema.return_value = {"schema": {"test": "schema"}}
    mock_generate_triples.return_value = valid_response_data

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/api/v1/graph/export-triples", json=valid_request_data)

    # Then
    log_messages = [record.getMessage() for record in caplog.records]
    assert any("Generated schema:" in message for message in log_messages)
    assert any(
        "Generated 1 triples and 2 chunks" in message
        for message in log_messages
    )
    assert any(
        "Sending response with triples and chunks" in message
        for message in log_messages
    )
