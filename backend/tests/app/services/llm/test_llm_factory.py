"""Tests for the LLM factory"""

from unittest.mock import Mock, patch

import pytest

from app.services.llm.base import LLMService
from app.services.llm.factory import LLMFactory
from app.services.llm.openai_service import OpenAIService


@pytest.mark.parametrize(
    "provider, expected_type",
    [("openai", OpenAIService), ("unknown_provider", type(None))],
)
def test_create_llm_service(provider, expected_type):
    """Test the create_llm_service method of LLMFactory."""
    # Given
    factory = LLMFactory()

    # When
    service = factory.create_llm_service(provider)

    # Then
    assert isinstance(service, expected_type)


@patch("app.services.llm.factory.OpenAIService")
def test_create_openai_service_initialization(mock_openai_service):
    """Test that OpenAIService is correctly initialized when created."""
    # Given
    factory = LLMFactory()
    mock_openai_service.return_value = Mock(spec=LLMService)

    # When
    service = factory.create_llm_service("openai")

    # Then
    mock_openai_service.assert_called_once()
    assert isinstance(service, LLMService)


@patch("app.services.llm.factory.logger")
def test_logging_in_create_llm_service(mock_logger):
    """Test that the correct log message is created when creating a service."""
    # Given
    factory = LLMFactory()
    provider = "test_provider"

    # When
    factory.create_llm_service(provider)

    # Then
    mock_logger.info.assert_called_once_with(
        f"Creating LLM service for provider: {provider}"
    )


def test_create_llm_service_default_provider():
    """Test that the default provider is 'openai' when no provider is specified."""
    # Given
    factory = LLMFactory()

    # When
    service = factory.create_llm_service()

    # Then
    assert isinstance(service, OpenAIService)


@pytest.mark.parametrize("provider", ["gpt4", "claude", "llama"])
def test_create_llm_service_unsupported_provider(provider):
    """Test that None is returned for unsupported providers."""
    # Given
    factory = LLMFactory()

    # When
    service = factory.create_llm_service(provider)

    # Then
    assert service is None
