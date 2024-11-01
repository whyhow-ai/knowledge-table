# Query API Overview

This section covers the API endpoints related to querying documents in the Knowledge Table backend. The query system allows you to ask questions about documents using different retrieval methods, including vector search, hybrid search, and decomposed search. These queries utilize a combination of keyword searches and vector-based methods to generate answers from the document data.

---

## **Run Query**

`POST /query`

**Description**  
Run a query against a document using one of three methods: Simple Vector Search, Hybrid Search, or Decomposed Search.

### Request

**Method**: `POST`

**URL**: `/query`

**Headers**:

- `Content-Type`: `application/json`

**Body**: JSON object containing the query details, including the retrieval type, document ID, and the prompt/query itself.

**Parameters**

| Name          | In   | Type     | Description                                       |
| ------------- | ---- | -------- | ------------------------------------------------- |
| `document_id` | body | `string` | The ID of the document to query                   |
| `prompt`      | body | `object` | A column prompt in the `QueryPromptSchema` format |

### QueryPromptSchema Structure

| Name          | Type      | Description                                                               |
| ------------- | --------- | ------------------------------------------------------------------------- |
| `id`          | `string`  | ID of the column                                                          |
| `entity_type` | `string`  | The name of the entity in the Knowledge Table                             |
| `query`       | `string`  | The actual query or question                                              |
| `type`        | `Literal` | One of `"int"`, `"str"`, `"bool"`, `"int_array"`, `"str_array"`           |
| `rules`       | `list`    | _(Optional) `"must_return"`, `"may_return"`, `"max_length"`, `"replace"`_ |

**Example**

```python
import requests

url = "http://localhost:8000/api/v1/query"
headers = {
    "Authorization": "Bearer YOUR_API_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "document_id": "abc123",
    "prompt": {
        "id": "prompt1",
        "entity_type": "Disease",
        "query": "Which diseases are mentioned in this document?",
        "type": "str_array",
        "rules": [
            {
                "type": "must_return",
                "options": ["asthma", "diabetes","cancer"]
            }
        ]
    }
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

### Response

**Status Code**: `200 OK`

**Content-Type**: `application/json`

**Body**:

```json
{
  "answer": {
    "id": "e7f4a6b8c5df4c099f39bdf0e2a1db8e",
    "document_id": "abc123",
    "prompt_id": "prompt1",
    "answer": ["diabetes", "cancer"],
    "type": "str_array"
  },
  "chunks": [
    {
      "content": "This is some content from page 1.",
      "page": 1
    },
    {
      "content": "Additional content from page 2.",
      "page": 2
    }
  ],
  "resolved_entities": null
}
```

### Error Responses

| Status Code | Error                   | Description                                                          |
| ----------- | ----------------------- | -------------------------------------------------------------------- |
| `400`       | `Bad Request`           | The request contains an invalid query type or is otherwise malformed |
| `500`       | `Internal Server Error` | An error occurred while processing the query                         |

---

### Retrieval Types

#### 1. Vector Search

Performs a simple vector search on the document and retrieves the most relevant chunks of text based on the query. Ideal for finding similar passages in large documents.

#### 2. Hybrid Search (Default)

Combines both keyword and vector searches to retrieve relevant chunks from both methods, creating a more comprehensive response. Useful when the document contains both structured and unstructured data.

#### 3. Decomposed Search

Breaks the main query into smaller sub-queries, runs vector searches for each sub-query, and then compiles the results into a cohesive answer. Ideal for complex queries that require a step-by-step breakdown.
