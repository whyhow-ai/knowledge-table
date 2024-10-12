"""Tests for the config module."""

from pydantic import BaseModel, Field

from app.core.config import Settings


def test_settings_default_values(monkeypatch):
    """Test that Settings initializes with default values."""
    # GIVEN: No environment variables are set
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("UNSTRUCTURED_API_KEY", raising=False)

    # WHEN: Settings are initialized
    settings = Settings()

    # THEN: Default values should be set correctly
    assert settings.PROJECT_NAME == "Knowledge Table API"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.BACKEND_CORS_ORIGINS == ["*"]
    assert settings.dimensions == 768
    assert settings.embedding_provider == "openai"
    assert settings.embedding_model == "text-embedding-3-small"
    assert settings.llm_provider == "openai"
    assert settings.llm_model == "gpt-4o"
    assert settings.vector_db_provider == "milvus-lite"
    assert settings.index_name == "milvus"
    assert settings.milvus_db_uri == "./milvus_demo.db"
    assert settings.milvus_db_token == "root:Milvus"
    assert settings.query_type == "hybrid"
    assert settings.loader == "pypdf"
    assert settings.chunk_size == 512
    assert settings.chunk_overlap == 64
    assert hasattr(settings, "openai_api_key")
    assert hasattr(settings, "unstructured_api_key")


def test_settings_custom_values(monkeypatch):
    """Test that Settings can be initialized with custom values from environment variables."""
    # GIVEN: Custom environment variables are set
    custom_values = {
        "PROJECT_NAME": "Custom API",
        "API_V1_STR": "/custom/api",
        "BACKEND_CORS_ORIGINS": '["http://localhost", "https://example.com"]',
        "DIMENSIONS": "1024",
        "EMBEDDING_PROVIDER": "custom_provider",
        "EMBEDDING_MODEL": "custom-embedding-model",
        "LLM_PROVIDER": "custom_llm",
        "LLM_MODEL": "custom-gpt",
        "OPENAI_API_KEY": "custom_openai_key",
        "VECTOR_DB_PROVIDER": "custom_db",
        "INDEX_NAME": "custom_index",
        "MILVUS_DB_URI": "custom_uri",
        "MILVUS_DB_TOKEN": "custom_token",
        "QUERY_TYPE": "custom_query",
        "LOADER": "custom_loader",
        "CHUNK_SIZE": "1024",
        "CHUNK_OVERLAP": "128",
        "UNSTRUCTURED_API_KEY": "custom_unstructured_key",
    }
    for key, value in custom_values.items():
        monkeypatch.setenv(key, value)

    # WHEN: Settings are initialized
    settings = Settings()

    # THEN: Custom values should be set correctly
    assert settings.PROJECT_NAME == "Custom API"
    assert settings.API_V1_STR == "/custom/api"
    assert settings.BACKEND_CORS_ORIGINS == [
        "http://localhost",
        "https://example.com",
    ]
    assert settings.dimensions == 1024
    assert settings.embedding_provider == "custom_provider"
    assert settings.embedding_model == "custom-embedding-model"
    assert settings.llm_provider == "custom_llm"
    assert settings.llm_model == "custom-gpt"
    assert settings.openai_api_key == "custom_openai_key"
    assert settings.vector_db_provider == "custom_db"
    assert settings.index_name == "custom_index"
    assert settings.milvus_db_uri == "custom_uri"
    assert settings.milvus_db_token == "custom_token"
    assert settings.query_type == "custom_query"
    assert settings.loader == "custom_loader"
    assert settings.chunk_size == 1024
    assert settings.chunk_overlap == 128
    assert settings.unstructured_api_key == "custom_unstructured_key"


def test_validate_api_keys():
    """Test the validate_api_keys method."""

    # GIVEN: A mock Settings class and ValidationInfo
    class TestSettings(BaseModel):
        openai_api_key: str | None = Field(default=None)
        unstructured_api_key: str | None = Field(default=None)

    class MockValidationInfo:
        def __init__(self, data, field_name):
            self.data = data
            self.field_name = field_name

    # GIVEN: Test data with API keys
    test_data = {
        "openai_api_key": "test_key",
        "unstructured_api_key": "test_unstructured_key",
    }

    # WHEN: v is None and field_name is in data
    # THEN: The method should return the value from the data
    assert (
        Settings.validate_api_keys(
            None, MockValidationInfo(test_data, "openai_api_key")
        )
        == "test_key"
    )
    assert (
        Settings.validate_api_keys(
            None, MockValidationInfo(test_data, "unstructured_api_key")
        )
        == "test_unstructured_key"
    )

    # GIVEN: An existing key value
    # WHEN: v is not None
    # THEN: The method should return the existing value
    assert (
        Settings.validate_api_keys(
            "existing_key", MockValidationInfo(test_data, "openai_api_key")
        )
        == "existing_key"
    )

    # GIVEN: Empty data
    empty_data = {}
    # WHEN: v is None and field_name is not in data
    # THEN: The method should return None
    assert (
        Settings.validate_api_keys(
            None, MockValidationInfo(empty_data, "non_existent_key")
        )
        is None
    )


def test_api_key_validation_in_settings(monkeypatch):
    """Test that API keys are properly handled in Settings initialization."""
    # GIVEN: No environment variables are set
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("UNSTRUCTURED_API_KEY", raising=False)

    # WHEN: Settings are initialized
    settings = Settings()

    # THEN: API key attributes should exist
    assert hasattr(settings, "openai_api_key")
    assert hasattr(settings, "unstructured_api_key")

    # GIVEN: Environment variables are set
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("UNSTRUCTURED_API_KEY", "test_unstructured_key")

    # WHEN: Settings are initialized
    settings = Settings()

    # THEN: API keys should match the set values
    assert settings.openai_api_key == "test_openai_key"
    assert settings.unstructured_api_key == "test_unstructured_key"

    # GIVEN: Environment variables are cleared
    monkeypatch.delenv("OPENAI_API_KEY")
    monkeypatch.delenv("UNSTRUCTURED_API_KEY")

    # WHEN: Settings are initialized
    settings = Settings()

    # THEN: API key attributes should exist
    assert hasattr(settings, "openai_api_key")
    assert hasattr(settings, "unstructured_api_key")
