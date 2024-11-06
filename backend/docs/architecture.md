# Architecture Overview

This section provides an overview of the Knowledge Table backend architecture, covering key components and their interactions. Knowledge Table follows a modular, service-oriented architecture.

```mermaid
graph TD
    Client[Client Application] -->|HTTP Requests| API[API Layer]
    API -->|Calls| Services[Service Layer]
    Services -->|Uses| Models[Model Layer]
    Services -->|Integrates| Ext[External Services]
    Ext -->|LLM| OpenAI[OpenAI]
    Ext -->|Vector DB| Milvus[Milvus]
    Ext -->|Loaders| DocLoaders[Document Loaders]
    DocLoaders -->|PDF| PyPDF[PyPDF]
    DocLoaders -->|Unstructured| Unstructured[Unstructured]
```

## Components

**API Layer**

_Handles HTTP requests from clients using FastAPI_

- **`/documents/`**: Document upload and retrieval.
- **`/graphs/`**: Knowledge graph management.
- **`/queries/`**: Natural language query processing.

**Service Layer**

_Contains core business logic_

- **Document Service**: Manages document processing and storage.
- **Graph Service**: Handles knowledge graph creation and querying.
- **LLM Service**: Interfaces with language models for text analysis.
- **Query Service**: Processes queries and returns structured responses.

**Model Layer**

_Defines database models for documents, graphs, and queries_

**External Integrations**

_Connects to Language Models (LLMs), vector databases, and document loaders_

- **LLM**: Supports OpenAI and is extensible to other providers.
- **Vector Database**: Manages embeddings for similarity search using Milvus.
- **Document Loaders**: Processes PDFs and unstructured documents.

## Project Structure

```plaintext
backend/
├── src/
│   └── app/
│       ├── api/
│       │   └── v1/
│       │       └── endpoints/
│       │           ├── document.py
│       │           ├── graph.py
│       │           └── query.py
│       ├── core/
│       │   ├── config.py
│       │   └── dependencies.py
│       ├── models/
│       │   ├── document.py
│       │   ├── graph.py
│       │   ├── llm.py
│       │   └── query.py
│       ├── schemas/
│       │   ├── document.py
│       │   ├── graph.py
│       │   └── query.py
│       └── services/
│           ├── document_service.py
│           ├── graph_service.py
│           ├── llm_service.py
│           ├── query_service.py
│           ├── llm/
│           │   ├── base.py
│           │   ├── factory.py
│           │   |── openai_service.py
│           │   └── prompts.py
│           ├── loaders/
│           │   ├── base.py
│           │   ├── factory.py
│           │   ├── pypdf_service.py
│           │   └── unstructured_service.py
│           └── vector_db/
│               ├── base.py
│               ├── factory.py
│               └── milvus_service.py
├── tests/
└── docs/
```

## Data Flow

### Document Upload

```mermaid
sequenceDiagram
    Client->>API: Upload Document
    API->>DocumentService: Process Document
    DocumentService->>Loader: Parse Document
    Loader->>LLMService: Generate Embeddings
    LLMService->>VectorDB: Store Embeddings
    DocumentService->>Database: Store Metadata
    API->>Client: Confirmation
```

### Query Processing

```mermaid
sequenceDiagram
    Client->>API: Submit Query
    API->>QueryService: Process Query
    QueryService->>LLMService: Generate Query Embedding
    QueryService->>VectorDB: Search
    VectorDB->>QueryService: Return Documents
    QueryService->>LLMService: Generate Response
    API->>Client: Structured Response
```
