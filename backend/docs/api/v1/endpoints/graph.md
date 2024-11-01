# Graph API Overview

This section covers the API endpoints related to exporting graph triples from tables in the Knowledge Table backend. These endpoints allow you to generate triples (subject, predicate, object) based on structured data in tables and export the results as a JSON file.

**How it works**

1. The backend receives the table structure (columns, rows, chunks) in the request body.
2. The service validates the table and ensures the data is correctly formatted.
3. Using a Language Model (LLM) service, the system generates a schema for the table.
4. Based on the schema, the service generates triples (subject, predicate, object) and extracts data chunks.
5. The response contains the generated triples and chunks in JSON format, downloadable as a file.

---

## **Export Triples**

`POST /graph/export-triples`

**Description**  
Export triples (subject, predicate, object) from a table based on the provided data. The results are returned as a JSON file containing both the triples and additional chunks of extracted data.

### Request

**Method**: `POST`

**URL**: `/graph/export-triples`

**Headers**:

- `Content-Type`: `application/json`

**Body**: JSON object representing a table with columns, rows, and chunks.

**Parameters**

| Name      | In   | Type   | Description                                        |
| --------- | ---- | ------ | -------------------------------------------------- |
| `columns` | body | `list` | A list of columns                                  |
| `rows`    | body | `list` | A list of rows                                     |
| `chunks`  | body | `dict` | A dictionary of chunk objects associated with rows |

**Example**

```python
import requests

url = "http://localhost:8000/api/v1/graph/export-triples"
headers = {
    "Content-Type": "application/json"
}
data = {
  "columns": [
    {
      "id": "column1",
      "hidden": false,
      "entityType": "Person",
      "type": "text",
      "generate": true,
      "query": "Who is mentioned in the document?",
      "rules": [
        {
          "type": "may_return",
          "options": ["Jill", "Jane"]
        }
      ]
    },
    {
      "id": "column2",
      "hidden": false,
      "entityType": "Location",
      "type": "text",
      "generate": true,
      "query": "Where is @[Person](column1) from?",
      "rules": [
        {
          "type": "must_return",
          "options": ["New York", "Los Angeles"]
        }
      ]
    }
  ],
  "rows": [
    {
      "id": "row1",
      "sourceData": {
        "documentId": "doc123",
        "metadata": {
          "author": "John Doe",
          "title": "Sample Document"
        }
      },
      "hidden": false,
      "cells": {
        "column1": "Jill",
        "column2": "New York"
      }
    },
    {
      "id": "row2",
      "sourceData": "raw_text",
      "hidden": "true",
      "cells": {
        "column1": "Jane",
        "column2": "Los Angeles"
      }
    }
  ],
  "chunks": {
    "row1-column1": [
      {
        "content": "This is some content from page 1.",
        "page": 1
      },
      {
        "content": "Additional content from page 2.",
        "page": 2
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
  "triples": [
    {
      "triple_id": "1",
      "head": {
        "label": "Person",
        "name": "Jill"
      },
      "tail": {
        "label": "Location",
        "name": "New York"
      },
      "relation": {
        "name": "is_from"
      },
      "chunk_ids": ["c_1234", "c_5678"]
    }
  ],
  "chunks": [
    {
      "chunk_id": "c_1234",
      "content": "This is some content from page 1.",
      "page": "1",
      "triple_id": "1"
    },
    {
      "chunk_id": "c_5678",
      "content": "Additional content from page 2.",
      "page": "2",
      "triple_id": "1"
    }
  ]
}
```

### Error Responses

| Status Code | Error                   | Description                                            |
| ----------- | ----------------------- | ------------------------------------------------------ |
| `400`       | `Bad Request`           | Invalid JSON in the request body                       |
| `422`       | `Unprocessable Entity`  | Validation error in the request data                   |
| `500`       | `Internal Server Error` | An unexpected error occurred during the export process |
