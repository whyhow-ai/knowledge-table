from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from app.services.llm.openai_llm_service import OpenAICompletionService


@pytest.fixture
def openai_service(test_settings):
    service = OpenAICompletionService(test_settings)
    service.client = MagicMock()  # Mock the entire client
    service.client.beta = MagicMock()  # Add the beta attribute
    service.client.beta.chat = MagicMock()
    service.client.beta.chat.completions = MagicMock()
    return service


@pytest.mark.asyncio
async def test_generate_completion(openai_service):
    class DummyResponseModel(BaseModel):
        content: str

    mock_response = MagicMock()
    mock_parsed = MagicMock()
    mock_parsed.model_dump.return_value = {"content": "Test response"}
    mock_response.choices[0].message.parsed = mock_parsed

    # Create an async mock for the parse method
    async def mock_parse(*args, **kwargs):
        return mock_response

    openai_service.client.beta.chat.completions.parse = mock_parse


@pytest.mark.asyncio
async def test_generate_completion_none_response(openai_service):
    class DummyResponseModel(BaseModel):
        content: str

    mock_response = MagicMock()
    mock_response.choices[0].message.parsed = None

    # Create an async mock for the parse method
    async def mock_parse(*args, **kwargs):
        return mock_response

    openai_service.client.beta.chat.completions.parse = mock_parse


@pytest.mark.asyncio
async def test_get_embeddings(openai_service):
    test_texts = ["Test text 1", "Test text 2"]
    expected_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    # Create an AsyncMock for the get_embeddings method
    async_mock = AsyncMock(return_value=expected_embeddings)
    openai_service.get_embeddings = async_mock

    result = await openai_service.get_embeddings(test_texts)

    assert result == expected_embeddings
    async_mock.assert_called_once_with(test_texts)


@pytest.mark.asyncio
async def test_decompose_query(openai_service):
    test_query = "Test query"
    result = await openai_service.decompose_query(test_query)

    assert result == {"sub_queries": [test_query]}
