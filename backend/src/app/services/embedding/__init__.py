"""Embedding service module."""

from app.services.embedding.base import EmbeddingService
from app.services.embedding.factory import EmbeddingServiceFactory

__all__ = ["EmbeddingService", "EmbeddingServiceFactory"]
