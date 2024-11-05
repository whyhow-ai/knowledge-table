# Testing

This guide covers how to run tests for the Knowledge Table project.

## Prerequisites

Ensure you have set up your development environment as described in the [Setup Guide](setup.md).

## Running Tests

We use pytest for our test suite. To run the tests, follow these steps:

**1. Activate your virtual environment** (if not already activated):

```sh
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

**2. Navigate to the backend directory**:

```sh
cd path/to/knowledge-table/backend
```

**3. Run the tests**:

```sh
pytest
```

This command will discover and run all tests in the project.

### Running Specific Tests

To run tests in a specific file:

```sh
pytest tests/path/to/test_file.py
```

To run a specific test function:

```sh
pytest tests/path/to/test_file.py::test_function_name
```

## Coverage

To run tests with coverage reporting:

**1. Install pytest-cov** (if not already installed):

```sh
pip install pytest-cov
```

**2. Run tests with coverage**:

```sh
pytest --cov=app tests/
```

This will run the tests and display a coverage report in the terminal.

**3. Generate an HTML coverage report**:

```sh
pytest --cov=app --cov-report=html tests/
```

This creates a `htmlcov` directory. Open `htmlcov/index.html` in a web browser to view the detailed coverage report.

## Writing Tests

When writing new tests:

1. Place test files in the `tests` directory.
2. Name test files with the prefix `test_`.
3. Name test functions with the prefix `test_`.
4. Use descriptive names for test functions to clearly indicate what they're testing.

Example:

```python
# tests/test_document_service.py

def test_upload_document_success():
    # Test code here
    pass

def test_upload_document_invalid_file():
    # Test code here
    pass
```

## Continuous Integration

We use GitHub Actions for continuous integration. The CI pipeline runs all tests automatically on every push and pull request.

To view the CI results:

1. Go to the GitHub repository.
2. Click on the "Actions" tab.
3. Select the workflow run you want to inspect.

## Troubleshooting

If you encounter any issues while running tests:

1. Ensure your virtual environment is activated and all dependencies are installed.
2. Check that your `.env` file is properly configured.
3. Verify that you're in the correct directory when running the tests.

If problems persist, please open an issue on the GitHub repository with details about the error you're encountering.
