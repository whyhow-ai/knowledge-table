"""The base class for the vector database services."""

import asyncio
import re
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

import numpy as np
from langchain.schema import Document
from pydantic import BaseModel, Field

from app.models.query import Rule
from app.schemas.query import VectorResponse
from app.services.llm.base import LLMService
from app.services.llm_service import get_keywords


class Metadata(BaseModel, extra="forbid"):
    """Metadata stored in vector storage."""

    text: str
    page_number: int
    chunk_number: int
    document_id: str
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))


class VectorDBService(ABC):
    """The base class for the vector database services."""

    llm_service: LLMService

    @abstractmethod
    async def upsert_vectors(
        self, vectors: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Upsert the vectors into the vector database."""
        pass

    @abstractmethod
    async def vector_search(
        self, queries: List[str], document_id: str
    ) -> VectorResponse:
        """Perform a vector search."""
        pass

    # Update other methods if they also return VectorResponse
    @abstractmethod
    async def keyword_search(
        self, query: str, document_id: str, keywords: List[str]
    ) -> VectorResponse:
        """Perform a keyword search."""
        pass

    @abstractmethod
    async def hybrid_search(
        self, query: str, document_id: str, rules: List[Rule]
    ) -> VectorResponse:
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
        self, text: Union[str, List[str]]
    ) -> Union[List[float], List[List[float]]]:
        """Get embeddings for the given text using the LLM service."""
        if isinstance(text, str):
            return await self.llm_service.get_embeddings(text)
        else:
            tasks = [self.llm_service.get_embeddings(t) for t in text]
            return await asyncio.gather(*tasks)

    async def prepare_chunks(
        self, document_id: str, chunks: List[Document]
    ) -> List[Dict[str, Any]]:
        """Prepare chunks for insertion into the vector index."""

        # Clean the chunks
        cleaned_chunks = []
        for chunk in chunks:
            cleaned_chunks.append(
                re.sub("/(\r\n|\n|\r)/gm", "", chunk.page_content)
            )

        # Embed all chunks at once
        texts = [chunk.page_content for chunk in chunks]
        embedded_chunks = await self.get_embeddings(texts)

        # Prepare the data for insertion
        datas = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embedded_chunks)):
            # Get the page number
            if "page" in chunk.metadata:
                page = chunk.metadata["page"] + 1
            else:
                page = (i // 5) + 1  # Assuming 5 chunks per "page"

            # Create the metadata
            metadata = Metadata(
                text=chunk.page_content,
                page_number=page,
                chunk_number=i,
                document_id=document_id,
            )

            # Create the data
            data = {
                "id": metadata.uuid,
                "vector": embedding,  # This should now be a list of floats
                "text": metadata.text,
                "page_number": metadata.page_number,
                "chunk_number": metadata.chunk_number,
                "document_id": metadata.document_id,
            }

            datas.append(data)

        return datas

    async def extract_keywords(
        self, query: str, rules: list[Rule], llm_service: LLMService
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
