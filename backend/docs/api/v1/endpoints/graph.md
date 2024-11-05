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

## Error Responses

| Status Code | Error                   | Description                                            |
| ----------- | ----------------------- | ------------------------------------------------------ |
| `400`       | `Bad Request`           | Invalid JSON in the request body                       |
| `422`       | `Unprocessable Entity`  | Validation error in the request data                   |
| `500`       | `Internal Server Error` | An unexpected error occurred during the export process |

---

## Schemas

This file defines Pydantic schemas for the graph API, including structures for prompts, table components, and export requests/responses.

**Prompt**

Represents a prompt used to extract specific information.

- **`entityType`** (str): The type of entity the prompt is associated with.
- **`id`** (str): Unique identifier for the prompt.
- **`query`** (str): The query text of the prompt.
- **`rules`** (List[Any]): List of rules associated with the prompt.
- **`type`** (str): The type of the prompt.

**Cell**

Represents a cell in a table.

- **`answer`** (Dict[str, Any]): The answer content of the cell.
- **`columnId`** (str): The ID of the column this cell belongs to.
- **`dirty`** (Union[bool, str]): Indicates if the cell has been modified.
- **`rowId`** (str): The ID of the row this cell belongs to.

**Column**

Represents a column in a table.

- **`id`** (str): Unique identifier for the column.
- **`prompt`** (Prompt): The prompt associated with this column.
- **`width`** (Union[int, str]): The width of the column.
- **`hidden`** (Union[bool, str]): Indicates if the column is hidden.

**Document**

Represents a document.

- **`id`** (str): Unique identifier for the document.
- **`name`** (str): The name of the document.
- **`author`** (str): The author of the document.
- **`tag`** (str): A tag associated with the document.
- **`page_count`** (Union[int, str]): The number of pages in the document.

**Row**

Represents a row in a table.

- **`id`** (str): Unique identifier for the row.
- **`document`** (Document): The document associated with this row.
- **`hidden`** (Union[bool, str]): Indicates if the row is hidden.

**Table**

Represents a table.

- **`columns`** (List[Column]): List of columns in the table.
- **`rows`** (List[Row]): List of rows in the table.
- **`cells`** (List[Cell]): List of cells in the table.

**ExportTriplesRequest**

Schema for export triples request.

- **`columns`** (List[Column]): List of columns in the table.
- **`rows`** (List[Row]): List of rows in the table.
- **`cells`** (List[Cell]): List of cells in the table.

**ExportTriplesResponse**

Schema for export triples response.

- **`triples`** (List[Dict[str, Any]]): List of triples exported.
- **`chunks`** (List[Dict[str, Any]]): List of chunks associated with the triples.

---

**Usage**

```python
from app.schemas.graph import Prompt, Cell, Column, Document, Row, Table, ExportTriplesRequest, ExportTriplesResponse

# Creating a prompt
prompt = Prompt(entityType="Person", id="1", query="What is the person's name?", rules=[], type="text")

# Creating a cell
cell = Cell(answer={"text": "John Doe"}, columnId="1", dirty=False, rowId="1")

# Creating a column
column = Column(id="1", prompt=prompt, width=100, hidden=False)

# Creating a document
document = Document(id="1", name="Sample Doc", author="Jane Doe", tag="sample", page_count=10)

# Creating a row
row = Row(id="1", document=document, hidden=False)

# Creating a table
table = Table(columns=[column], rows=[row], cells=[cell])

# Creating an export request
export_request = ExportTriplesRequest(columns=[column], rows=[row], cells=[cell])

# Creating an export response
export_response = ExportTriplesResponse(triples=[{"subject": "John", "predicate": "is", "object": "Person"}], chunks=[{"id": "1", "text": "John is a person"}])
```

These schemas are used to validate and structure data for API requests and responses related to queries in the application.
