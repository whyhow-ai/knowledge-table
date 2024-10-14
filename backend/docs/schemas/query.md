# Query Schemas

This file defines Pydantic schemas for API requests and responses related to queries.

## Class: QueryPrompt

Represents a query prompt.

### Attributes:
- `id` (str): Unique identifier for the prompt.
- `query` (str): The query text.
- `type` (Literal["int", "str", "bool", "int_array", "str_array"]): The expected type of the answer.
- `entity_type` (str): The type of entity the query is about.
- `rules` (Optional[List[Rule]]): Optional list of rules to apply to the query.

## Class: QueryRequest

Represents a query request.

### Attributes:
- `document_id` (str): The ID of the document to query.
- `previous_answer` (Optional[Union[int, str, bool, List[int], List[str]]]): The previous answer, if any.
- `prompt` (QueryPrompt): The query prompt.
- `rag_type` (Optional[Literal["vector", "hybrid", "decomposed"]]): The type of retrieval-augmented generation to use. Defaults to "hybrid".

## Class: VectorResponse

Represents a vector response.

### Attributes:
- `message` (str): A message associated with the response.
- `chunks` (List[Chunk]): List of relevant chunks from the document.
- `keywords` (Optional[List[str]]): Optional list of keywords extracted from the query.

## Class: QueryResponse

Represents a query response.

### Attributes:
- `id` (str): Unique identifier for the response.
- `document_id` (str): The ID of the document queried.
- `prompt_id` (str): The ID of the prompt used.
- `answer` (Optional[Union[int, str, bool, List[int], List[str]]]): The answer to the query.
- `chunks` (List[Chunk]): List of relevant chunks from the document.
- `type` (str): The type of the answer.

## Usage

```python
from app.schemas.query import QueryPrompt, QueryRequest, VectorResponse, QueryResponse
from app.models.query import Rule, Chunk

# Creating a query prompt
prompt = QueryPrompt(
    id="1",
    query="What is the capital of France?",
    type="str",
    entity_type="Location",
    rules=[Rule(type="must_return", options=["Paris", "Lyon", "Marseille"])]
)

# Creating a query request
request = QueryRequest(
    document_id="doc123",
    prompt=prompt,
    rag_type="hybrid"
)

# Creating a vector response
vector_response = VectorResponse(
    message="Retrieved relevant chunks",
    chunks=[Chunk(content="Paris is the capital of France.", page=1)],
    keywords=["capital", "France"]
)

# Creating a query response
query_response = QueryResponse(
    id="resp1",
    document_id="doc123",
    prompt_id="1",
    answer="Paris",
    chunks=[Chunk(content="Paris is the capital of France.", page=1)],
    type="str"
)
````


These schemas are used to validate and structure data for API requests and responses related to queries in the application.
