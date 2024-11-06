# LLM Service

The LLM Service generates responses from a language model (LLM) based on various prompts and input data. It supports query decomposition, schema generation, and keyword extraction.

---

## Core Functions

**generate_response**  
 Generates a response from the LLM based on a query and specified format.

```python
async def generate_response(llm_service: LLMService, query: str, chunks: str, rules: list[Rule], format: Literal["int", "str", "bool", "int_array", "str_array"]) -> dict[str, Any]
```

**get_keywords**  
 Extracts keywords from a query using the LLM.

```python
async def get_keywords(llm_service: LLMService, query: str) -> dict[str, list[str] | None]
```

**get_similar_keywords**  
 Retrieves keywords similar to the provided list from text chunks.

```python
async def get_similar_keywords(llm_service: LLMService, chunks: str, rule: list[str]) -> dict[str, Any]
```

**decompose_query**  
 Breaks down a complex query into simpler sub-queries.

```python
async def decompose_query(llm_service: LLMService, query: str) -> dict[str, Any]
```

**generate_schema**  
 Generates a schema for a table based on column information and prompts.

```python
async def generate_schema(llm_service: LLMService, data: Table) -> dict[str, Any]
```

---

## Helper Functions

**\_get_str_rule_line**  
 Formats instructions for string-based rules, incorporating specific response rules into the prompt.

```python
def _get_str_rule_line(str_rule: Rule | None, query: str) -> str
```

**\_get_int_rule_line**  
 Generates instructions for integer-based rules, specifying the item limit in responses.

```python
def _get_int_rule_line(int_rule: Rule | None) -> str
```

---

## Usage

These functions are used with an LLM service to handle queries, extract keywords, and generate schemas.

```python
llm_service = get_llm_service()  # Assume this function exists to get an LLM service
query = "What is the capital of France?"
chunks = "Paris is the capital and most populous city of France."
rules = [Rule(type="must_return", options=["Paris", "London", "Berlin"])]

response = await generate_response(llm_service, query, chunks, rules, format="str")
print(response)  # {'answer': 'Paris'}

keywords = await get_keywords(llm_service, query)
print(keywords)  # {'keywords': ['capital', 'France']}
```

---

## Configuration

Settings for LLM-related operations, such as response formatting and rule handling, can be configured in the application's settings file.

---

## Error Handling

The LLM Service includes error handling and logging for:

- Query processing errors
- Schema generation issues
- Keyword extraction failures

Functions return either a dictionary with an error message or `None` in case of failure. Logging is enabled for key operations to aid in debugging.

---

## Dependencies

- **app.models.llm**: For response models like `BoolResponseModel`, `IntArrayResponseModel`, etc.
- **app.models.query**: For the `Rule` model.
- **app.schemas.graph**: For `Table` schema.
- **app.services.llm.base**: For `LLMService`.
- **app.services.llm.prompts**: For prompt templates like `BASE_PROMPT`, `SCHEMA_PROMPT`, etc.

---

## Models

### BoolResponseModel

Validates boolean responses.

```python
from app.models.llm import BoolResponseModel

bool_response = BoolResponseModel(answer=True)
```

Attributes:

- `answer` (Optional[bool]): The boolean answer to the query.

---

### IntResponseModel

Validates integer responses.

```python
from app.models.llm import IntResponseModel

int_response = IntResponseModel(answer=42)
```

Attributes:

- `answer` (Optional[int]): The integer answer to the query.

---

### IntArrayResponseModel

Validates integer array responses.

```python
from app.models.llm import IntArrayResponseModel

int_array_response = IntArrayResponseModel(answer=[1, 2, 3])
```

Attributes:

- `answer` (Optional[List[int]]): The list of integer answers to the query.

---

### StrArrayResponseModel

Validates string array responses.

```python
from app.models.llm import StrArrayResponseModel

str_array_response = StrArrayResponseModel(answer=["apple", "banana", "cherry"])
```

Attributes:

- `answer` (Optional[List[str]]): The list of string answers to the query.

---

### StrResponseModel

Validates string responses.

```python
from app.models.llm import StrResponseModel

str_response = StrResponseModel(answer="Hello, World!")
```

Attributes:

- `answer` (Optional[str]): The string answer to the query.

---

### KeywordsResponseModel

Validates keyword responses.

```python
from app.models.llm import KeywordsResponseModel

keywords_response = KeywordsResponseModel(keywords=["AI", "machine learning", "data science"])
```

Attributes:

- `keywords` (Optional[List[str]]): The extracted keywords from the query.

---

### SubQueriesResponseModel

Validates sub-query responses.

```python
from app.models.llm import SubQueriesResponseModel

sub_queries_response = SubQueriesResponseModel(sub_queries=["What is AI?", "How does ML work?"])
```

Attributes:

- `sub_queries` (Optional[List[str]]): The decomposed sub-queries.

---

### SchemaRelationship

Represents a schema relationship.

```python
from app.models.llm import SchemaRelationship

schema_relationship = SchemaRelationship(head="Person", relation="works_at", tail="Company")
```

Attributes:

- `head` (str): The head entity of the relationship.
- `relation` (str): The relation between the head and tail entities.
- `tail` (str): The tail entity of the relationship.

---

### SchemaResponseModel

Validates schema responses.

```python
from app.models.llm import SchemaResponseModel, SchemaRelationship

schema_response = SchemaResponseModel(relationships=[
    SchemaRelationship(head="Person", relation="lives_in", tail="City")
])
```

Attributes:

- `relationships` (Optional[List[`SchemaRelationship`]]): The relationships in the schema.
