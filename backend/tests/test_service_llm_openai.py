from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from app.services.llm.openai_service import OpenAIService


@pytest.fixture
def openai_service(test_settings):
    with (
        patch("app.services.llm.openai_service.OpenAI"),
        patch("app.services.llm.openai_service.OpenAIEmbeddings"),
    ):
        service = OpenAIService(test_settings)
        yield service


@pytest.mark.asyncio
async def test_generate_completion(openai_service):
    class DummyResponseModel(BaseModel):
        content: str

    mock_response = MagicMock()
    mock_parsed = MagicMock()
    mock_parsed.model_dump.return_value = {"content": "Test response"}
    mock_response.choices[0].message.parsed = mock_parsed
    openai_service.client.beta.chat.completions.parse.return_value = (
        mock_response
    )

    result = await openai_service.generate_completion(
        "Test prompt", DummyResponseModel
    )

    assert isinstance(result, DummyResponseModel)
    assert result.content == "Test response"
    openai_service.client.beta.chat.completions.parse.assert_called_once()
    mock_parsed.model_dump.assert_called_once()


@pytest.mark.asyncio
async def test_generate_completion_none_response(openai_service):
    class DummyResponseModel(BaseModel):
        content: str

    mock_response = MagicMock()
    mock_response.choices[0].message.parsed = None
    openai_service.client.beta.chat.completions.parse.return_value = (
        mock_response
    )

    result = await openai_service.generate_completion(
        "Test prompt", DummyResponseModel
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_embeddings(openai_service):
    test_texts = ["Test text 1", "Test text 2"]
    expected_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    openai_service.embeddings.embed_documents = MagicMock(
        return_value=expected_embeddings
    )

    result = await openai_service.get_embeddings(test_texts)

    assert result == expected_embeddings
    openai_service.embeddings.embed_documents.assert_called_once_with(
        test_texts
    )


@pytest.mark.asyncio
async def test_decompose_query(openai_service):
    test_query = "Test query"
    result = await openai_service.decompose_query(test_query)

    assert result == {"sub_queries": [test_query]}
