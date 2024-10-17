# Build stage
FROM python:3.12.1-slim-bookworm AS builder

# Set working directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --upgrade pip setuptools wheel

# Copy project files
COPY pyproject.toml ./
COPY src ./src

# Install project dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -e .

# Final stage
FROM python:3.12.1-slim-bookworm

# Create a non-root user
RUN useradd -m appuser

# Set working directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy wheels and install dependencies
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/src ./src
COPY pyproject.toml ./
RUN pip install --no-cache /wheels/*

# Install the project
RUN pip install -e .

# Change ownership of the app directory
RUN chown -R appuser:appuser /usr/src/app

# Switch to non-root user
USER appuser

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]