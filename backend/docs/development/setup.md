# Development Setup

This guide will help you set up your development environment for Knowledge Table.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10+
- Git
- Bun (for frontend development)

## Backend Setup

1. **Clone the Repository**

   ```sh
   git clone https://github.com/yourusername/knowledge-table.git
   cd knowledge-table/backend
   ```

2. **Create and Activate a Virtual Environment**

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Development Dependencies**

   ```sh
   pip install .[dev]
   ```

   This command installs the project along with all development dependencies.

4. **Set Up Environment Variables**

   Copy the sample environment file and edit it with your settings:

   ```sh
   cp .env.sample .env
   ```

   Open `.env` in a text editor and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_api_key_here
   ```

5. **Install Pre-commit Hooks** (Optional but recommended)

   ```sh
   pre-commit install
   ```

   This sets up git hooks to automatically run linters and formatters before each commit.

## Frontend Setup

1. **Navigate to the Frontend Directory**

   ```sh
   cd ../frontend
   ```

2. **Install Bun** (if not already installed)

   ```sh
   curl https://bun.sh/install | bash
   ```

3. **Install Frontend Dependencies**

   ```sh
   bun install
   ```

## Running the Application

### Backend

From the `backend/src` directory:

```sh
python -m uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`.

### Frontend

From the `frontend` directory:

```sh
bun start
```

The frontend will be available at `http://localhost:5173`.

## Code Style and Linting

We use the following tools to maintain code quality:

- Black for code formatting
- Flake8 for linting
- isort for import sorting

To run these tools:

```sh
black .
flake8
isort .
```

## Next Steps

- Familiarize yourself with the project structure.
- Read through the API documentation.
- Check out the [Contributing](../CONTRIBUTING.md) for information on how to contribute to the project.

If you encounter any issues during setup, please refer to our troubleshooting guide or open an issue on the GitHub repository.