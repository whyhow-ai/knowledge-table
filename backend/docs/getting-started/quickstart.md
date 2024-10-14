# Quickstart Guide

Welcome to the Knowledge Table Backend! This guide will walk you through the fastest way to get started with the backend, from installation to running your first API call.

## Prerequisites

Before you begin, make sure you have the following installed on your machine:

- **Python 3.10** or higher
- **Git**
- **Docker** (optional, if you want to use Docker for deployment)

## Step 1: Clone the Repository

Start by cloning the Knowledge Table repository from GitHub:

```bash
git clone https://github.com/whyhow-ai/knowledge-table.git
cd knowledge-table/backend
```

## Step 2: Set Up a Virtual Environment

We recommend setting up a Python virtual environment for managing dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

## Step 3: Install Dependencies

Next, install the required Python dependencies:

```bash
pip install -e .[dev,docs]
```

This command installs both the development and documentation dependencies.

## Step 4: Run the Application Locally

To run the FastAPI application locally, use the following command:

```bash
uvicorn src.main:app --reload
```

The API should now be running at http://127.0.0.1:8000.

## Step 5: Explore the API

Once the application is running, you can access the interactive API documentation:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Use these interfaces to try out API requests directly in your browser.

## Step 6: Running Unit Tests (Optional)

To ensure that everything is working correctly, you can run the unit tests:

```bash
pytest
```

You are now ready to explore the Knowledge Table backend. For more detailed instructions, refer to the Installation and Configuration guides.