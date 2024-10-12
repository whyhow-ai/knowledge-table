from unittest.mock import Mock, patch

import pytest

from app.core.config import settings
from app.services.llm.openai_service import OpenAIService


@pytest.fixture
def openai_service():
    with (
        patch("app.services.llm.openai_service.OpenAI"),
        patch("app.services.llm.openai_service.OpenAIEmbeddings"),
    ):
        yield OpenAIService()


@pytest.mark.asyncio
async def test_generate_completion(openai_service):
    """Test the generate_completion method."""
    # Given
    prompt = "Test prompt"
    response_model = {"type": "object"}
    expected_result = {"result": "Test result"}
    openai_service.client.beta.chat.completions.parse.return_value = Mock(
        choices=[Mock(message=Mock(parsed=expected_result))]
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
    openai_service._get_embeddings_sync = Mock(
        return_value=expected_embeddings
    )

    # When
    result = await openai_service.get_embeddings(text)

    # Then
    assert result == expected_embeddings
    openai_service._get_embeddings_sync.assert_called_once_with(text)
