import json
import logging
from typing import Any, Dict, List, Optional

import numpy as np
from langchain.schema import Document
from pymilvus import DataType, MilvusClient

from backend.src.knowledge_table_api.services.vector_index.base import (
    VectorIndex,
)
from knowledge_table_api.dependencies import get_settings
from knowledge_table_api.models.query import Chunk, Rule, VectorResponse
from knowledge_table_api.services.llm import decompose_query, get_keywords
from knowledge_table_api.services.llm_service import LLMService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MilvusIndex(VectorIndex):
    def __init__(self):
        settings = get_settings()
        self.collection_name = settings.index_name
        self.dimensions = settings.dimensions
        self.client = MilvusClient(
            "./milvus_demo.db",
            token=f"{settings.milvus_db_username}:{settings.milvus_db_password}",
        )
        self.ensure_collection_exists(self.client, settings)

    async def upsert_vectors(
        self, document_id: str, chunks: List[Document], llm_service: LLMService
    ) -> Dict[str, str]:
        """Upsert the vectors into the Milvus database."""

        vectors = self.prepare_chunks(document_id, chunks, llm_service)
        logger.info(f"Upserting {len(vectors)} chunks")

        upsert_response = self.client.insert(
            collection_name=self.collection_name, data=vectors
        )

        return {
            "message": f"Successfully upserted {upsert_response['insert_count']} chunks."
        }

    def ensure_collection_exists(self) -> None:
        """Ensure the collection exists in the Milvus database."""
        if not self.client.has_collection(collection_name=self.collection_name):
            schema = self.client.create_schema(
                auto_id=False,
                enable_dynamic_field=True,
            )

            schema.add_field(
                field_name="id",
                datatype=DataType.VARCHAR,
                is_primary=True,
                max_length=36,
            )
            schema.add_field(
                field_name="vector",
                datatype=DataType.FLOAT_VECTOR,
                dim=self.dimensions,
            )
            index_params = self.client.prepare_index_params()
            index_params.add_index(
                index_type="AUTOINDEX",
                field_name="vector",
                metric_type="COSINE",
            )

            self.client.create_collection(
                collection_name=self.collection_name,
                schema=schema,
                index_params=index_params,
                consistency_level=0,
            )

    async def vector_search(
        self, queries: List[str], document_id: str, llm_service: LLMService
    ) -> dict[str, Any]:
        """Perform a vector search on the Milvus database."""
        logger.info(f"Retrieving vectors for {len(queries)} queries.")

        embeddings = llm_service.get_embeddings()

        final_chunks: List[Dict[str, Any]] = []

        for query in queries:
            logger.info("Generating embedding.")
            embedded_query = [np.array(embeddings.embed_query(query)).tolist()]

            logger.info("Searching...")
            query_response = self.client.search(
                collection_name=self.collection_name,
                data=embedded_query,
                filter=f"document_id == '{document_id}'",
                limit=40,
                output_fields=[
                    "text",
                    "page_number",
                    "document_id",
                    "chunk_number",
                ],
            )

            # Extend final_chunks with the flattened response directly
            final_chunks.extend(
                item["entity"] for result in query_response for item in result
            )

        # Deduplicate chunks based on `chunk_number`
        seen_chunks = set()
        formatted_output = []

        for chunk in final_chunks:
            if chunk["chunk_number"] not in seen_chunks:
                seen_chunks.add(chunk["chunk_number"])
                formatted_output.append(
                    {"content": chunk["text"], "page": chunk["page_number"]}
                )

        logger.info(f"Retrieved {len(formatted_output)} unique chunks.")

        return {
            "message": "Query processed successfully.",
            "chunks": formatted_output,
        }

    async def hybrid_search(
        self, query: str, document_id: str, rules: list[Rule], llm_service: LLMService
    ) -> VectorResponse:
        """Perform a hybrid search on the Milvus database."""
        logger.info("Performing hybrid search.")

        embeddings = llm_service.get_embeddings()

        keywords = await self.extract_keywords(query, rules, llm_service)

        if keywords:

            # Build the filter string
            like_conditions = " || ".join(
                [f'text like "%{keyword}%"' for keyword in keywords]
            )
            filter_string = f'({like_conditions}) && document_id == "{document_id}"'

            # Run Milvus query
            logger.info("Running query with keyword filters.")

            keyword_response = self.client.query(
                collection_name=self.collection_name,
                filter=filter_string,
                output_fields=[
                    "text",
                    "page_number",
                    "document_id",
                    "chunk_number",
                ],
            )

            keyword_chunks = json.dumps(keyword_response, indent=2)
            deserialized_keyword_chunks = json.loads(keyword_chunks)

            # Count up the keyword occurrences
            def count_keywords(text: str, keywords: List[str]) -> int:
                return sum(text.lower().count(keyword.lower()) for keyword in keywords)

            # Sort chunks by the number of keyword occurrences
            sorted_keyword_chunks = sorted(
                deserialized_keyword_chunks,
                key=lambda chunk: count_keywords(chunk["text"], keywords or []),
                reverse=True,
            )

        # Build the semantic similarity search
        embedded_query = [np.array(embeddings.embed_query(query)).tolist()]

        logger.info("Running semantic similarity search.")

        # Running search here instead of in the vector_search function to preserve chunk ids and deduplicate
        semantic_response = self.client.search(
            collection_name=self.collection_name,
            data=embedded_query,
            filter=f'document_id == "{document_id}"',
            limit=40,
            output_fields=["text", "page_number", "document_id", "chunk_number"],
        )

        semantic_chunks = json.dumps(semantic_response, indent=2)
        deserialized_semantic_chunks = json.loads(semantic_chunks)

        flattened_semantic_chunks = [
            item["entity"]
            for sublist in deserialized_semantic_chunks
            for item in sublist
        ]

        print(f"Found {len(flattened_semantic_chunks)} semantic chunks.")

        # Combine the top results from keyword and semantic searches
        combined_chunks = sorted_keyword_chunks[:20] + flattened_semantic_chunks

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

    async def decomposed_search(
        self, query: str, document_id: str, rules: List[Rule], llm_service: LLMService
    ) -> Dict[str, Any]:
        """Decomposition query."""
        logger.info("Decomposing query into smaller sub-queries.")

        # Break the question into simpler sub-questions, and get the chunks for each
        decomposition_response = await decompose_query(
            llm_service=llm_service, query=query
        )

        sub_query_chunks = await self.vector_search(
            decomposition_response["sub-queries"], document_id, llm_service
        )

        return {
            "sub_queries": decomposition_response["sub-queries"],
            "chunks": sub_query_chunks["chunks"],
        }

    async def delete_document(
        self,
        document_id: str,
    ) -> Dict[str, str]:
        """Delete a document from the Milvus."""

        self.client.delete(
            collection_name=self.collection_name,
            filter=f'document_id == "{document_id}"',
        )

        confirm_delete = self.client.query(
            collection_name=self.collection_name,
            filter=f'document_id == "{document_id}"',
        )

        chunks = json.dumps(confirm_delete, indent=2)

        if len(json.loads(chunks)) == 0:
            return {
                "status": "success",
                "message": "Document deleted successfully.",
            }
        else:
            return {"status": "error", "message": "Document deletion failed."}
