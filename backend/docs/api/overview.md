# Knowledge Table API Overview

Welcome to the Knowledge Table API! This summary provides a quick overview of key endpoints, usage guidelines, and how to access the interactive API documentation.

---

**Base URL**

All API requests should be made to the following base URL for version 1:

```
https://api.example.com/v1
```

---

**Documentation**

Explore and test all API endpoints through the interactive docs provided by FastAPI:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) – A user-friendly interface for API exploration.
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc) – A clean reference for detailed API information.

---

Knowledge Table currently offers the following backend endpoints for document management, graph export, and query processing:

**Document**  
 Upload and manage documents within the Knowledge Table system.

- **POST** `/document` – Uploads and processes a document.
- **DELETE** `/document/{document_id}` – Deletes a document by its ID.  
  For details, refer to [Document Endpoints](v1/endpoints/document.md).

**Graph**  
 Export structured data from processed documents in the form of triples.

- **POST** `/graph/export-triples` – Exports triples (subject, predicate, object) based on table data.  
  More information is available at [Graph Endpoints](v1/endpoints/graph.md).

**Query**  
 Run queries to interact with documents using natural language or structured queries.

- **POST** `/query` – Submits a query and receives a structured response with relevant document data.  
  See [Query Endpoints](v1/endpoints/query.md) for further details.

---

**Error Codes**

Standard HTTP status codes are used to indicate request success or failure:

| Status Code | Error                   | Description                      |
| ----------- | ----------------------- | -------------------------------- |
| `200`       | `OK`                    | Successful request               |
| `400`       | `Bad Request`           | Invalid request parameters       |
| `401`       | `Unauthorized`          | Authentication failed or missing |
| `404`       | `Not Found`             | Resource not found               |
| `500`       | `Internal Server Error` | Server encountered an error      |
