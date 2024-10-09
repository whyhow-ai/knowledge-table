from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM CONFIG
    dimensions: int
    embedding_provider: str
    llm_provider: str
    openai_api_key: str

    # VECTOR DATABASE CONFIG
    vector_db: str
    index_name: str
    milvus_db_username: str
    milvus_db_password: str

    # QUERY CONFIG
    query_type: str

    # UNSTRUCTURED CONFIG
    unstructured_api_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()