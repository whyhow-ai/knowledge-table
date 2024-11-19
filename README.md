# Knowledge Table

**Knowledge Table** is an open-source package designed to simplify extracting and exploring structured data from unstructured documents. It enables the creation of structured knowledge representations, such as tables and graphs, using a natural language query interface. With customizable extraction rules, fine-tuned formatting options, and data traceability through provenance displayed in the UI, Knowledge Table is adaptable to various use cases.

Our goal is to provide a familiar, spreadsheet-like interface for business users, while offering a flexible and highly configurable backend for developers. This ensures seamless integration into existing RAG workflows, whether you’re processing a handful of files or exploring hundreds of documents.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/whyhow-ai/knowledge-table)](https://github.com/whyhow-ai/knowledge-table/issues)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

For a limited demo, check out the [Knowledge Table Demo](https://knowledge-table-demo.whyhow.ai/).

https://github.com/user-attachments/assets/8e0e5cc6-6468-4bb5-888c-6b552e15b58a

Also check out the WhyHow [Knowledge Graph Studio](https://github.com/whyhow-ai/knowledge-graph-studio), an open source platform that makes it easy and intuitive to create and manage RAG-native knowledge graphs. To learn more about WhyHow and our projects, visit our [website](https://whyhow.ai/) and our [blog](https://medium.com/enterprise-rag).

## Table of Contents

- [Why Knowledge Table?](#why-knowledge-table)
- [Getting Started](#getting-started)
  - [Running from Docker](#running-from-docker)
  - [Running Natively](#running-natively)
  - [Environment Setup](#environment-setup)
- [Features](#features)
- [Concepts](#concepts)
  - [Tables](#tables)
  - [Documents](#documents)
  - [Question](#question)
- [Practical Usage](#practical-usage)
- [Extending the Project](#extending-the-project)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)
- [Screenshots](#screenshots)
- [Roadmap](#roadmap)

## Why Knowledge Table?

Better RAG systems depend on bringing structure to unstructured data, transforming it into formats like tables or graphs. WhyHow.AI develops tools that organize document content and metadata, and tools like Knowledge Table play a key role in this process. Its intuitive interface makes data easy to explore and manage for both technical and non-technical users.

As an open-source project, Knowledge Table is fully customizable to suit your needs. Whether you're integrating your own models, workflows, or extraction rules, its flexibility supports innovation and adapts to your specific requirements. By structuring the right data in the right format, Knowledge Table helps streamline your data extraction process, making it easier to unlock valuable insights from unstructured information.

---

## Getting Started

### Running from Docker

#### Prerequisites

- Docker
- Docker Compose

#### Starting the app

```sh
docker-compose up -d --build
```

#### Stopping the app

```sh
docker-compose down
```

#### Accessing the project

The frontend can be accessed at `http://localhost:3000`, and the backend can be accessed at `http://localhost:8000`.

---

### Running Natively

#### Prerequisites

- Python 3.10+
- Bun (for frontend)

#### Backend

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/knowledge-table.git
   ```

2. **Navigate to the backend directory:**

   ```sh
   cd knowledge-table/backend/
   ```

3. **Create and activate a virtual environment:**

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
   ```

4. **Install the dependencies:**

   For basic installation:

   ```sh
   pip install .
   ```

   For installation with development tools:

   ```sh
   pip install .[dev]
   ```

5. **Start the backend:**

   ```sh
   cd src/
   python -m uvicorn app.main:app
   ```

   The backend will be available at `http://localhost:8000`.

#### Frontend

1. **Navigate to the frontend directory:**

   ```sh
   cd ../frontend/
   ```

2. **Install Bun (if not already installed):**

   ```sh
   curl https://bun.sh/install | bash
   ```

3. **Install the dependencies:**

   ```sh
   bun install
   ```

4. **Start the frontend:**

   ```sh
   bun start
   ```

   The frontend will be available at `http://localhost:5173`.

---

### Environment Setup

1. Rename `.env.sample` to `.env`.
2. Add your OpenAI API key to the `.env` file.

> **Note:** This version of this project uses OpenAI as our initial provider, but the system is designed to be flexible and can be extended to support other AI providers. If you prefer a different provider, please create an issue, submit a PR, or check back soon for updates.

3. Configure the vector store in the `.env`. [Milvus](https://milvus.io) and [Qdrant](http://qdrant.tech) are the available as options.

---

## Development

To set up the project for development:

1. Clone the repository
2. Install the project with development dependencies:
   ```sh
   pip install .[dev]
   ```
3. Run tests:
   ```sh
   pytest
   ```
4. Run linters:
   ```sh
   flake8
   black .
   isort .
   ```

---

## Features

### Available in this repo:

- **Chunk Linking** - Link raw source text chunks to the answers for traceability and provenance.
- **Extract with natural language** - Use natural language queries to extract structured data from unstructured documents.
- **Customizable extraction rules** - Define rules to guide the extraction process and ensure data quality.
- **Custom formatting** - Control the output format of your extracted data. Knowledge table current supports text, list of text, number, list of numbers, and boolean formats.
- **Filtering** - Filter documents based on metadata or extracted data.
- **Exporting as CSV or Triples** - Download extracted data as CSV or graph triples.
- **Chained extraction** - Reference previous columns in your extraction questions using @ i.e. "What are the treatments for `@disease`?".
- **Split Cell Into Rows** - Turn outputs within a single cell from List of Numbers or List of Values and split it into individual rows to do more complex Chained Extraction

---

## Concepts

### Tables

Like a spreadsheet, a **table** is a collection of rows and columns that store structured data. Each row represents a **document**, and each column represents an **entity** that is extracted and formatted with a **question**.

### Documents

Each **document** is an unstructured data source (e.g., a contract, article, or report) uploaded to the Knowledge Table. When you upload a document, it is split into chunks, the chunks are embedded and tagged with metadata, and stored in a vector database.

### Question

A **Question** is the core mechanism for guiding extraction. It defines what data you want to extract from a document.

### Rule

A **Rule** guides the extraction from the LLM. You can add rules on a column level or on a global level. Currently, the following rule types are supported:

- **May Return** rules give the LLM examples of answers that can be used to guide the extraction. This is a great way to give more guidance for the LLM on the type of things it should keep an eye out for.
- **Must Return** rules give the LLM an exhaustive list of answers that are allowed to be returned. This is a great way to give guardrails for the LLM to ensure only certain terms are returned.
- **Allowed # of Responses** rules are useful for provide guardrails in the event there are may be a range of potential ‘grey-area’ answers and we want to only restrict and guarantee only a certain number of the top responses are provided.
- **Resolve Entity** rules allow you to resolve values to a specific entity. This is useful for ensuring output conforms to a specific entity type. For example, you can write rules that ensure "blackrock", "Blackrock, Inc.", and "Blackrock Corporation" all resolve to the same entity - "Blackrock".

---

## Practical Usage

Once you've set up your questions, rules, and documents, the Knowledge Table processes the data and returns structured outputs based on your inputs. You may need to tweak the questions or adjust rule settings to fine-tune the extraction.

### Use Cases

- **Contract Management**: Extract key information such as party names, effective dates, and renewal dates.
- **Financial Reports**: Extract financial data from annual reports or earnings statements.
- **Research Extraction**: Extract information with key questions of a range of research reports
- **Metadata Generation**: Classify and tag information about your documents and files by running targeted questions against the files (i.e. "What project is this email thread about?")

---

## Export to Triples

To create the Schema for the Triples, we use an LLM to consider the Entity Type of the Column, the question that was used to generate the cells, and the values themselves, to create the schema and the triples. The document name is inserted as a node property. The vector chunk ids are also included in the JSON file of the triples, and tied to the triples created.

---

## Rules

We now have 3 types of [Rules](https://medium.com/enterprise-rag/rules-extraction-guardrails-knowledge-table-studio-e84999ade353) you can now incorporate within your processes, which are:

- **Entity Resolution Rules**: Resolving discrepencies between Entities or imposing a common terminology on top of Entities

- **Entity Extraction Rules**: Imposing Guardrails and Context for the Entities that should be detected and returned across Documents

- **Entity Relationship Rules**: Imposing Guardrails on the types of Patterns that should be returned on the Relationships between the extracted Entities

---

## Extending the Project

Knowledge Table is built to be flexible and customizable, allowing you to extend it to fit your workflow:

- **Integrate with your own databases**.
- **Create custom questions and rules**.
- **Connect your models**.
- **Use custom embeddings**.
- **Scale for larger workloads**.

---

## Optional Integrations

### Unstructured API

Knowledge Table offers optional integration with the Unstructured API for enhanced document processing capabilities. This integration allows for more advanced parsing and extraction from various document types.

To use the Unstructured API integration:

1. Sign up for an API key at [Unstructured.io](https://www.unstructured.io/).
2. Set the `UNSTRUCTURED_API_KEY` environment variable in the `.env` file, or with your API key:
   ```
   export UNSTRUCTURED_API_KEY=your_api_key_here
   ```
3. Install the project with Unstructured support:
   ```
   pip install .[unstructured]
   ```

When the `UNSTRUCTURED_API_KEY` is set, Knowledge Table will automatically use the Unstructured API for document processing. If the key is not set or if there's an issue with the Unstructured API, the system will fall back to the default document loaders.

## Note: Usage of the Unstructured API may incur costs based on your plan with Unstructured.io.

## Roadmap

- [x] Expansion of Rules System
  - [x] Upload Extraction Rules via CSV
  - [x] Entity Resolution Rules
  - [x] Rules Dashboard
  - [x] Rules Log
- [ ] Support for more LLMs
  - [ ] Azure OpenAI
  - [ ] Llama3
  - [ ] GPT-4
  - [ ] Anthropic
- [ ] Support for more vector databases
  - [x] Milvus
  - [x] Qdrant
  - [ ] Weaviate
  - [ ] Chroma
  - [ ] Pinecone
- [ ] Backend data stores
  - [ ] PostgreSQL
  - [ ] MongoDB
  - [ ] MySQL
  - [ ] Redis
- [ ] Other
  - [ ] Deployment scripts to cloud

---

## Contributing

We welcome contributions to improve the Knowledge Table. If you have any ideas, bug reports, or feature requests, please open an issue on the GitHub repository.

### How to Contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your forked repository.
5. Open a pull request to the main repository.

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## Support

WhyHow.AI is building tools to help developers bring more determinism and control to their RAG pipelines using graph structures. If you're incorporating knowledge graphs in RAG, we’d love to chat at team@whyhow.ai, or follow our newsletter at [WhyHow.AI](https://www.whyhow.ai/). Join our discussions on our [Discord](https://discord.com/invite/9bWqrsxgHr).

---

## Backlog

- [ ] Support for custom embeddings.
- [ ] Backend storage for extracted data.

---

## Roadmap

Here's what’s coming soon:

- [ ] More LLM integrations.
- [ ] Memory storage options.
