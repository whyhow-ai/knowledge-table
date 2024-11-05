# Document API Overview

This section covers endpoints for managing documents in the Knowledge Table backend. You can upload, delete, and interact with document data using these API calls.

---

## **Upload Document**

`POST /document`

**Description**  
Upload a document to the system for processing. This endpoint parses the document, extracting its content for further use.

### Request

**Method**: `POST`

**URL**: `/document`

**Headers**:

- `Content-Type`: `multipart/form-data`

**Parameters**

| Name   | In       | Type   | Description                 |
| ------ | -------- | ------ | --------------------------- |
| `file` | formData | `file` | The document file to upload |

**Example**

```python
import requests

url = "http://localhost:8000/api/v1/document"
files = {
    "file": open("/path/to/your/document.pdf", "rb")
}

response = requests.post(url, files=files)
print(response.json())
```

### Response

**Status Code**: `200 OK`

**Content-Type**: `application/json`

**Body**:

```json
{
  "document_id": "12345",
  "filename": "document.pdf",
  "status": "processed",
  "metadata": {
    "pages": 10,
    "title": "Sample Document",
    "author": "John Doe"
  }
}
```

### Error Responses

| Status Code | Error                   | Description                               |
| ----------- | ----------------------- | ----------------------------------------- |
| `400`       | `Bad Request`           | Malformed request or missing/invalid file |
| `500`       | `Internal Server Error` | Error during document processing          |

---

## **Delete Document**

`DELETE /document/{document_id}`

**Description**  
Delete a document from the system by specifying its unique document ID.

### Request

**Method**: `DELETE`

**URL**: `/document/{document_id}`

**Headers**:

**Path Parameters**

| Name          | In   | Type     | Description                   |
| ------------- | ---- | -------- | ----------------------------- |
| `document_id` | path | `string` | The unique ID of the document |

**Example**

```python
import requests

url = "http://localhost:8000/api/v1/document/12345"

response = requests.delete(url)
print(response.json())
```

### Response

**Status Code**: `200 OK`

**Body**:

```json
{
  "message": "Document deleted successfully",
  "document_id": "12345"
}
```

## Error Responses

| Status Code | Error                   | Description                      |
| ----------- | ----------------------- | -------------------------------- |
| `200`       | `OK`                    | Successful request               |
| `400`       | `Bad Request`           | Invalid request parameters       |
| `401`       | `Unauthorized`          | Authentication failed or missing |
| `404`       | `Not Found`             | Resource not found               |
| `500`       | `Internal Server Error` | Server encountered an error      |

---

## Schemas

This file defines Pydantic schemas for API requests and responses related to documents.

**DocumentCreate**

Schema for creating a new document.

- **`name`** (str): The name of the document.
- **`author`** (str): The author of the document.
- **`tag`** (str): A tag associated with the document.
- **`page_count`** (Annotated[int, Field(strict=True, gt=0)]): The number of pages in the document. This field is strictly validated to ensure it's a positive integer.

**DocumentResponse**

Schema for document response, inheriting from the Document model.

Inherits all attributes from the `Document` model:

- **`id`** (str): The unique identifier for the document.
- **`name`** (str): The name of the document.
- **`author`** (str): The author of the document.
- **`tag`** (str): A tag associated with the document.
- **`page_count`** (int): The number of pages in the document.

**DeleteDocumentResponse**

Schema for delete document response.

- **`id`** (str): The ID of the deleted document.
- **`status`** (str): The status of the delete operation.
- **`message`** (str): A message describing the result of the delete operation.

---

**Usage**

```python
from app.schemas.document import DocumentCreate, DocumentResponse, DeleteDocumentResponse

# Creating a new document
new_doc = DocumentCreate(
    name="Sample Document",
    author="John Doe",
    tag="sample",
    page_count=10
)

# Document response
doc_response = DocumentResponse(
    id="123",
    name="Sample Document",
    author="John Doe",
    tag="sample",
    page_count=10
)

# Delete document response
delete_response = DeleteDocumentResponse(
    id="123",
    status="success",
    message="Document successfully deleted"
)
```

These schemas are used to validate and structure data for API requests and responses related to queries in the application.
