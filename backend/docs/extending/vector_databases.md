# Extending Vector DB Services

This guide explains how to add support for new Vector Database services.

---

## Steps

### **1. Create a Vector DB Service Class**

In `src/app/services/vector_db/`, create a new file, e.g., `your_vector_db_service.py`.

```python
# your_vector_db_service.py
from typing import Any, Dict, List
from langchain.schema import Document as LangchainDocument
from app.models.query import Rule
from app.schemas.query import VectorResponse
from app.services.vector_db.base import VectorDBService
from app.services.llm_service import LLMService

class YourVectorDBService(VectorDBService):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> Dict[str, str]:
        # Implement vector upsert logic
        pass

    async def vector_search(self, queries: List[str], document_id: str) -> VectorResponse:
        # Implement vector search logic
        pass

    async def keyword_search(self, query: str, document_id: str, keywords: List[str]) -> VectorResponse:
        # Implement keyword search logic
        pass

    async def hybrid_search(self, query: str, document_id: str, rules: List[Rule]) -> VectorResponse:
        # Implement hybrid search logic
        pass

    async def decomposed_search(self, query: str, document_id: str, rules: List[Rule]) -> Dict[str, Any]:
        # Implement decomposed search logic
        pass

    async def delete_document(self, document_id: str) -> Dict[str, str]:
        # Implement document deletion logic
        pass

    async def ensure_collection_exists(self) -> None:
        # Implement collection creation logic
        pass

    async def prepare_chunks(self, document_id: str, chunks: List[LangchainDocument]) -> List[Dict[str, Any]]:
        # Implement chunk preparation logic
        pass
```

### **2. Update the Vector DB Factory**

In `src/app/services/vector_db/factory.py`, add an import and update the factory method.

```python
# factory.py
from app.services.vector_db.your_vector_db_service import YourVectorDBService

class VectorDBFactory:
    @staticmethod
    def create_vector_db_service(provider: str, llm_service: LLMService) -> Optional[VectorDBService]:
        logger.info(f"Creating vector database service with provider: {provider}")
        if provider.lower() == "milvus-lite":
            return MilvusService(llm_service)
        elif provider.lower() == "your_vector_db":
            return YourVectorDBService(llm_service)
        # Add other vector database providers here
        logger.warning(f"Unsupported vector database provider: {provider}")
        return None
```

### **3. Configure the Service**

In `src/app/core/config.py`, add a configuration option for your Vector DB.

```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    VECTOR_DB_PROVIDER: str = "milvus-lite"  # Default to Milvus-Lite

settings = Settings()
```

Update your environment variables or `.env` file:

```
VECTOR_DB_PROVIDER=your_vector_db
```

---

## Considerations

- **Authentication**: Ensure you handle any API keys or authentication required by your Vector DB service.
- **Error Handling**: Implement proper error handling in your service.
- **Testing**: Write unit tests for your new service.
- **Performance**: Optimize for large-scale vector operations.
- **Compatibility**: Ensure compatibility with the existing LLM service and document processing pipeline.

## Example

Here's an example of how you might implement the `vector_search` method for a hypothetical Vector DB:

```python
async def vector_search(self, queries: List[str], document_id: str) -> VectorResponse:
    results = []
    for query in queries:
        # Get embeddings for the query
        query_embedding = await self.llm_service.get_embeddings(query)

        # Perform the search in your Vector DB
        search_results = self.vector_db_client.search(
            collection_name="your_collection",
            query_vector=query_embedding,
            filter=f"document_id == '{document_id}'",
            limit=10
        )

        # Process and format the results
        for result in search_results:
            results.append(Chunk(
                content=result.text,
                page=result.metadata.get('page_number', 0)
            ))

    return VectorResponse(
        message="Query processed successfully.",
        chunks=results
    )
```
