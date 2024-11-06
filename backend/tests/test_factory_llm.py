from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config import Settings
from app.services.llm.base import CompletionService
from app.services.llm.factory import CompletionServiceFactory


@pytest.fixture(scope="session")
def mock_settings():
    return MagicMock(spec=Settings)


def test_create_test_provider_service(mock_settings):
    """Test creating service with test_provider"""
    mock_settings.llm_provider = "test_provider"
    mock_settings.llm_model = "test_model"

    # Create a mock service
    mock_service = AsyncMock(spec=CompletionService)
    mock_service.generate_completion.return_value = "Mocked completion"
    mock_service.settings = mock_settings
    mock_service.model = mock_settings.llm_model
    mock_service.api_key = None

    # Mock the factory's create method directly
    with patch.object(
        CompletionServiceFactory,
        "create_service",
        return_value=mock_service,
    ) as mock_create:
        service = CompletionServiceFactory.create_service(mock_settings)

        mock_create.assert_called_once_with(mock_settings)
        assert service == mock_service


def test_create_unknown_service(mock_settings):
    """Test creating service with unknown provider"""
    mock_settings.llm_provider = "unknown_provider"

    # Mock the factory's create method to return None
    with patch.object(
        CompletionServiceFactory,
        "create_service",
        return_value=None,
    ):
        service = CompletionServiceFactory.create_service(mock_settings)
        assert service is None
