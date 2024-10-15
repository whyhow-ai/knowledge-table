import re
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import numpy as np
from langchain.schema import Document
from pydantic import BaseModel, Field

from knowledge_table_api.models.query import Rule, VectorResponse
from knowledge_table_api.services.llm import get_keywords
from knowledge_table_api.services.llm_service import LLMService


class Metadata(BaseModel, extra="forbid"):
    text: str
    page_number: int
    chunk_number: int
    document_id: str
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))


class VectorIndex(ABC):
    @abstractmethod
    async def upsert_vectors(
        self, document_id: str, chunks: List[Document], llm_service: LLMService
    ) -> Dict[str, str]:
        pass

    @abstractmethod
    async def vector_search(
        self, queries: List[str], document_id: str, llm_service: LLMService
    ) -> VectorResponse:
        pass

    @abstractmethod
    async def hybrid_search(
        self,
        query: str,
        document_id: str,
        rules: list[Rule],
        llm_service: LLMService,
    ) -> VectorResponse:
        pass

    @abstractmethod
    async def decomposed_search(
        self,
        query: str,
        document_id: str,
        rules: List[Rule],
        llm_service: LLMService,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def delete_document(
        self,
        document_id: str,
    ) -> Dict[str, str]:
        pass

    def prepare_chunks(
        self, document_id: str, chunks: List[Document], llm_service: LLMService
    ) -> List[Dict[str, Any]]:
        """Prepare chunks for insertion into the vector index."""

        cleaned_chunks = []
        for chunk in chunks:
            cleaned_chunks.append(
                re.sub("/(\r\n|\n|\r)/gm", "", chunk.page_content)
            )

        texts = [chunk.page_content for chunk in chunks]

        embeddings = llm_service.get_embeddings()

        embedded_chunks = [
            np.array(embeddings.embed_documents(texts)).tolist()
        ]

        datas = []

        for i, (chunk, embedding) in enumerate(
            zip(chunks, embedded_chunks[0])
        ):
            # Use the existing page number if available, otherwise calculate a pseudo-page number
            if "page" in chunk.metadata:
                page = chunk.metadata["page"] + 1
            else:
                # Create a pseudo-page number based on chunk index
                # Adjust this calculation as needed
                page = (i // 5) + 1  # Assuming 5 chunks per "page"

            metadata = Metadata(
                text=chunk.page_content,
                page_number=page,
                chunk_number=i,
                document_id=document_id,
            )
            data = {
                "id": metadata.uuid,
                "vector": embedding,
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
