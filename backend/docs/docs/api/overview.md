# API Overview

This document provides an overview of the Knowledge Table API endpoints.

## Base URL

All API requests should be made to: `https://api.example.com/v1`

## Endpoints

### Document

- **POST** `/document`
  - Upload and process a document
  - Request: Multipart form data with file
  - Response: Document information

- **DELETE** `/document/{document_id}`
  - Delete a document
  - Request: Path parameter `document_id`
  - Response: Deletion status and message

### Graph

- **POST** `/graph/export-triples`
  - Export triples from a table
  - Request: JSON body with table data
  - Response: Triples and chunks data

### Query

- **POST** `/query`
  - Run a query and generate a response
  - Request: JSON body with query details
  - Response: Answer with chunks

## Authentication

[Include information about authentication method, if applicable]

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests. In case of errors, additional details may be provided in the response body.

## Rate Limiting

[Include information about rate limiting, if applicable]

For detailed information on request and response schemas, please refer to the individual endpoint documentation.