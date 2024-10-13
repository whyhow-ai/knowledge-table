from unittest.mock import Mock, patch

import pytest

from app.core.config import settings
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
async def test_generate_completion(openai_service):
    # Given
    prompt = "Test prompt"
    response_model = {"type": "object"}
    expected_result = {"result": "Test result"}

    # Create a mock response that mimics the structure of the beta client response
    mock_message = Mock()
    mock_message.parsed = expected_result
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
    assert result == expected_result
    openai_service.client.beta.chat.completions.parse.assert_called_once_with(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        response_format=response_model,
    )


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
