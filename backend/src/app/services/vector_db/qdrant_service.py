"""Vector index implementation using Qdrant."""

# mypy: disable-error-code="index"

import logging
import uuid
from typing import Any, Dict, List, Sequence

import numpy as np
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient, models

from app.core.config import Settings
from app.models.query_core import Chunk, Rule
from app.schemas.query_api import VectorResponseSchema
from app.services.llm_service import LLMService
from app.services.vector_db.base import VectorDBService

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantMetadata(BaseModel, extra="forbid"):
    """Metadata for Qdrant documents."""

    text: str
    page_number: int
    chunk_number: int
    document_id: str
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))


class QdrantService(VectorDBService):
    """Vector service implementation using Qdrant."""

    def __init__(self, llm_service: LLMService, settings: Settings):
        self.settings = settings
        self.llm_service = llm_service
        self.collection_name = settings.index_name
        self.dimensions = settings.dimensions
        qdrant_config = settings.qdrant.model_dump(exclude_none=True)
        self.client = QdrantClient(**qdrant_config)

    async def ensure_collection_exists(self) -> None:
        """Ensure the Qdrant collection exists."""
        if not self.client.collection_exists(self.collection_name):
            logger.info(f"Creating collection {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.dimensions, distance=models.Distance.COSINE
                ),
            )
            logger.info(f"Collection {self.collection_name} created")
        else:
            logger.info(f"Collection {self.collection_name} already exists")
            # Optionally, retrieve and log the collection info
            collection_info = self.client.get_collection(self.collection_name)
            logger.info(f"Collection info: {collection_info}")

    async def upsert_vectors(
        self, vectors: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Upsert vectors into the Qdrant collection."""
        logger.info(f"Upserting {len(vectors)} chunks")
        await self.ensure_collection_exists()
        points = [
            models.PointStruct(
                id=entry.pop("id"), vector=entry.pop("vector"), payload=entry
            )
            for entry in vectors
        ]
        try:
            self.client.upsert(self.collection_name, points=points, wait=True)
            logger.info("Upsert successful")
        except Exception as e:
            logger.error(f"Error during upsert: {str(e)}")
            raise
        return {"message": f"Successfully upserted {len(vectors)} chunks."}

    async def vector_search(
        self, queries: List[str], document_id: str
    ) -> VectorResponseSchema:
        """Perform a vector search on the Qdrant collection."""
        logger.info(f"Retrieving vectors for {len(queries)} queries.")

        final_chunks: List[Dict[str, Any]] = []

        for query in queries:
            logger.info(f"Processing query: {query}")
            embedded_queries = await self.get_embeddings(query)

            # We expect a single embedding for a single query
            embedded_query = embedded_queries[0]

            # Ensure embedded_query is a flat list of floats
            if isinstance(embedded_query, np.ndarray):
                embedded_query = embedded_query.flatten().tolist()

            logger.debug(
                f"Embedded query type: {type(embedded_query)}, length: {len(embedded_query)}"
            )

            try:
                query_response = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=embedded_query,
                    limit=40,
                    query_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document_id",
                                match=models.MatchValue(value=document_id),
                            )
                        ]
                    ),
                )
                logger.info(
                    f"Search completed. Number of results: {len(query_response)}"
                )

                final_chunks.extend(
                    [
                        point.payload
                        for point in query_response
                        if point.payload
                    ]
                )
            except Exception as e:
                logger.error(f"Error during search: {str(e)}", exc_info=True)
                raise

        return self._format_response(final_chunks)

    def _format_response(
        self, chunks: List[Dict[str, Any]]
    ) -> VectorResponseSchema:
        """Format the response from the Qdrant collection."""
        seen_chunks = set()
        formatted_output = []

        for chunk in chunks:
            if chunk["chunk_number"] not in seen_chunks:
                seen_chunks.add(chunk["chunk_number"])
                formatted_output.append(
                    {"content": chunk["text"], "page": chunk["page_number"]}
                )

        logger.info(f"Retrieved {len(formatted_output)} unique chunks.")
        return VectorResponseSchema(
            message="Query processed successfully.",
            chunks=[Chunk(**chunk) for chunk in formatted_output],
        )

    async def hybrid_search(
        self,
        query: str,
        document_id: str,
        rules: list[Rule],
    ) -> VectorResponseSchema:
        """Perform a hybrid search on the Qdrant collection."""
        logger.info("Performing hybrid search.")

        sorted_keyword_chunks = []
        keywords = await self.extract_keywords(query, rules, self.llm_service)

        if keywords:
            like_conditions: Sequence[models.FieldCondition] = [
                models.FieldCondition(
                    key="text", match=models.MatchText(text=keyword)
                )
                for keyword in keywords
            ]
            _filter = models.Filter(
                must=models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id),
                ),
                should=like_conditions,  # type: ignore
            )

            logger.info("Running query with keyword filters.")
            keyword_response = self.client.query_points(
                collection_name=self.collection_name,
                query_filter=_filter,
                with_payload=True,
            ).points
            keyword_response = [
                point.payload for point in keyword_response if point.payload  # type: ignore
            ]

            def count_keywords(text: str, keywords: List[str]) -> int:
                return sum(
                    text.lower().count(keyword.lower()) for keyword in keywords
                )

            sorted_keyword_chunks = sorted(
                keyword_response,
                key=lambda chunk: count_keywords(
                    chunk["text"], keywords or []
                ),
                reverse=True,
            )

        embedded_query = await self.get_embeddings(query)
        logger.info("Running semantic similarity search.")

        semantic_response = self.client.query_points(
            collection_name=self.collection_name,
            query=embedded_query,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            ),
            limit=40,
            with_payload=True,
        ).points

        semantic_response = [
            point.payload for point in semantic_response if point.payload  # type: ignore
        ]

        print(f"Found {len(semantic_response)} semantic chunks.")

        # Combine the top results from keyword and semantic searches
        combined_chunks = sorted_keyword_chunks[:20] + semantic_response

        # Sort the combined results by chunk number
        combined_sorted_chunks = sorted(
            combined_chunks, key=lambda chunk: chunk["chunk_number"]
        )

        # Optionally, for each chunk, retrieve neighbouring chunks to ensure full context is retrieved

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

        return VectorResponseSchema(
            message="Query processed successfully.",
            chunks=[Chunk(**chunk) for chunk in formatted_output],
        )

    # Decomposition query
    async def decomposed_search(
        self,
        query: str,
        document_id: str,
        rules: List[Rule],
    ) -> Dict[str, Any]:
        """Perform a decomposed search on a Qdrant collection."""
        logger.info("Decomposing query into smaller sub-queries.")
        decomposition_response = await self.llm_service.decompose_query(query)
        sub_query_chunks = await self.vector_search(
            decomposition_response["sub-queries"], document_id
        )
        return {
            "sub_queries": decomposition_response["sub-queries"],
            "chunks": sub_query_chunks.chunks,
        }

    async def keyword_search(
        self, query: str, document_id: str, keywords: List[str]
    ) -> VectorResponseSchema:
        """Perform a keyword search."""
        # Not being used currently
        raise NotImplementedError("Keyword search is not implemented yet.")

    async def delete_document(self, document_id: str) -> Dict[str, str]:
        """Delete a document from a Qdrant collection."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            ),
            wait=True,
        )
        return {
            "status": "success",
            "message": "Document deleted successfully.",
        }