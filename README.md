# Knowledge Table

**Knowledge Table** is an open-source package designed to simplify extracting and exploring structured data from unstructured documents. It enables the creation of structured knowledge representations, such as tables and graphs, using a natural language query interface. With customizable extraction rules, fine-tuned formatting options, and data traceability through provenance displayed in the UI, Knowledge Table is adaptable to various use cases.

Our goal is to provide a familiar, spreadsheet-like interface for business users, while offering a flexible and highly configurable backend for developers. This ensures seamless integration into existing RAG workflows, whether you're processing a handful of files or exploring hundreds of documents.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/whyhow-ai/knowledge-table)](https://github.com/whyhow-ai/knowledge-table/issues)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

For a limited demo, check out the [Knowledge Table Demo](https://knowledge-table-demo.whyhow.ai/).

https://github.com/user-attachments/assets/0129ea64-173b-461b-a525-5d870a1e2f41

To learn more about WhyHow and our projects, visit our [website](https://whyhow.ai/).

## Table of Contents

- [Why Knowledge Table?](#why-knowledge-table)
- [Features](#features)
- [Documentation](#documentation)
- [Getting Started](#getting-started)
- [Concepts](#concepts)
- [Practical Usage](#practical-usage)
- [Architecture](#architecture)
- [Extending the Project](#extending-the-project)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)
- [Future Plans](#future-plans)

## Why Knowledge Table?

Better RAG systems depend on bringing structure to unstructured data, transforming it into formats like tables or graphs. WhyHow.AI develops tools that organize document content and metadata, and tools like Knowledge Table play a key role in this process. Its intuitive interface makes data easy to explore and manage for both technical and non-technical users.

As an open-source project, Knowledge Table is fully customizable to suit your needs. Whether you're integrating your own models, workflows, or extraction rules, its flexibility supports innovation and adapts to your specific requirements. By structuring the right data in the right format, Knowledge Table helps streamline your data extraction process, making it easier to unlock valuable insights from unstructured information.

## Features

- **Document Processing**: Upload and process various document types
- **Graph Operations**: Create and manage knowledge graphs from extracted data
- **LLM Integration**: Utilize language models for intelligent data extraction
- **Query Processing**: Support for vector, hybrid, and decomposed queries
- **Customizable Extraction Rules**: Define rules to guide the extraction process
- **Data Export**: Export extracted data as CSV or graph triples
- **Chunk Linking**: Link raw source text chunks to answers for traceability
- **Chained Extraction**: Reference previous columns in extraction questions

## Documentation

Detailed documentation for the Knowledge Table backend is now available. It covers:

- API reference
- Data models and schemas
- Key components and services
- Getting started guides
- Extension guides

You can find the full documentation [here](link-to-your-documentation).

## Getting Started

Knowledge Table can be run using Docker or natively. For detailed installation and setup instructions, please refer to our [Getting Started Guide](https://whyhow-ai.github.io/knowledge-table/).

### Quick Start with Docker

```sh
docker-compose up -d --build
```


The frontend will be available at `http://localhost:3000`, and the backend at `http://localhost:8000`.

### Environment Setup

1. Rename `.env.sample` to `.env`.
2. Add your OpenAI API key to the `.env` file.

For more detailed setup instructions and configuration options, please see our [documentation](https://whyhow-ai.github.io/knowledge-table/).

## Concepts

### Tables

Like a spreadsheet, a **table** is a collection of rows and columns that store structured data. Each row represents a **document**, and each column represents an **entity** that is extracted and formatted with a **question**.

### Documents

Each **document** is an unstructured data source (e.g., a contract, article, or report) uploaded to the Knowledge Table. When you upload a document, it is split into chunks, the chunks are embedded and tagged with metadata, and stored in a vector database.

### Question

A **Question** is the core mechanism for guiding extraction. It defines what data you want to extract from a document.

## Practical Usage

Once you've set up your questions, rules, and documents, the Knowledge Table processes the data and returns structured outputs based on your inputs. You may need to tweak the questions or adjust rule settings to fine-tune the extraction.

### Use Cases

- **Contract Management**: Extract key information such as party names, effective dates, and renewal dates.
- **Financial Reports**: Extract financial data from annual reports or earnings statements.
- **Research Extraction**: Extract information with key questions of a range of research reports
- **Metadata Generation**: Classify and tag information about your documents and files by running targeted questions against the files (i.e. "What project is this email thread about?")

## Architecture

Knowledge Table's backend is built with a modular architecture, consisting of:

- Document Service: Handles document processing and storage
- Graph Service: Manages graph-related operations
- LLM Service: Interfaces with language models
- Query Service: Processes various types of queries

This modular design allows for easy extension and customization of the system.

## Extending the Project

Knowledge Table is designed to be flexible and extensible. You can:

- Integrate new vector databases
- Add support for different LLMs
- Implement custom document processing pipelines
- Extend the graph operations
- Customize query processing

For detailed guides on extending the project, refer to our [documentation](https://whyhow-ai.github.io/knowledge-table/).

## Contributing

We welcome contributions to improve Knowledge Table. Before contributing, please:

1. Check our [documentation](https://whyhow-ai.github.io/knowledge-table/) for detailed information about the project structure.
2. Review our [contributing guidelines](CONTRIBUTING.md).
3. Open an issue to discuss major changes before submitting a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Support

WhyHow.AI is building tools to help developers bring more determinism and control to their RAG pipelines using graph structures. If you're incorporating knowledge graphs in RAG, we'd love to chat at team@whyhow.ai, or follow our newsletter at [WhyHow.AI](https://www.whyhow.ai/). Join our discussions on our [Discord](https://discord.com/invite/9bWqrsxgHr).

## Future Plans

- Support for more LLMs (Azure OpenAI, Ollama, VertexAI)
- Integration with additional vector databases (Weaviate, Chroma, Qdrant)
- Backend data stores (PostgreSQL, MongoDB, Redis)
- Deployment scripts for cloud environments
- Support for custom embeddings
- Enhanced memory storage options
