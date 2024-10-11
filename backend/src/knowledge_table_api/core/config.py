"""Configuration settings for the application.

This module defines the configuration settings using Pydantic's
SettingsConfigDict to load environment variables from a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings class for the application."""

    # LLM CONFIG
    dimensions: int = 768
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    openai_api_key: str | None = None

    # VECTOR DATABASE CONFIG
    vector_db_provider: str = "milvus-lite"
    index_name: str = "milvus"
    milvus_db_uri: str = "./milvus_demo.db"
    milvus_db_token: str = "root:Milvus"

    # QUERY CONFIG
    query_type: str = "hybrid"

    # DOCUMENT PROCESSING CONFIG
    loader: str = "pypdf"
    chunk_size: int = 512
    chunk_overlap: int = 64

    # UNSTRUCTURED CONFIG
    unstructured_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
