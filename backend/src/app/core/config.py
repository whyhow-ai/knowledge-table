"""Configuration settings for the application.

This module defines the configuration settings using Pydantic's
SettingsConfigDict to load environment variables from a .env file.
"""

import os
from typing import List, Optional

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # API CONFIG
    PROJECT_NAME: str = "Knowledge Table API"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = [
        "*"
    ]  # TODO: Restrict this in production

    # LLM CONFIG
    dimensions: int = 768
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    openai_api_key: Optional[str] = None

    # VECTOR DATABASE CONFIG
    vector_db_provider: str = "milvus-lite"
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

    @field_validator("openai_api_key", "unstructured_api_key", mode="before")
    @classmethod
    def validate_api_keys(
        cls, v: Optional[str], info: ValidationInfo
    ) -> Optional[str]:
        """Validate the API keys."""
        if v is None or v.strip() == "":
            return None
        return v.strip()

    @property
    def is_openai_available(self) -> bool:
        """Check if OpenAI service is available."""
        return self.openai_api_key is not None

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(__file__), "..", "..", "..", ".env"
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="_",
    )


settings = Settings()
