"""The base class for the vector database services."""

import logging
import re
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

from langchain.schema import Document
from pydantic import BaseModel, Field

from app.models.query_core import Rule
from app.schemas.query_api import VectorResponseSchema
from app.services.embedding.base import EmbeddingService
from app.services.llm.base import CompletionService
from app.services.llm_service import get_keywords

logger = logging.getLogger(__name__)


class Metadata(BaseModel, extra="forbid"):
    """Metadata stored in vector storage."""

    text: str
    page_number: int
    chunk_number: int
    document_id: str
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))


class VectorDBService(ABC):
    """The base class for the vector database services."""

    embedding_service: EmbeddingService

    @abstractmethod
    async def upsert_vectors(
        self, vectors: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Upsert the vectors into the vector database."""
        pass

    @abstractmethod
    async def vector_search(
        self, queries: List[str], document_id: str
    ) -> VectorResponseSchema:
        """Perform a vector search."""
        pass

    # Update other methods if they also return VectorResponse
    @abstractmethod
    async def keyword_search(
        self, query: str, document_id: str, keywords: List[str]
    ) -> VectorResponseSchema:
        """Perform a keyword search."""
        pass

    @abstractmethod
    async def hybrid_search(
        self, query: str, document_id: str, rules: List[Rule]
    ) -> VectorResponseSchema:
        """Perform a hybrid search."""
        pass

    @abstractmethod
    async def decomposed_search(
        self, query: str, document_id: str, rules: List[Rule]
    ) -> Dict[str, Any]:
        """Decomposition query."""
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> Dict[str, str]:
        """Delete the document from the vector database."""
        pass

    @abstractmethod
    async def ensure_collection_exists(self) -> None:
        """Ensure the collection exists in the vector database."""
        pass

    async def get_embeddings(
        self, texts: Union[str, List[str]]
    ) -> List[List[float]]:
        """Get embeddings for the given text(s) using the embedding service."""
        if isinstance(texts, str):
            texts = [texts]
        return await self.embedding_service.get_embeddings(texts)

    async def get_single_embedding(self, text: str) -> List[float]:
        """Get a single embedding for the given text."""
        embeddings = await self.get_embeddings(text)
        return embeddings[0]

    async def prepare_chunks(
        self, document_id: str, chunks: List[Document]
    ) -> List[Dict[str, Any]]:
        """Prepare chunks for insertion into the vector database."""
        logger.info(f"Preparing {len(chunks)} chunks")

        # Clean the chunks
        cleaned_texts = [
            re.sub(r"\s+", " ", chunk.page_content.strip()) for chunk in chunks
        ]

        logger.info("Generating embeddings.")

        # Embed all chunks at once
        embedded_chunks = await self.get_embeddings(cleaned_texts)

        # Prepare the data for insertion
        return [
            {
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "text": text,
                "page_number": chunk.metadata.get("page", i // 5 + 1),
                "chunk_number": i,
                "document_id": document_id,
            }
            for i, (chunk, text, embedding) in enumerate(
                zip(chunks, cleaned_texts, embedded_chunks)
            )
        ]

    async def extract_keywords(
        self, query: str, rules: list[Rule], llm_service: CompletionService
    ) -> list[str]:
        """Extract keywords from a user query."""
        keywords = []
        if rules:
            for rule in rules:
                if rule.type in ["must_return", "may_return"]:
                    if rule.options:
                        if isinstance(rule.options, list):
                            keywords.extend(rule.options)
                        elif isinstance(rule.options, dict):
                            for value in rule.options.values():
                                if isinstance(value, list):
                                    keywords.extend(value)
                                elif isinstance(value, str):
                                    keywords.append(value)

        if not keywords:
            extracted_keywords = await get_keywords(llm_service, query)
            if extracted_keywords and isinstance(extracted_keywords, list):
                keywords = extracted_keywords

        return keywords
