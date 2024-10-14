# LLM Response Models

This file defines Pydantic models for validating responses from the LLM API.

## Base Classes

### BaseResponseModel

Base class for response models with common validation logic.

#### Methods:
- `validate_none(cls, v: Any) -> Optional[Any]`: Validates if the value is None or equivalent to None.

### ArrayResponseModel

Base class for array response models.

#### Methods:
- `validate_array(cls, v: Any, max_length: Optional[int] = None) -> Optional[List[Any]]`: Validates if the value is a list or None, and applies max length constraint if specified.

## Response Models

### BoolResponseModel

Validates boolean responses.

#### Attributes:
- `answer` (Optional[bool]): The boolean answer to the query.

#### Methods:
- `validate_bool(cls, v: Union[str, bool, None]) -> Optional[bool]`: Validates if the value is a boolean or None.

### IntResponseModel

Validates integer responses.

#### Attributes:
- `answer` (Optional[int]): The integer answer to the query.

#### Methods:
- `validate_int(cls, v: Union[str, int, None]) -> Optional[int]`: Validates if the value is an integer or None.

### IntArrayResponseModel

Validates integer array responses.

#### Attributes:
- `answer` (Optional[List[int]]): The list of integer answers to the query.

#### Methods:
- `validate_int_array(cls, v: Any, info: ValidationInfo) -> Optional[List[int]]`: Validates if the value is an integer array or None.

### StrArrayResponseModel

Validates string array responses.

#### Attributes:
- `answer` (Optional[List[str]]): The list of string answers to the query.

#### Methods:
- `validate_str_array(cls, v: Any, info: ValidationInfo) -> Optional[List[str]]`: Validates if the value is a string array or None.

### StrResponseModel

Validates string responses.

#### Attributes:
- `answer` (Optional[str]): The string answer to the query.

#### Methods:
- `validate_str(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]`: Validates if the value is a string or None.

### KeywordsResponseModel

Validates keyword responses.

#### Attributes:
- `keywords` (Optional[List[str]]): The extracted keywords from the query.

#### Methods:
- `validate_keywords(cls, v: Any) -> Optional[List[str]]`: Validates if the value is a string array or None.

### SubQueriesResponseModel

Validates sub-query responses.

#### Attributes:
- `sub_queries` (Optional[List[str]]): The decomposed sub-queries.

#### Methods:
- `validate_sub_queries(cls, v: Any) -> Optional[List[str]]`: Validates if the value is a string array or None.

### SchemaRelationship

Represents a schema relationship.

#### Attributes:
- `head` (str): The head entity of the relationship.
- `relation` (str): The relation between the head and tail entities.
- `tail` (str): The tail entity of the relationship.

### SchemaResponseModel

Validates schema responses.

#### Attributes:
- `relationships` (Optional[List[SchemaRelationship]]): The relationships in the schema.

#### Methods:
- `validate_relationships(cls, v: Any) -> Optional[List[SchemaRelationship]]`: Validates if the value is a schema relationship array or None.

## Usage

```python
from app.models.llm import BoolResponseModel, IntArrayResponseModel, SchemaResponseModel, SchemaRelationship

bool_response = BoolResponseModel(answer=True)
int_array_response = IntArrayResponseModel(answer=[1, 2, 3])
schema_response = SchemaResponseModel(relationships=[
    SchemaRelationship(head="Person", relation="lives_in", tail="City")
])
````


These models are used to validate and structure responses from the LLM API in the application.
``````

This markdown file provides documentation for the LLM response models in your `llm.py` file, explaining their structure, attributes, methods, and providing a usage example.
````
