import logging
from typing import Any, Dict, List, Optional

import numpy as np
from dotenv import load_dotenv
from knowledge_table_api.models.query import Chunk, Rule, VectorResponse
from knowledge_table_api.services.llm import decompose_query, get_keywords
from knowledge_table_api.services.vector_index.base import VectorIndex
from langchain.schema import Document
from pydantic_settings import BaseSettings, SettingsConfigDict
from qdrant_client import QdrantClient, models

from backend.src.knowledge_table_api.dependencies import get_settings
from backend.src.knowledge_table_api.services.llm_service import LLMService

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="QDRANT_")

    location: Optional[str] = None
    url: Optional[str] = None
    port: Optional[int] = 6333
    grpc_port: int = 6334
    prefer_grpc: bool = False
    https: Optional[bool] = None
    api_key: Optional[str] = None
    prefix: Optional[str] = None
    timeout: Optional[int] = None
    host: Optional[str] = None
    path: Optional[str] = None


class QdrantIndex(VectorIndex):
    def __init__(self):
        settings = get_settings()
        self.collection_name = settings.index_name
        self.dimensions = settings.dimensions
        self.client = QdrantClient(**QdrantConfig().model_dump(exclude_none=True))
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.dimensions, distance=models.Distance.COSINE
                ),
            )

    async def upsert_vectors(
        self, document_id: str, chunks: List[Document], llm_service: LLMService
    ) -> Dict[str, str]:
        entries = self.prepare_chunks(document_id, chunks, llm_service)
        logger.info(f"Upserting {len(entries)} chunks")
        points = [
            models.PointStruct(
                id=entry.pop("id"), vector=entry.pop("vector"), payload=entry
            )
            for entry in entries
        ]
        self.client.upsert(self.collection_name, points=points, wait=True)
        return {"message": f"Successfully upserted {len(entries)} chunks."}

    async def vector_search(
        self, queries: List[str], document_id: str, llm_service: LLMService
    ) -> dict[str, Any]:
        logger.info(f"Retrieving vectors for {len(queries)} queries.")

        embeddings = llm_service.get_embeddings()

        final_chunks: List[Dict[str, Any]] = []

        for query in queries:
            logger.info("Generating embedding.")
            embedded_query = [np.array(embeddings.embed_query(query)).tolist()]
            logger.info("Searching...")

            query_response = self.client.query_points(
                self.collection_name,
                query=embedded_query,
                limit=40,
                with_payload=True,
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id),
                        )
                    ]
                ),
            ).points

            final_chunks.extend([point.payload for point in query_response])

        seen_chunks, formatted_output = set(), []

        for chunk in final_chunks:
            if chunk["chunk_number"] not in seen_chunks:
                seen_chunks.add(chunk["chunk_number"])
                formatted_output.append(
                    {"content": chunk["text"], "page": chunk["page_number"]}
                )

        logger.info(f"Retrieved {len(formatted_output)} unique chunks.")
        return VectorResponse(
            message="Query processed successfully.",
            chunks=[Chunk(**chunk) for chunk in formatted_output],
        )

    async def hybrid_search(
        self, query: str, document_id: str, rules: list[Rule], llm_service: LLMService
    ) -> VectorResponse:
        logger.info("Performing hybrid search.")

        embeddings = llm_service.get_embeddings()

        keywords = await self.extract_keywords(query, rules, llm_service)

        if keywords:
            like_conditions = [
                models.FieldCondition(key="text", match=models.MatchText(text=keyword))
                for keyword in keywords
            ]
            _filter = models.Filter(
                must=models.FieldCondition(
                    key="document_id", match=models.MatchValue(value=document_id)
                ),
                should=like_conditions,
            )

            logger.info("Running query with keyword filters.")
            keyword_response = self.client.query_points(
                collection_name=self.collection_name,
                filter=_filter,
                with_payload=True,
            ).points
            keyword_response = [point.payload for point in keyword_response]

            def count_keywords(text: str, keywords: List[str]) -> int:
                return sum(text.lower().count(keyword.lower()) for keyword in keywords)

            sorted_keyword_chunks = sorted(
                keyword_response,
                key=lambda chunk: count_keywords(chunk["text"], keywords or []),
                reverse=True,
            )

        embedded_query = [np.array(embeddings.embed_query(query)).tolist()]
        logger.info("Running semantic similarity search.")

        semantic_response = self.client.query_points(
            collection_name=self.collection_name,
            query=embedded_query,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id", match=models.MatchValue(value=document_id)
                    )
                ]
            ),
            limit=40,
            with_payload=True,
        ).points

        semantic_response = [point.payload for point in semantic_response]

        print(f"Found {len(semantic_response)} semantic chunks.")

        # Combine the top results from keyword and semantic searches
        combined_chunks = sorted_keyword_chunks[:20] + semantic_response

        # Sort the combined results by chunk number
        combined_sorted_chunks = sorted(
            combined_chunks, key=lambda chunk: chunk["chunk_number"]
        )

        # Optionally, for eact chunk, retrieve neighboring chunks to ensure full context is retrieved

        # Eliminate duplicate chunks
        seen_chunks = set()
        formatted_output = []

        for chunk in combined_sorted_chunks:
            if chunk["chunk_number"] not in seen_chunks:
                formatted_output.append(
                    {"content": chunk["text"], "page": chunk["page_number"]}
                )
                seen_chunks.add(chunk["chunk_number"])

        logger.info(f"Retrieved {len(formatted_output)} unique chunks.")

        return VectorResponse(
            message="Query processed successfully.",
            chunks=[Chunk(**chunk) for chunk in formatted_output],
        )

    # Decomposition query
    async def decomposed_search(
        self, query: str, document_id: str, rules: List[Rule], llm_service: LLMService
    ) -> Dict[str, Any]:
        logger.info("Decomposing query into smaller sub-queries.")
        decomposition_response = await decompose_query(query)
        sub_query_chunks = await self.vector_search(
            decomposition_response["sub-queries"], document_id, llm_service
        )
        return {
            "sub_queries": decomposition_response["sub-queries"],
            "chunks": sub_query_chunks["chunks"],
        }

    # Delete a document from the Qdrant
    async def delete_document(self, document_id: str) -> Dict[str, str]:
        self.client.delete(
            collection_name=self.collection_name,
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id", match=models.MatchValue(value=document_id)
                    )
                ]
            ),
            wait=True,
        )
        return {"message": "Successfully deleted document."}
