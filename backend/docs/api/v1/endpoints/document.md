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

response = requests.post(url, headers=headers, files=files)
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

response = requests.delete(url, headers=headers)
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

### Error Responses

| Status Code | Error                   | Description                      |
| ----------- | ----------------------- | -------------------------------- |
| `200`       | `OK`                    | Successful request               |
| `400`       | `Bad Request`           | Invalid request parameters       |
| `401`       | `Unauthorized`          | Authentication failed or missing |
| `404`       | `Not Found`             | Resource not found               |
| `500`       | `Internal Server Error` | Server encountered an error      |
