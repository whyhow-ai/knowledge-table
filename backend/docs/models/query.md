# Query Models

This file defines Pydantic models related to queries and their responses.

## Class: Rule

Represents a rule for query processing.

### Attributes:
- `type` (Literal["must_return", "may_return", "max_length"]): The type of rule.
- `options` (Optional[List[str]]): Possible options for the rule.
- `length` (Optional[int]): The length constraint for the rule.

## Class: Chunk

Represents a chunk of content in a query response.

### Attributes:
- `content` (str): The content of the chunk.
- `page` (int): The page number where the chunk is found.

## Class: Answer

Represents an answer to a query.

### Attributes:
- `id` (str): Unique identifier for the answer.
- `document_id` (str): The ID of the document containing the answer.
- `prompt_id` (str): The ID of the prompt used to generate the answer.
- `answer` (Optional[Union[int, str, bool, List[int], List[str]]]): The actual answer content.
- `chunks` (List[Chunk]): List of chunks supporting the answer.
- `type` (str): The type of the answer.

## Usage

```python
from app.models.query import Rule, Chunk, Answer

rule = Rule(type="must_return", options=["option1", "option2"])

chunk = Chunk(content="Sample content", page=1)

answer = Answer(
    id="123",
    document_id="doc1",
    prompt_id="prompt1",
    answer="Sample answer",
    chunks=[chunk],
    type="text"
)
````


These models are used to represent and validate query-related data in the application.
``````

This markdown file provides documentation for the query-related models in your `query.py` file, explaining their structure, attributes, and providing a usage example.
````

````
