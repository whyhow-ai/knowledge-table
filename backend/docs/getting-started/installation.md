# 🚀 Installation Guide

This guide will walk you through setting up and running the Knowledge Table backend and frontend.

> **Prerequisites**
>
> - Python 3.10+
> - Git
> - [Bun](https://bun.sh/) (for frontend)

---

## Setup and Run

### Backend

> **Step 1:** Clone the Knowledge Table repository

```bash
git clone https://github.com/whyhow-ai/knowledge-table.git
cd knowledge-table/backend/
```

> **Step 2:** Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

> **Step 3:** Install the necessary packages

```bash
pip install .
```

_To install additional development dependencies:_

```bash
pip install .[dev]
```

> **Step 4:** Launch the backend server

```bash
uvicorn app.main:app --reload
```

**API** available at: [http://localhost:8000](http://localhost:8000)

---

### Frontend

> **Step 1:** Navigate to the frontend directory and install dependencies

```bash
cd ../frontend
bun install
```

> **Step 2:** Start the frontend

```bash
bun start
```

**Frontend** available at: [http://localhost:5173](http://localhost:5173)

---

## Configuration

The backend uses environment variables for configuration.

> **Create a `.env` file**

```bash
cp .env.sample .env
```

> **Add API keys**

Open `.env` and set up your OpenAI API key:

```dotenv
OPENAI_API_KEY=sk-yourkeyhere
```

_Optional: Add the Unstructured API key:_

```dotenv
UNSTRUCTURED_API_KEY=your-unstructured-api-key
```

| Variable               | Description                            |
| ---------------------- | -------------------------------------- |
| `OPENAI_API_KEY`       | Your OpenAI API key                    |
| `UNSTRUCTURED_API_KEY` | API key for Unstructured.io (optional) |

---

## Explore the API

Once the application is running, you can access the interactive API documentation:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Use these interfaces to try out API requests directly in your browser.

---

## Run Tests

To ensure that everything is working correctly, you can run the unit tests:

```bash
pytest
```

---

🎉 **Your Knowledge Table backend and frontend setup is now complete!**
