"""Tests for the config module."""

from unittest.mock import patch

from app.core.config import Settings


def test_settings_default_values():
    """Test that Settings initializes with default values."""
    with patch.dict("os.environ", {}, clear=True):
        settings = Settings(_env_file=None)

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
    assert settings.openai_api_key is None
    assert settings.unstructured_api_key is None


def test_settings_custom_values():
    """Test that Settings can be initialized with custom values."""
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

    with patch.dict("os.environ", custom_values, clear=True):
        settings = Settings(_env_file=None)

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


def test_api_key_validation():
    """Test API key validation and initialization."""
    # Test with no API keys
    with patch.dict("os.environ", {}, clear=True):
        settings = Settings(_env_file=None)
        assert settings.openai_api_key is None
        assert settings.unstructured_api_key is None

    # Test with environment variables
    with patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "test_openai_key",
            "UNSTRUCTURED_API_KEY": "test_unstructured_key",
        },
        clear=True,
    ):
        settings = Settings(_env_file=None)
        assert settings.openai_api_key == "test_openai_key"
        assert settings.unstructured_api_key == "test_unstructured_key"

    # Test with only one API key set
    with patch.dict(
        "os.environ", {"OPENAI_API_KEY": "test_openai_key"}, clear=True
    ):
        settings = Settings(_env_file=None)
        assert settings.openai_api_key == "test_openai_key"
        assert settings.unstructured_api_key is None

    with patch.dict(
        "os.environ",
        {"UNSTRUCTURED_API_KEY": "test_unstructured_key"},
        clear=True,
    ):
        settings = Settings(_env_file=None)
        assert settings.openai_api_key is None
        assert settings.unstructured_api_key == "test_unstructured_key"
