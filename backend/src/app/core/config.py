"""Configuration settings for the application.

This module defines the configuration settings using Pydantic's
SettingsConfigDict to load environment variables from a .env file.
"""

import logging
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("uvicorn")


class Qdrant(BaseSettings):
    """Qdrant connection configuration."""

    model_config = SettingsConfigDict(env_prefix="QDRANT_")

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

    # ENVIRONMENT CONFIG
    environment: str = "dev"
    testing: bool = bool(0)

    # API CONFIG
    project_name: str = "Knowledge Table API"
    api_v1_str: str = "/api/v1"
    backend_cors_origins: List[str] = [
        "*"
    ]  # TODO: Restrict this in production

    # LLM CONFIG
    dimensions: int = 1536
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    openai_api_key: Optional[str] = None

    # VECTOR DATABASE CONFIG
    vector_db_provider: str = "milvus"
    index_name: str = "milvus"

    # MILVUS CONFIG
    milvus_db_uri: str = "./milvus_demo.db"
    milvus_db_token: str = "root:Milvus"

    # QDRANT CONFIG
    qdrant: Qdrant = Field(default_factory=lambda: Qdrant())

    # QUERY CONFIG
    query_type: str = "hybrid"

    # DOCUMENT PROCESSING CONFIG
    loader: str = "pypdf"
    chunk_size: int = 512
    chunk_overlap: int = 64

    # UNSTRUCTURED CONFIG
    unstructured_api_key: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="_",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get the settings for the application."""
    logger.info("Loading config settings from the environment...")
    return Settings()
