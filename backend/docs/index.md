# Knowledge Table Backend Documentation

Welcome to the official documentation for the Knowledge Table backend. This site provides all the information you need to understand, install, and extend the backend of Knowledge Table.

## Overview

Knowledge Table is an open-source package designed to simplify extracting and exploring structured data from unstructured documents. This documentation covers the backend, which is powered by FastAPI and provides RESTful APIs for interacting with the system.

## Features

- Extract structured data using natural language queries
- Customizable extraction rules and formatting
- Support for various vector databases and LLMs
- Extensible architecture for adding new services
- Chunk linking for traceability and provenance
- Filtering based on metadata or extracted data
- Export data as CSV or graph triples
- Chained extraction using references to previous columns

## Key Components

- [Document Service](services/document_service.md): Handles document processing and storage
- [Graph Service](services/graph_service.md): Manages graph-related operations
- [LLM Service](services/llm_service.md): Interfaces with language models
- [Query Service](services/query_service.md): Processes various types of queries

## Data Models

- [Document Models](models/document.md): Represents document data
- [Graph Models](models/graph.md): Defines graph-related data structures
- [LLM Models](models/llm.md): Structures for LLM responses
- [Query Models](models/query.md): Represents query-related data

## API Schemas

- [Document Schemas](schemas/document.md): API schemas for document operations
- [Graph Schemas](schemas/graph.md): API schemas for graph operations
- [Query Schemas](schemas/query.md): API schemas for query operations

## Getting Started

To get started with the Knowledge Table backend:

1. [Installation Guide](getting-started/installation.md)
2. [Configuration](getting-started/configuration.md)

## Extending the Backend

Learn how to extend the backend:

- [Document Loaders](extending/document_loaders.md)
- [Integrating New LLMs](extending/llm_services.md)
- [Custom Vector Databases](extending/vector_databases.md)

## API Reference

For detailed API documentation, refer to the [API Reference](api/overview.md) section.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more information on how to get involved.

## Support

For support, join our [Discord community](https://discord.gg/PAgGMxfhKd) or contact us at team@whyhow.ai.