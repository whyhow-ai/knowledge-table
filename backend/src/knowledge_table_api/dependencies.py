from functools import lru_cache
from pymilvus import MilvusClient
from .config import Settings

@lru_cache()
def get_settings():
    return Settings()

def get_milvus_client():
    settings = get_settings()
    return MilvusClient(
        "./milvus_demo.db", 
        token=f"{settings.milvus_db_username}:{settings.milvus_db_password}"
    )