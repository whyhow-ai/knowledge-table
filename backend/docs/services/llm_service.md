# LLM Service

This module provides functions for generating responses from a language model (LLM) based on various prompts and input data. It handles different types of queries, including keyword extraction, schema generation, and query decomposition.

## Functions

### generate_response

````python
async def generate_response(
    llm_service: LLMService,
    query: str,
    chunks: str,
    rules: list[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
) -> dict[str, Any]:
````


Generates a response from the language model based on the given query and format.

**Parameters:**
- `llm_service` (LLMService): The language model service to use.
- `query` (str): The user's query to be answered.
- `chunks` (str): The context or relevant text chunks for answering the query.
- `rules` (list[Rule]): A list of rules to apply when generating the response.
- `format` (Literal["int", "str", "bool", "int_array", "str_array"]): The desired format of the response.

**Returns:**
- `dict[str, Any]`: A dictionary containing the generated answer or an error message.

### get_keywords

````python
async def get_keywords(
    llm_service: LLMService, query: str
) -> dict[str, list[str] | None]:
````


Extracts keywords from a query using the language model.

**Parameters:**
- `llm_service` (LLMService): The language model service to use.
- `query` (str): The query from which to extract keywords.

**Returns:**
- `dict[str, list[str] | None]`: A dictionary containing the extracted keywords or None if an error occurs.

### get_similar_keywords

````python
async def get_similar_keywords(
    llm_service: LLMService, chunks: str, rule: list[str]
) -> dict[str, Any]:
````


Retrieves keywords similar to the provided keywords from the given text chunks.

**Parameters:**
- `llm_service` (LLMService): The language model service to use.
- `chunks` (str): The text chunks to search for similar keywords.
- `rule` (list[str]): The list of keywords to use as a reference.

**Returns:**
- `dict[str, Any]`: A dictionary containing the similar keywords found or None if an error occurs.

### decompose_query

````python
async def decompose_query(
    llm_service: LLMService, query: str
) -> dict[str, Any]:
````


Decomposes a complex query into multiple simpler sub-queries.

**Parameters:**
- `llm_service` (LLMService): The language model service to use.
- `query` (str): The complex query to be decomposed.

**Returns:**
- `dict[str, Any]`: A dictionary containing the list of sub-queries or None if an error occurs.

### generate_schema

````python
async def generate_schema(
    llm_service: LLMService, data: Table
) -> dict[str, Any]:
````


Generates a schema for the table based on column information and questions.

**Parameters:**
- `llm_service` (LLMService): The language model service to use.
- `data` (Table): The table data containing information about columns, rows, and documents.

**Returns:**
- `dict[str, Any]`: A dictionary containing the generated schema or None if an error occurs.

## Helper Functions

### _get_str_rule_line

````python
def _get_str_rule_line(str_rule: Rule | None, query: str) -> str:
````


Generates a string rule line based on the given string rule and query.

### _get_int_rule_line

````python
def _get_int_rule_line(int_rule: Rule | None) -> str:
````


Generates an integer rule line based on the given integer rule.

## Usage

These functions are typically used in conjunction with an LLM service to process queries, generate responses, and manipulate data. They are designed to be flexible and handle various types of inputs and outputs.

Example usage:

````python
llm_service = get_llm_service()  # Assume this function exists to get an LLM service
query = "What is the capital of France?"
chunks = "Paris is the capital and most populous city of France."
rules = [Rule(type="must_return", options=["city name"])]

response = await generate_response(llm_service, query, chunks, rules, format="str")
print(response)  # {'answer': 'Paris'}

keywords = await get_keywords(llm_service, query)
print(keywords)  # {'keywords': ['capital', 'France']}
````


## Error Handling

All functions include error handling to catch and log exceptions. In case of an error, they typically return a dictionary with a None value or an error message.

## Dependencies

This module depends on:
- Various response models from `app.models.llm`
- `Rule` model from `app.models.query`
- `Table` schema from `app.schemas.graph`
- `LLMService` from `app.services.llm.base`
- Various prompt templates from `app.services.llm.prompts`

Ensure all these dependencies are properly installed and imported in your environment.
`````

This documentation provides an overview of the `llm_service.py` file, detailing its functions, their parameters, return values, and usage. It also includes information about helper functions, error handling, and dependencies. This should help developers understand how to use and extend the LLM service functionality in the Knowledge Table backend.
````

````
