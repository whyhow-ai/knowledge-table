# Query Service

This module provides services for processing different types of queries using vector database search and language model generation. It supports decomposition, hybrid, and simple vector queries.

## Functions

### get_vector_db_service

```python
async def get_vector_db_service() -> Any:
```

Gets the vector database service instance.

**Returns:**
- `Any`: An instance of the vector database service.

**Raises:**
- `ValueError`: If the vector database service creation fails.

### process_query

```python
async def process_query(
    query_type: Literal["decomposition", "hybrid", "simple_vector"],
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
```

Processes the query based on the specified type.

**Parameters:**
- `query_type`: The type of query to perform.
- `query`: The query string.
- `document_id`: The ID of the document to search.
- `rules`: A list of rules to apply to the query.
- `format`: The desired format of the answer.
- `llm_service`: The language model service to use for generating responses.

**Returns:**
- `Dict[str, Any]`: A dictionary containing the answer and relevant chunks.

### decomposition_query

```python
async def decomposition_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
```

Performs a decomposition query. This is a wrapper function that calls `process_query` with the "decomposition" query type.

**Parameters:**
- `query`: The query string.
- `document_id`: The ID of the document to search.
- `rules`: A list of rules to apply to the query.
- `format`: The desired format of the answer.
- `llm_service`: The language model service to use for generating responses.

**Returns:**
- `Dict[str, Any]`: A dictionary containing the answer and relevant chunks.

### hybrid_query

```python
async def hybrid_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
```

Performs a hybrid query. This is a wrapper function that calls `process_query` with the "hybrid" query type.

**Parameters:**
- `query`: The query string.
- `document_id`: The ID of the document to search.
- `rules`: A list of rules to apply to the query.
- `format`: The desired format of the answer.
- `llm_service`: The language model service to use for generating responses.

**Returns:**
- `Dict[str, Any]`: A dictionary containing the answer and relevant chunks.

### simple_vector_query

```python
async def simple_vector_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
```

Performs a simple vector query. This is a wrapper function that calls `process_query` with the "simple_vector" query type.

**Parameters:**
- `query`: The query string.
- `document_id`: The ID of the document to search.
- `rules`: A list of rules to apply to the query.
- `format`: The desired format of the answer.
- `llm_service`: The language model service to use for generating responses.

**Returns:**
- `Dict[str, Any]`: A dictionary containing the answer and relevant chunks.

## Usage

The query service provides three main types of queries: decomposition, hybrid, and simple vector. Each query type is implemented as a separate function, but they all use the common `process_query` function internally.

Example usage:

```python
llm_service = get_llm_service()  # Assume this function exists to get an LLM service
query = "What is the capital of France?"
document_id = "doc123"
rules = [Rule(type="must_return", options=["city name"])]

result = await decomposition_query(query, document_id, rules, format="str", llm_service)
print(result)  # {'answer': 'Paris', 'chunks': [...]}
```

## Dependencies

This module depends on:
- `app.core.dependencies` for getting LLM service and settings
- `app.models.query` for the Rule model
- `app.services.llm_service` for LLMService and generate_response function
- `app.services.vector_db.factory` for VectorDBFactory

Ensure all these dependencies are properly installed and imported in your environment.

## Error Handling

The service includes error handling, particularly in the `get_vector_db_service` function, which raises a `ValueError` if the vector database service creation fails. Other functions may propagate exceptions from the underlying services they use.