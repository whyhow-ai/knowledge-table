from unittest.mock import patch

import pytest

from app.models.query_core import Chunk
from app.schemas.query_api import QueryResult, VectorResponseSchema
from app.services.query_service import (
    decomposition_query,
    hybrid_query,
    process_query,
    simple_vector_query,
)


@pytest.mark.asyncio
async def test_process_query_decomposition(
    mock_vector_db_service, mock_llm_service
):
    with patch(
        "app.services.query_service.generate_response"
    ) as mock_generate_response:
        mock_vector_db_service.decomposed_search.return_value = {
            "chunks": [Chunk(content="Test content", page=1)]
        }
        mock_generate_response.return_value = {"answer": "Test answer"}

        result = await process_query(
            "decomposition",
            "test query",
            "doc_id",
            [],
            "str",
            mock_llm_service,
            mock_vector_db_service,
        )

        assert result == QueryResult(
            answer="Test answer",
            chunks=[Chunk(content="Test content", page=1)],
        )
        mock_vector_db_service.decomposed_search.assert_called_once_with(
            "test query", "doc_id", []
        )
        mock_generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_hybrid(mock_vector_db_service, mock_llm_service):
    with patch(
        "app.services.query_service.generate_response"
    ) as mock_generate_response:
        mock_vector_db_service.hybrid_search.return_value = {
            "chunks": [Chunk(content="Test content", page=1)]
        }
        mock_generate_response.return_value = {"answer": "Test answer"}

        result = await process_query(
            "hybrid",
            "test query",
            "doc_id",
            [],
            "str",
            mock_llm_service,
            mock_vector_db_service,
        )

        assert result == QueryResult(
            answer="Test answer",
            chunks=[Chunk(content="Test content", page=1)],
        )
        mock_vector_db_service.hybrid_search.assert_called_once_with(
            "test query", "doc_id", []
        )
        mock_generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_simple_vector(
    mock_vector_db_service, mock_llm_service
):
    # Reset the mock before the test
    mock_vector_db_service.vector_search.reset_mock()

    with patch(
        "app.services.query_service.generate_response"
    ) as mock_generate_response:
        mock_vector_db_service.vector_search.return_value = (
            VectorResponseSchema(
                message="Test message",
                chunks=[Chunk(content="Test content", page=1)],
                keywords=["test", "keyword"],
            )
        )
        mock_generate_response.return_value = {"answer": "Test answer"}

        result = await process_query(
            "simple_vector",
            "test query",
            "doc_id",
            [],
            "str",
            mock_llm_service,
            mock_vector_db_service,
        )

        assert result == QueryResult(
            answer="Test answer",
            chunks=[Chunk(content="Test content", page=1)],
        )

        # Reset the mock and then check the call
        mock_vector_db_service.vector_search.assert_called_once_with(
            ["test query"], "doc_id"
        )


@pytest.mark.asyncio
async def test_decomposition_query(mock_llm_service, mock_vector_db_service):
    with patch(
        "app.services.query_service.process_query"
    ) as mock_process_query:
        mock_process_query.return_value = QueryResult(
            answer="Test answer", chunks=[]
        )

        result = await decomposition_query(
            "test query",
            "doc_id",
            [],
            "str",
            mock_llm_service,
            mock_vector_db_service,
        )

        assert result == QueryResult(answer="Test answer", chunks=[])
        mock_process_query.assert_called_once_with(
            "decomposition",
            "test query",
            "doc_id",
            [],
            "str",
            mock_llm_service,
            mock_vector_db_service,
        )


@pytest.mark.asyncio
async def test_hybrid_query(mock_llm_service, mock_vector_db_service):
    with patch(
        "app.services.query_service.process_query"
    ) as mock_process_query:
        mock_process_query.return_value = QueryResult(
            answer="Test answer", chunks=[]
        )

        result = await hybrid_query(
            "test query",
            "doc_id",
            [],
            "str",
            mock_llm_service,
            mock_vector_db_service,
        )

        assert result == QueryResult(answer="Test answer", chunks=[])
        mock_process_query.assert_called_once_with(
            "hybrid",
            "test query",
            "doc_id",
            [],
            "str",
            mock_llm_service,
            mock_vector_db_service,
        )


@pytest.mark.asyncio
async def test_simple_vector_query(mock_llm_service, mock_vector_db_service):
    with patch(
        "app.services.query_service.process_query"
    ) as mock_process_query:
        mock_process_query.return_value = QueryResult(
            answer="Test answer", chunks=[]
        )

        result = await simple_vector_query(
            "test query",
            "doc_id",
            [],
            "str",
            mock_llm_service,
            mock_vector_db_service,
        )

        assert result == QueryResult(answer="Test answer", chunks=[])
        mock_process_query.assert_called_once_with(
            "simple_vector",
            "test query",
            "doc_id",
            [],
            "str",
            mock_llm_service,
            mock_vector_db_service,
        )
