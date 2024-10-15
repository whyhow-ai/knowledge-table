"""Configuration settings for the application.

This module defines the configuration settings using Pydantic's
SettingsConfigDict to load environment variables from a .env file.
"""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Qdrant(BaseSettings):
    """Qdrant connection configuration."""

    location: Optional[str] = None
    url: Optional[str] = None
    port: Optional[int] = 6333
    grpc_port: int = 6334
    prefer_grpc: bool = False
    https: Optional[bool] = None
    api_key: Optional[str] = None
    prefix: Optional[str] = None
    timeout: Optional[int] = None
    host: Optional[str] = None
    path: Optional[str] = None


class Settings(BaseSettings):
    """Settings class for the application."""

    # LLM CONFIG
    dimensions: int = 768
    embedding_provider: str = "openai"
    llm_provider: str = "openai"
    openai_api_key: str

    # Milvus CONFIG
    vector_db: str = "milvus-lite"
    index_name: str = "milvus"
    milvus_db_username: str = "root"
    milvus_db_password: str = "Milvus"

    # QUERY CONFIG
    query_type: str = "hybrid"

    # UNSTRUCTURED CONFIG
    unstructured_api_key: str | None = None

    # Qdrant config
    qdrant: Qdrant = Qdrant()

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="_"
    )


settings = Settings()
