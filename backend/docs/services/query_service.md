# Query Service

The `QueryService` processes various types of queries, leveraging vector database searches and language model responses. It supports `decomposition`, `hybrid`, and `simple_vector` query types.

---

## Core Functions

**get_vector_db_service**  
 Retrieves the vector database service instance.

```python
async def get_vector_db_service() -> Any
```

**Returns**:

- `Any`: An instance of the vector database service.

**Raises**:

- `ValueError`: If vector database service creation fails.

**process_query**  
 Processes a query based on the specified type.

```python
async def process_query(
    query_type: Literal["decomposition", "hybrid", "simple_vector"],
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]
```

**Parameters**:

- `query_type`: Type of query (`decomposition`, `hybrid`, or `simple_vector`).
- `query`: Query text to process.
- `document_id`: ID of the document to search.
- `rules`: Rules to apply during query processing.
- `format`: Desired answer format.
- `llm_service`: Language model service for generating responses.

**Returns**:

- `Dict[str, Any]`: Contains `answer` and relevant `chunks`.

**decomposition_query**  
 Wrapper for processing a `decomposition` type query.

```python
async def decomposition_query(...) -> Dict[str, Any]
```

**hybrid_query**  
 Wrapper for processing a `hybrid` type query.

```python
async def hybrid_query(...) -> Dict[str, Any]
```

**simple_vector_query**  
 Wrapper for processing a `simple_vector` type query.

```python
async def simple_vector_query(...) -> Dict[str, Any]
```

---

## Usage

Each query type is implemented as a separate function but calls the main `process_query` function.

Example:

```python
llm_service = get_llm_service()  # Assume this function exists
query = "What is the capital of France?"
document_id = "doc123"
rules = [Rule(type="must_return", options=["city name"])]

result = await decomposition_query(query, document_id, rules, format="str", llm_service=llm_service)
print(result)  # {'answer': 'Paris', 'chunks': [...]}
```

---

## Configuration

Settings affecting the `QueryService` include:

- **vector_db_provider**: Specifies the provider used by `VectorDBFactory` to create the vector database service.

These configurations are accessed through `get_settings()` and can be customized in the application’s configuration file.

---

## Error Handling

The service includes error handling for:

- Vector database service creation: Raises `ValueError` if creation fails.
- Relies on underlying services (`VectorDBService`, `LLMService`) for additional error handling during query processing and response generation.

Errors are logged for debugging, and exceptions are managed to ensure service stability.

---

## Dependencies

- **app.core.dependencies**: Provides access to `get_llm_service` and `get_settings`.
- **app.models.query**: Defines `Rule`, used to apply constraints during query processing.
- **app.services.llm_service**: Provides `LLMService` and `generate_response` for response generation.
- **app.services.vector_db.factory**: Creates the vector database service with `VectorDBFactory`.

---

## Models

### Rule

Represents a rule for query processing.

```python
from app.models.query import Rule

rule = Rule(type="must_return", options=["option1", "option2"])
```

Attributes:

- `type` (Literal["must_return", "may_return", "max_length"]): The type of rule.
- `options` (Optional[List[str]]): Possible options for the rule.
- `length` (Optional[int]): The length constraint for the rule.

---

### Chunk

Represents a chunk of content in a query response.

```python
from app.models.query import Chunk

chunk = Chunk(content="Sample content", page=1)
```

Attributes:

- `content` (str): The content of the chunk.
- `page` (int): The page number where the chunk is found.

---

### Answer

Represents an answer to a query.

```python
from app.models.query import Answer, Chunk

chunk = Chunk(content="Sample content", page=1)
answer = Answer(
    id="123",
    document_id="doc1",
    prompt_id="prompt1",
    answer="Sample answer",
    chunks=[chunk],
    type="text"
)
```

Attributes:

- `id` (str): Unique identifier for the answer.
- `document_id` (str): The ID of the document containing the answer.
- `prompt_id` (str): The ID of the prompt used to generate the answer.
- `answer` (Optional[Union[int, str, bool, List[int], List[str]]]): The actual answer content.
- `chunks` (List[`Chunk`]): List of chunks supporting the answer.
- `type` (str): The type of the answer.
