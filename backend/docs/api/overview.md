# API Overview

Welcome to the Knowledge Table API! This page provides a high-level overview of the available API endpoints and their use.

## Base URL

All API requests should be made to the following base URL (for version 1):

```
https://api.example.com/v1
```

## Accessing the Interactive API Docs

Knowledge Table's backend uses [FastAPI](https://fastapi.tiangolo.com), which automatically generates interactive API documentation. You can explore all API endpoints, see request and response formats, and try out requests using the following interfaces:

- **Swagger UI**: [https://api.example.com/docs](https://api.example.com/docs)
  - A user-friendly interface to explore the API.
  
- **ReDoc**: [https://api.example.com/redoc](https://api.example.com/redoc)
  - A clean and detailed API reference using ReDoc.

## Error Handling

The API follows standard HTTP status codes to indicate the success or failure of requests. Here are some of the common status codes you may encounter:

- **200 OK**: The request was successful.
- **400 Bad Request**: The request was malformed or contained invalid parameters.
- **401 Unauthorized**: Authentication failed or was not provided.
- **403 Forbidden**: You do not have the necessary permissions for this request.
- **404 Not Found**: The requested resource could not be found.
- **500 Internal Server Error**: An error occurred on the server.

---

## API Endpoints Overview

Here is a summary of the key endpoints available in version 1 of the Knowledge Table API:

### Document Management

These endpoints allow you to upload, delete, and manage documents in the system.

- **POST** `/document`
- Upload and process a document.
- **Request**: Multipart form data containing the document file.
- **Response**: Document metadata and status.

- **DELETE** `/document/{document_id}`
- Delete a document by its ID.
- **Request**: Path parameter `document_id`.
- **Response**: Confirmation of document deletion.

For more details on document-related endpoints, see [Document Endpoints](v1/endpoints/document.md).

---

### Graph Management

The graph endpoints allow you to export structured data (e.g., triples) from processed documents.

- **POST** `/graph/export-triples`
- Export triples (subject, predicate, object) from a table.
- **Request**: JSON body containing table data.
- **Response**: Triples and associated chunk information.

For more information, see [Graph Endpoints](v1/endpoints/graph.md).

---

### Query Processing

These endpoints handle the processing of queries, enabling you to interact with the documents using natural language or other forms of structured querying.

- **POST** `/query`
- Submit a query and receive a structured response.
- **Request**: JSON body with query details.
- **Response**: Query result, including chunks of extracted data.

For additional details, see [Query Endpoints](v1/endpoints/query.md).

---

For more detailed information on specific endpoints and their schema, please refer to the interactive API documentation provided by FastAPI.
