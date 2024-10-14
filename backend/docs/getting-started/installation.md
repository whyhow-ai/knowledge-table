# Installation Guide

This guide will help you set up the Knowledge Table backend.

## Prerequisites

- Python 3.10+
- Git

## Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/whyhow-ai/knowledge-table.git
   cd knowledge-table/backend/
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies**

   ```bash
   pip install .
   ```

4. **Install development dependencies (optional)**

   ```bash
   pip install .[dev]
   ```

5. **Start the backend server**

   ```bash
   uvicorn app.main:app --reload
   ```

   The backend API will be available at `http://localhost:8000`.

[Next: Configuration](configuration.md)