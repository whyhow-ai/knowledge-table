"""Tests for the query service"""

from typing import List, Literal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.query import Rule
from app.services.llm_service import LLMService
from app.services.query_service import (
    decomposition_query,
    get_vector_db_service,
    hybrid_query,
    process_query,
    simple_vector_query,
)


@pytest.fixture
def mock_llm_service():
    return AsyncMock(spec=LLMService)


@pytest.fixture
def mock_vector_db_service():
    return AsyncMock()


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.vector_db_provider = "mock_provider"
    return settings


@pytest.mark.asyncio
async def test_get_vector_db_service(mock_llm_service, mock_settings):
    # Given
    with (
        patch(
            "app.services.query_service.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.services.query_service.get_settings",
            return_value=mock_settings,
        ),
        patch(
            "app.services.query_service.VectorDBFactory.create_vector_db_service"
        ) as mock_create,
    ):
        mock_create.return_value = AsyncMock()

        # When
        result = await get_vector_db_service()

        # Then
        assert result is not None
        mock_create.assert_called_once_with(
            mock_settings.vector_db_provider, mock_llm_service
        )


@pytest.mark.asyncio
async def test_get_vector_db_service_failure(mock_llm_service, mock_settings):
    # Given
    with (
        patch(
            "app.services.query_service.get_llm_service",
            return_value=mock_llm_service,
        ),
        patch(
            "app.services.query_service.get_settings",
            return_value=mock_settings,
        ),
        patch(
            "app.services.query_service.VectorDBFactory.create_vector_db_service"
        ) as mock_create,
    ):
        mock_create.return_value = None

        # When/Then
        with pytest.raises(
            ValueError, match="Failed to create vector database service"
        ):
            await get_vector_db_service()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query_type", ["decomposition", "hybrid", "simple_vector"]
)
async def test_process_query(
    query_type: Literal["decomposition", "hybrid", "simple_vector"],
    mock_llm_service,
    mock_vector_db_service,
):
    # Given
    query = "test query"
    document_id = "doc123"
    rules: List[Rule] = []
    format: Literal["int", "str", "bool", "int_array", "str_array"] = "str"

    mock_chunks = [MagicMock(content="chunk1"), MagicMock(content="chunk2")]
    mock_search_response = (
        {"chunks": mock_chunks}
        if query_type == "decomposition"
        else MagicMock(chunks=mock_chunks)
    )

    with (
        patch(
            "app.services.query_service.get_vector_db_service",
            return_value=mock_vector_db_service,
        ),
        patch(
            "app.services.query_service.generate_response"
        ) as mock_generate_response,
    ):
        mock_vector_db_service.decomposed_search.return_value = (
            mock_search_response
        )
        mock_vector_db_service.hybrid_search.return_value = (
            mock_search_response
        )
        mock_vector_db_service.vector_search.return_value = (
            mock_search_response
        )
        mock_generate_response.return_value = {"answer": "test answer"}

        # When
        result = await process_query(
            query_type, query, document_id, rules, format, mock_llm_service
        )

        # Then
        assert result == {"answer": "test answer", "chunks": mock_chunks[:10]}
        if query_type == "decomposition":
            mock_vector_db_service.decomposed_search.assert_called_once_with(
                query, document_id, rules
            )
        elif query_type == "hybrid":
            mock_vector_db_service.hybrid_search.assert_called_once_with(
                query, document_id, rules
            )
        else:
            mock_vector_db_service.vector_search.assert_called_once_with(
                [query], document_id
            )
        mock_generate_response.assert_called_once_with(
            mock_llm_service, query, "chunk1 chunk2", rules, format
        )


@pytest.mark.asyncio
async def test_decomposition_query(mock_llm_service):
    # Given
    with patch(
        "app.services.query_service.process_query"
    ) as mock_process_query:
        mock_process_query.return_value = {
            "answer": "test answer",
            "chunks": [],
        }
        query = "test query"
        document_id = "doc123"
        rules: List[Rule] = []
        format: Literal["int", "str", "bool", "int_array", "str_array"] = "str"

        # When
        result = await decomposition_query(
            query, document_id, rules, format, mock_llm_service
        )

        # Then
        assert result == {"answer": "test answer", "chunks": []}
        mock_process_query.assert_called_once_with(
            "decomposition",
            query,
            document_id,
            rules,
            format,
            mock_llm_service,
        )


@pytest.mark.asyncio
async def test_hybrid_query(mock_llm_service):
    # Given
    with patch(
        "app.services.query_service.process_query"
    ) as mock_process_query:
        mock_process_query.return_value = {
            "answer": "test answer",
            "chunks": [],
        }
        query = "test query"
        document_id = "doc123"
        rules: List[Rule] = []
        format: Literal["int", "str", "bool", "int_array", "str_array"] = "str"

        # When
        result = await hybrid_query(
            query, document_id, rules, format, mock_llm_service
        )

        # Then
        assert result == {"answer": "test answer", "chunks": []}
        mock_process_query.assert_called_once_with(
            "hybrid", query, document_id, rules, format, mock_llm_service
        )


@pytest.mark.asyncio
async def test_simple_vector_query(mock_llm_service):
    # Given
    with patch(
        "app.services.query_service.process_query"
    ) as mock_process_query:
        mock_process_query.return_value = {
            "answer": "test answer",
            "chunks": [],
        }
        query = "test query"
        document_id = "doc123"
        rules: List[Rule] = []
        format: Literal["int", "str", "bool", "int_array", "str_array"] = "str"

        # When
        result = await simple_vector_query(
            query, document_id, rules, format, mock_llm_service
        )

        # Then
        assert result == {"answer": "test answer", "chunks": []}
        mock_process_query.assert_called_once_with(
            "simple_vector",
            query,
            document_id,
            rules,
            format,
            mock_llm_service,
        )
