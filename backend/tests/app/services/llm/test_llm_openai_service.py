from unittest.mock import Mock, patch

import pytest

from app.core.config import settings
from app.models.llm import (
    BoolResponseModel,
    IntArrayResponseModel,
    IntResponseModel,
    KeywordsResponseModel,
    SchemaResponseModel,
    StrArrayResponseModel,
    StrResponseModel,
    SubQueriesResponseModel,
)
from app.services.llm.openai_service import OpenAIService


@pytest.fixture
def openai_service():
    with (
        patch("app.services.llm.openai_service.OpenAI") as mock_openai,
        patch(
            "app.services.llm.openai_service.OpenAIEmbeddings"
        ) as mock_embeddings,
    ):
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_embeddings.return_value = Mock()
        service = OpenAIService()
        service.client = mock_client
        service.embeddings = mock_embeddings.return_value
        yield service


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response_model, mock_response, expected_result",
    [
        (
            BoolResponseModel,
            BoolResponseModel(answer=True),
            BoolResponseModel(answer=True),
        ),
        (
            BoolResponseModel,
            BoolResponseModel(answer=None),
            BoolResponseModel(answer=None),
        ),
        (
            IntResponseModel,
            IntResponseModel(answer=42),
            IntResponseModel(answer=42),
        ),
        (
            IntResponseModel,
            IntResponseModel(answer=None),
            IntResponseModel(answer=None),
        ),
        (
            StrResponseModel,
            StrResponseModel(answer="test"),
            StrResponseModel(answer="test"),
        ),
        (
            StrResponseModel,
            StrResponseModel(answer=None),
            StrResponseModel(answer=None),
        ),
        (
            IntArrayResponseModel,
            IntArrayResponseModel(answer=[1, 2, 3]),
            IntArrayResponseModel(answer=[1, 2, 3]),
        ),
        (
            IntArrayResponseModel,
            IntArrayResponseModel(answer=None),
            IntArrayResponseModel(answer=None),
        ),
        (
            StrArrayResponseModel,
            StrArrayResponseModel(answer=["a", "b", "c"]),
            StrArrayResponseModel(answer=["a", "b", "c"]),
        ),
        (
            StrArrayResponseModel,
            StrArrayResponseModel(answer=None),
            StrArrayResponseModel(answer=None),
        ),
        (
            KeywordsResponseModel,
            KeywordsResponseModel(keywords=["key1", "key2"]),
            KeywordsResponseModel(keywords=["key1", "key2"]),
        ),
        (
            KeywordsResponseModel,
            KeywordsResponseModel(keywords=None),
            KeywordsResponseModel(keywords=None),
        ),
        (
            SubQueriesResponseModel,
            SubQueriesResponseModel(sub_queries=["q1", "q2"]),
            SubQueriesResponseModel(sub_queries=["q1", "q2"]),
        ),
        (
            SubQueriesResponseModel,
            SubQueriesResponseModel(sub_queries=None),
            SubQueriesResponseModel(sub_queries=None),
        ),
        (
            SchemaResponseModel,
            SchemaResponseModel(
                relationships=[{"head": "a", "relation": "b", "tail": "c"}]
            ),
            SchemaResponseModel(
                relationships=[{"head": "a", "relation": "b", "tail": "c"}]
            ),
        ),
        (
            SchemaResponseModel,
            SchemaResponseModel(relationships=None),
            SchemaResponseModel(relationships=None),
        ),
    ],
)
async def test_generate_completion(
    openai_service, response_model, mock_response, expected_result
):
    # Given
    prompt = "Test prompt"

    # Create a mock response that mimics the structure of the beta client response
    mock_message = Mock()
    mock_message.parsed = mock_response
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response_obj = Mock()
    mock_response_obj.choices = [mock_choice]

    openai_service.client.beta.chat.completions.parse.return_value = (
        mock_response_obj
    )

    # When
    result = await openai_service.generate_completion(prompt, response_model)

    # Then
    assert result == expected_result
    assert isinstance(result, response_model)
    openai_service.client.beta.chat.completions.parse.assert_called_once_with(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        response_format=response_model,
    )


@pytest.mark.asyncio
async def test_generate_completion_none_string(openai_service):
    # Given
    prompt = "Test prompt"
    response_model = StrResponseModel

    mock_message = Mock()
    mock_message.parsed = StrResponseModel(answer=None)
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response = Mock()
    mock_response.choices = [mock_choice]

    openai_service.client.beta.chat.completions.parse.return_value = (
        mock_response
    )

    # When
    result = await openai_service.generate_completion(prompt, response_model)

    # Then
    assert isinstance(result, StrResponseModel)
    assert result.answer is None


@pytest.mark.asyncio
async def test_get_embeddings(openai_service):
    """Test the get_embeddings method."""
    # Given
    text = "Test text"
    expected_embeddings = [0.1, 0.2, 0.3]
    openai_service.embeddings.embed_query.return_value = expected_embeddings

    # When
    result = await openai_service.get_embeddings(text)

    # Then
    assert result == expected_embeddings
    openai_service.embeddings.embed_query.assert_called_once_with(text)
