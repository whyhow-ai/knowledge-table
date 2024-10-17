"""Tests for the vector database factory."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from app.services.llm.base import LLMService
from app.services.vector_db.factory import VectorDBFactory


class TestVectorDBFactory:

    @pytest.fixture
    def mock_llm_service(self):
        return MagicMock(spec=LLMService)

    def test_create_vector_db_service_logging(self, mock_llm_service, caplog):
        """
        Given: The VectorDBFactory
        When: Creating a vector database service
        Then: It should log the appropriate messages
        """
        with patch("app.services.vector_db.factory.MilvusService"):
            with caplog.at_level(logging.INFO):
                VectorDBFactory.create_vector_db_service(
                    "milvus", mock_llm_service
                )
            assert (
                "Creating vector database service with provider: milvus"
                in caplog.text
            )

        with caplog.at_level(logging.WARNING):
            VectorDBFactory.create_vector_db_service(
                "unknown-provider", mock_llm_service
            )
        assert (
            "Unsupported vector database provider: unknown-provider"
            in caplog.text
        )

    def test_create_vector_db_service_milvus_lite(self, mock_llm_service):
        """
        Given: The VectorDBFactory
        When: Creating a vector database service with 'milvus' provider
        Then: It should return a MilvusService instance
        """
        with patch(
            "app.services.vector_db.factory.MilvusService"
        ) as mock_milvus:
            result = VectorDBFactory.create_vector_db_service(
                "milvus", mock_llm_service
            )
            mock_milvus.assert_called_once_with(mock_llm_service)
            assert isinstance(
                result, MagicMock
            )  # In the test, it's a MagicMock due to patching
            assert result == mock_milvus.return_value

    def test_create_vector_db_service_milvus_lite_case_insensitive(
        self, mock_llm_service
    ):
        """
        Given: The VectorDBFactory
        When: Creating a vector database service with 'MILVUS' provider (uppercase)
        Then: It should return a MilvusService instance
        """
        with patch(
            "app.services.vector_db.factory.MilvusService"
        ) as mock_milvus:
            result = VectorDBFactory.create_vector_db_service(
                "MILVUS", mock_llm_service
            )
            mock_milvus.assert_called_once_with(mock_llm_service)
            assert isinstance(
                result, MagicMock
            )  # In the test, it's a MagicMock due to patching
            assert result == mock_milvus.return_value

    def test_create_vector_db_service_unknown_provider(self, mock_llm_service):
        """
        Given: The VectorDBFactory
        When: Creating a vector database service with an unknown provider
        Then: It should return None
        """
        result = VectorDBFactory.create_vector_db_service(
            "unknown-provider", mock_llm_service
        )
        assert result is None

    @pytest.mark.parametrize(
        "provider", ["milvus", "MILVUS", "Milvus"]
    )
    def test_create_vector_db_service_different_casings(
        self, provider, mock_llm_service
    ):
        """
        Given: The VectorDBFactory
        When: Creating a vector database service with different casings of 'milvus'
        Then: It should return a MilvusService instance for all casings
        """
        with patch(
            "app.services.vector_db.factory.MilvusService"
        ) as mock_milvus:
            result = VectorDBFactory.create_vector_db_service(
                provider, mock_llm_service
            )
            mock_milvus.assert_called_once_with(mock_llm_service)
            assert isinstance(
                result, MagicMock
            )  # In the test, it's a MagicMock due to patching
            assert result == mock_milvus.return_value
