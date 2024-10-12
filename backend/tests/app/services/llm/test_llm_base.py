"""Tests for the base LLM service"""

from typing import Any

import pytest

from app.services.llm.base import LLMService


class ConcreteLLMService(LLMService):
    """Concrete implementation of LLMService for testing purposes."""

    async def generate_completion(
        self, prompt: str, response_model: Any
    ) -> Any:
        return "Mocked completion"

    async def get_embeddings(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]

    async def decompose_query(self, query: str) -> list[str]:
        return [query]  # Simple implementation for testing purposes


@pytest.mark.asyncio
async def test_cannot_instantiate_abstract_llm_service():
    """Test that LLMService cannot be instantiated directly."""
    # Given
    # An abstract base class LLMService

    # When / Then
    with pytest.raises(TypeError) as exc_info:
        LLMService()

    assert (
        "Can't instantiate abstract class LLMService with abstract methods"
        in str(exc_info.value)
    )


@pytest.mark.asyncio
async def test_generate_completion_method():
    """Test the generate_completion method of ConcreteLLMService."""
    # Given
    prompt = "Hello, world!"
    response_model = Any
    llm_service = ConcreteLLMService()

    # When
    result = await llm_service.generate_completion(prompt, response_model)

    # Then
    assert result == "Mocked completion"


@pytest.mark.asyncio
async def test_get_embeddings_method():
    """Test the get_embeddings method of ConcreteLLMService."""
    # Given
    text = "Test text"
    llm_service = ConcreteLLMService()

    # When
    embeddings = await llm_service.get_embeddings(text)

    # Then
    assert embeddings == [0.1, 0.2, 0.3]
    assert isinstance(embeddings, list)
    assert all(isinstance(value, float) for value in embeddings)
