# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
