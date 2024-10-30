from unittest.mock import MagicMock, patch

import pytest

from app.core.config import Settings
from app.services.llm.factory import CompletionServiceFactory


@pytest.fixture
def mock_settings():
    return MagicMock(spec=Settings)


def test_create_openai_service(mock_settings):
    mock_settings.llm_provider = "openai"

    with patch(
        "app.services.llm.factory.OpenAIService"
    ) as mock_openai_service:
        service = CompletionServiceFactory.create_service(mock_settings)

        mock_openai_service.assert_called_once_with(mock_settings)
        assert service == mock_openai_service.return_value


def test_create_unknown_service(mock_settings):
    mock_settings.llm_provider = "unknown_provider"

    service = CompletionServiceFactory.create_service(mock_settings)

    assert service is None
