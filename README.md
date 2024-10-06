
# Knowledge Table

**Knowledge Table** is an open-source package designed to simplify extracting and exploring structured data from unstructured documents. It enables the creation of structured knowledge representations, such as tables and graphs, using a natural language query interface. With customizable extraction rules, fine-tuned formatting options, and data traceability through provenance displayed in the UI, Knowledge Table is adaptable to various use cases.

Our goal is to provide a familiar, spreadsheet-like interface for business users, while offering a flexible and highly configurable backend for developers. This ensures seamless integration into existing RAG workflows, whether you’re processing a handful of files or exploring hundreds of documents.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/whyhow-ai/knowledge-table)](https://github.com/whyhow-ai/knowledge-table/issues)

For a limited demo, check out the [Knowledge Table Demo](https://knowledge-table-demo.whyhow.ai/).

To learn more about WhyHow and our projects, visit our [website](https://whyhow.ai/).

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

   ```sh
   pip install -r requirements.txt
   ```

5. **Start the backend:**

   ```sh
   cd src/
   python -m uvicorn knowledge_table_api.main:app
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

---

## Features

### Available in this repo:

- **Chunk Linking** - Link raw source text chunks to the answers for traceability and provenance.
- **Extract with natural language** - Use natural language queries to extract structured data from unstructured documents.
- **Customizable extraction rules** - Define rules to guide the extraction process and ensure data quality.
- **Custom formatting** - Control the output format of your extracted data.
- **Filtering** - Filter documents based on metadata or extracted data.
- **Exporting** - Download extracted data as CSV.
- **Chained extraction** - Reference previous columns in your extraction questions using brackets "What are the treatments for `{disease}`?".

### Coming soon:

- **Save to memory** - Save extracted data to a WhyHow knowledge graph.
- **Natural language querying** - Query over extracted data using natural language.
- **Query functions** - Activate custom functions such as aggregations, summaries, etc., using simple annotation like `#average`.

---

## Concepts

### Tables

Like a spreadsheet, a **table** is a collection of rows and columns that store structured data. Each row represents a **document**, and each column represents an **entity** that is extracted and formatted with a **question**.

### Documents

Each **document** is an unstructured data source (e.g., a contract, article, or report) uploaded to the Knowledge Table. When you upload a document, it is split into chunks, the chunks are embedded and tagged with metadata, and stored in a vector database.

### Question

A **Question** is the core mechanism for guiding extraction. It defines what data you want to extract from a document.

---

## Practical Usage

Once you've set up your questions, rules, and documents, the Knowledge Table processes the data and returns structured outputs based on your inputs. You may need to tweak the questions or adjust rule settings to fine-tune the extraction.

### Use Cases

- **Contract Management**: Extract key information such as party names, effective dates, and renewal dates.
- **Financial Reports**: Extract financial data from annual reports or earnings statements.
- **Compliance Monitoring**: Track clauses or regulations from legal documents.

---

## Extending the Project

Knowledge Table is built to be flexible and customizable, allowing you to extend it to fit your workflow:

- **Integrate with your own databases**.
- **Create custom questions and rules**.
- **Connect your models**.
- **Use custom embeddings**.
- **Scale for larger workloads**.

---

## Roadmap

- [ ] Support for more LLMs
  - [ ] Azure OpenAI
  - [ ] Llama3
  - [ ] GPT-4
  - [ ] Anthropic
- [ ] Support for more vector databases
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
