# pull official base image
FROM python:3.12.1-slim-bookworm

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies
RUN pip install --upgrade pip
RUN pip install setuptools wheel

# copy pyproject.toml and setup files
COPY pyproject.toml ./
COPY src ./src

# install project in editable mode
RUN pip install -e .

# run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]