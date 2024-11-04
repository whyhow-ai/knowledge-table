# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.1.6] - 2024-11-04

### Added

- Added support for queries without source data in vector database
- Graceful failure of triple export when no chunks are found
- Tested Qdrant vector database service
- Added resolve entity rule

### Changed

- Separated embedding service from LLM service

## [v0.1.5] - 2024-10-29

### Changed

- Updating backend to work with new UI
- Tweaked query output for separating answers and chunks
- Support for [Qdrant](https://qdrant.tech/) vector database.
- Updated Milvus reference in the factory to be more robust to other Milvus datastores

### Improved

- Updating testing to Mock OpenAI client and embeddings

## [v0.1.4] - 2024-10-16

### Improved

- Refactored add question, add document
- Refactored csv download and export triple components
- Refactored factories for depedency injection

### Added

- Added react mentions + coloring logic to highlight mentioned columns

### Changed

- Added document to node properties when exporting triples
- Streamlined testing to remove complication and restriciton

## [v0.1.3] - 2024-10-13

### Changed

- Restructured project directory for improved organization and scalability
- Moved router files to new `api/v1/endpoints` directory
- Created new `core` directory for fundamental application components
- Updated llm operations to new services in `services/llm`
- Updated vector database operations to new services in `services/vector_db`
- Updated tests to new directory structure

### Improved

- Separated configuration from dependency injection for better maintainability and clarity
- Created new `utils` directory for fundamental application components
- Seperated Pydantic models into `models` and `schemas` directories
- Massively uncomplicated the test files

## [v0.1.2] - 2024-10-10

### Added

- Integrated Instructor library for enhanced LLM response handling
- New prompt templates for improved query decomposition and keyword extraction
- Implemented LLMService abstract base class for decoupling LLM operations
- Created OpenAIService as a concrete implementation of LLMService
- Added LLMFactory for creating LLM service instances

### Changed

- Modified `generate_triples` function to skip creation of triples with empty head or tail values
- Updated `triple_to_dict` function to potentially return `None` for invalid triples
- Refactored dependency management in vector and query services
- Removed FastAPI Depends usage from utility functions in vector.py
- Implemented direct calls to get_milvus_client(), get_settings(), and get_embeddings()
- Updated hybrid_search, vector_search, and other related functions
- Modified LLM service to use Instructor for structured outputs
- Updated query processing to leverage new prompt templates
- Refactored vector operations to use the new LLMService abstraction
- Updated document processing pipeline to work with the decoupled LLM service
- Modified dependency injection to include LLM service creation
- Adjusted query processing to utilize the new LLM service structure

### Improved

- Enhanced reliability and maintainability of vector and query services
- Optimized query processing in query.py to align with new dependency approach
- Improved structured output handling in LLM responses
- Enhanced flexibility by allowing easy switching between different LLM providers
- Improved testability of LLM-dependent components through abstraction

### Fixed

- Prevented creation and return of triples with empty string values for head or tail
- Resolved issues related to incorrect usage of FastAPI's Depends in non-route functions
- Ensured more predictable behavior in data access and query processing operations
- Resolved issues related to direct OpenAI client usage in vector operations
- Addressed errors in document upload process due to LLM service changes

## [0.1.1] - 2024-10-08

### Added

- Added git workflows
- Added issue templates
- Integrated Unstructured API for enhanced document processing
- Optional dependency groups in pyproject.toml for flexible installation
- New `unstructured_loader` function for processing documents with Unstructured API
- Error handling for Unstructured API import and usage

### Changed

- Updated `upload_document` function to use Unstructured API when available
- Modified project structure to support optional Unstructured integration
- Updated installation instructions in README to reflect new dependency options

### Fixed

- Fixed issues for mypy, flake8, isort, black
- Improved error handling in document processing pipeline

## [0.1.0]

### Added

- Initial release

### Changed
