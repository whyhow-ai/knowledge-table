from unittest.mock import AsyncMock, patch

import pytest

from app.models.query import Rule
from app.schemas.query import QueryPrompt, QueryRequest
from app.services.llm.base import LLMService
from app.services.vector_db.base import VectorDBService


@pytest.fixture
def valid_query_request():
    return QueryRequest(
        rag_type="vector",
        document_id="doc123",
        prompt=QueryPrompt(
            id="prompt123",
            query="What is the capital of France?",
            type="str",
            entity_type="country",
            rules=[Rule(type="must_return", options=["Paris"])],
        ),
    )


@pytest.fixture
def mock_llm_service():
    return AsyncMock(spec=LLMService)


@pytest.fixture
def mock_vector_db_service():
    mock = AsyncMock(spec=VectorDBService)
    mock.search.return_value = [
        {
            "id": "1",
            "content": "Paris is the capital of France.",
            "page": 1,
            "triple_id": "t1",
        }
    ]
    return mock


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="TODO: Implement when search index is available for testing"
)
@patch("app.api.v1.endpoints.query.get_vectordb_service")
@patch("app.api.v1.endpoints.query.simple_vector_query")
async def test_run_query_vector_success(
    mock_vector_query, mock_get_vectordb, mock_llm_service, valid_query_request
):
    # TODO: Implement this test when search index is available
    pass


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="TODO: Implement when search index is available for testing"
)
@patch("app.api.v1.endpoints.query.get_vectordb_service")
@patch("app.api.v1.endpoints.query.decomposition_query")
async def test_run_query_decomposed(
    mock_decomp_query, mock_get_vectordb, mock_llm_service, valid_query_request
):
    # TODO: Implement this test when search index is available
    pass
