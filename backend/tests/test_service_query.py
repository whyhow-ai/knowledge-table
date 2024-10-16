from unittest.mock import AsyncMock, patch

import pytest

from app.models.graph import GraphChunk
from app.models.query import Chunk
from app.schemas.query import VectorResponse
from app.services.query_service import (
    decomposition_query,
    execute_query,
    hybrid_query,
    process_query,
    simple_vector_query,
)


@pytest.fixture
def mock_vector_db_service():
    return AsyncMock()


@pytest.fixture
def mock_llm_service():
    return AsyncMock()


@pytest.fixture
def mock_generate_response():
    return AsyncMock(return_value={"answer": "Test answer"})


@pytest.mark.asyncio
@patch("app.services.query_service.get_vector_db_service")
@patch("app.services.query_service.generate_response")
async def test_process_query_decomposition(
    mock_generate_response,
    mock_get_vector_db_service,
    mock_vector_db_service,
    mock_llm_service,
):
    mock_get_vector_db_service.return_value = mock_vector_db_service
    mock_vector_db_service.decomposed_search.return_value = {
        "chunks": [
            GraphChunk(
                chunk_id="1", content="Test content", page=1, triple_id="t1"
            )
        ]
    }
    mock_generate_response.return_value = {"answer": "Test answer"}

    result = await process_query(
        "decomposition", "test query", "doc_id", [], "str", mock_llm_service
    )

    assert result == {
        "answer": "Test answer",
        "chunks": [
            GraphChunk(
                chunk_id="1", content="Test content", page=1, triple_id="t1"
            )
        ],
    }
    mock_vector_db_service.decomposed_search.assert_called_once_with(
        "test query", "doc_id", []
    )
    mock_generate_response.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.query_service.get_vector_db_service")
@patch("app.services.query_service.generate_response")
async def test_process_query_hybrid(
    mock_generate_response,
    mock_get_vector_db_service,
    mock_vector_db_service,
    mock_llm_service,
):
    mock_get_vector_db_service.return_value = mock_vector_db_service
    mock_vector_db_service.hybrid_search.return_value = {
        "chunks": [
            GraphChunk(
                chunk_id="1", content="Test content", page=1, triple_id="t1"
            )
        ]
    }
    mock_generate_response.return_value = {"answer": "Test answer"}

    result = await process_query(
        "hybrid", "test query", "doc_id", [], "str", mock_llm_service
    )

    assert result == {
        "answer": "Test answer",
        "chunks": [
            GraphChunk(
                chunk_id="1", content="Test content", page=1, triple_id="t1"
            )
        ],
    }
    mock_vector_db_service.hybrid_search.assert_called_once_with(
        "test query", "doc_id", []
    )
    mock_generate_response.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.query_service.get_vector_db_service")
@patch("app.services.query_service.generate_response")
async def test_process_query_simple_vector(
    mock_generate_response,
    mock_get_vector_db_service,
    mock_vector_db_service,
    mock_llm_service,
):
    mock_get_vector_db_service.return_value = mock_vector_db_service
    mock_vector_db_service.vector_search.return_value = VectorResponse(
        message="Test message",
        chunks=[Chunk(content="Test content", page=1)],
        keywords=["test", "keyword"],
    )
    mock_generate_response.return_value = {"answer": "Test answer"}

    result = await process_query(
        "simple_vector", "test query", "doc_id", [], "str", mock_llm_service
    )

    assert result == {
        "answer": "Test answer",
        "chunks": [Chunk(content="Test content", page=1)],
    }
    # Change this line to expect a list containing the query string
    mock_vector_db_service.vector_search.assert_called_once_with(
        ["test query"], "doc_id"
    )
    mock_generate_response.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.query_service.process_query")
async def test_execute_query(mock_process_query, mock_llm_service):
    mock_process_query.return_value = {"answer": "Test answer", "chunks": []}

    result = await execute_query(
        "hybrid", "test query", "doc_id", [], "str", mock_llm_service
    )

    assert result == {"answer": "Test answer", "chunks": []}
    mock_process_query.assert_called_once_with(
        "hybrid", "test query", "doc_id", [], "str", mock_llm_service
    )


@pytest.mark.asyncio
@patch("app.services.query_service.execute_query")
async def test_decomposition_query(mock_execute_query, mock_llm_service):
    mock_execute_query.return_value = {"answer": "Test answer", "chunks": []}

    result = await decomposition_query(
        "test query", "doc_id", [], "str", mock_llm_service
    )

    assert result == {"answer": "Test answer", "chunks": []}
    mock_execute_query.assert_called_once_with(
        "decomposition", "test query", "doc_id", [], "str", mock_llm_service
    )


@pytest.mark.asyncio
@patch("app.services.query_service.execute_query")
async def test_hybrid_query(mock_execute_query, mock_llm_service):
    mock_execute_query.return_value = {"answer": "Test answer", "chunks": []}

    result = await hybrid_query(
        "test query", "doc_id", [], "str", mock_llm_service
    )

    assert result == {"answer": "Test answer", "chunks": []}
    mock_execute_query.assert_called_once_with(
        "hybrid", "test query", "doc_id", [], "str", mock_llm_service
    )


@pytest.mark.asyncio
@patch("app.services.query_service.execute_query")
async def test_simple_vector_query(mock_execute_query, mock_llm_service):
    mock_execute_query.return_value = {"answer": "Test answer", "chunks": []}

    result = await simple_vector_query(
        "test query", "doc_id", [], "str", mock_llm_service
    )

    assert result == {"answer": "Test answer", "chunks": []}
    mock_execute_query.assert_called_once_with(
        "simple_vector", "test query", "doc_id", [], "str", mock_llm_service
    )
