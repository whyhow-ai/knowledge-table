"""The Milvus service for the vector database."""

import asyncio
import json
import logging
import re
import uuid
from typing import Any, Dict, List, Optional, Union

from langchain.schema import Document
from pydantic import BaseModel, Field
from pymilvus import DataType, MilvusClient

from app.core.config import get_settings, Settings
from app.schemas.query import Chunk, Rule, VectorResponse
from app.services.llm_service import LLMService, get_keywords
from app.services.vector_db.base import VectorDBService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MilvusMetadata(BaseModel, extra="forbid"):
    """Metadata for Milvus documents."""

    text: str
    page_number: int
    chunk_number: int
    document_id: str
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))


class MilvusService(VectorDBService):
    """The Milvus service for the vector database."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.client = MilvusClient(
            uri=settings.milvus_db_uri,
            token=settings.milvus_db_token,
        )

    async def get_embeddings(
        self, text: Union[str, List[str]]
    ) -> Union[List[float], List[List[float]]]:
        """Get embeddings for the given text using the LLM service."""
        if isinstance(text, str):
            return await self.llm_service.get_embeddings(text)
        else:
            # If it's a list of strings, get embeddings for all strings in parallel
            tasks = [self.llm_service.get_embeddings(t) for t in text]
            return await asyncio.gather(*tasks)

    async def ensure_collection_exists(self) -> None:
        """Ensure the collection exists in the Milvus database."""
        if not self.client.has_collection(collection_name=settings.index_name):
            # Create the schema
            schema = self.client.create_schema(
                auto_id=False,
                enable_dynamic_field=True,
            )

            # Add the id field
            schema.add_field(
                field_name="id",
                datatype=DataType.VARCHAR,
                is_primary=True,
                max_length=36,
            )

            # Add the vector field
            schema.add_field(
                field_name="vector",
                datatype=DataType.FLOAT_VECTOR,
                dim=settings.dimensions,
            )

            # Add the index
            index_params = self.client.prepare_index_params()
            index_params.add_index(
                index_type="AUTOINDEX",
                field_name="vector",
                metric_type="COSINE",
            )

            # Create the collection
            self.client.create_collection(
                collection_name=settings.index_name,
                schema=schema,
                index_params=index_params,
                consistency_level=0,
            )

    async def upsert_vectors(
        self, vectors: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Upsert the vectors into the Milvus database."""
        logger.info(f"Upserting {len(vectors)} chunks")

        batch_size = (
            1000  # Adjust this based on your Milvus instance's capabilities
        )
        total_inserted = 0

        try:
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i : i + batch_size]
                upsert_response = self.client.insert(
                    collection_name=settings.index_name, data=batch
                )
                total_inserted += upsert_response["insert_count"]
                logger.info(
                    f"Inserted batch of {upsert_response['insert_count']} chunks."
                )

            logger.info(
                f"Successfully upserted {total_inserted} chunks in total."
            )
            return {
                "message": f"Successfully upserted {total_inserted} chunks."
            }
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            if vectors:
                logger.error(f"Sample vector data: {vectors[0]}")
            raise

    async def prepare_chunks(
        self, document_id: str, chunks: List[Document]
    ) -> List[Dict[str, Any]]:
        """Prepare chunks for insertion into the Milvus database."""
        logger.info(f"Preparing {len(chunks)} chunks")

        # Clean the chunks
        cleaned_chunks = []
        for chunk in chunks:
            cleaned_chunks.append(
                re.sub("/(\r\n|\n|\r)/gm", "", chunk.page_content)
            )

        logger.info("Generating embeddings.")

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
            metadata = MilvusMetadata(
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

        logger.info("Chunks processed successfully.")
        return datas

    async def vector_search(
        self, queries: List[str], document_id: str
    ) -> VectorResponse:
        """Perform a vector search on the Milvus database."""
        logger.info(f"Retrieving vectors for {len(queries)} queries.")

        # Prepare the final chunks
        final_chunks: List[Dict[str, Any]] = []

        # Search for each query
        for query in queries:
            logger.info("Generating embedding.")

            # Embed the query
            embedded_query = await self.get_embeddings(query)

            logger.info("Searching...")

            # Search the collection
            query_response = self.client.search(
                collection_name=settings.index_name,
                data=[embedded_query],
                filter=f"document_id == '{document_id}'",
                limit=40,
                output_fields=[
                    "text",
                    "page_number",
                    "document_id",
                    "chunk_number",
                ],
            )

            # Add the chunks to the final chunks
            final_chunks.extend(
                item["entity"] for result in query_response for item in result
            )

        seen_chunks = set()
        formatted_output = []

        # Format the output
        for chunk in final_chunks:
            if chunk["chunk_number"] not in seen_chunks:
                seen_chunks.add(chunk["chunk_number"])
                formatted_output.append(
                    Chunk(content=chunk["text"], page=chunk["page_number"])
                )

        logger.info(f"Retrieved {len(formatted_output)} unique chunks.")

        return VectorResponse(
            message="Query processed successfully.",
            chunks=formatted_output,
        )

    async def keyword_search(
        self, query: str, document_id: str, keywords: list[str]
    ) -> VectorResponse:
        """Perform a keyword search on the Milvus database."""
        logger.info("Performing keyword search.")

        response = []
        chunk_response = []
        seen_chunks = set()

        # Run the keyword search
        if keywords:
            for keyword in keywords:
                logger.info(f"Running keyword search for: {keyword}")

                clean_keyword = keyword.replace("%", "\\%").replace("_", "\\_")

                filter_string = f'(text like "%{clean_keyword}%") && document_id == "{document_id}"'

                # Query the collection
                keyword_response = self.client.query(
                    collection_name=settings.index_name,
                    filter=filter_string,
                    output_fields=[
                        "text",
                        "page_number",
                        "document_id",
                        "chunk_number",
                    ],
                )

                chunks = json.dumps(keyword_response, indent=2)
                deserialized_chunks = json.loads(chunks)

                # If there are chunks, add the keyword to the response
                if deserialized_chunks:
                    response.append(keyword)

                    def count_keyword_occurrences(
                        text: str, keyword: str
                    ) -> int:
                        return text.lower().count(keyword.lower())

                    # Sort the chunks by the number of keyword occurrences
                    sorted_keyword_chunks = sorted(
                        deserialized_chunks,
                        key=lambda chunk: count_keyword_occurrences(
                            chunk["text"], keyword
                        ),
                        reverse=True,
                    )

                    chunks_added = 0

                # Add the chunks to the response
                for chunk in sorted_keyword_chunks[:5]:
                    if chunk["chunk_number"] not in seen_chunks:
                        chunk_response.append(
                            Chunk(
                                content=chunk["text"],
                                page=chunk["page_number"],
                            )
                        )
                        seen_chunks.add(chunk["chunk_number"])
                        chunks_added += 1
                    if chunks_added >= 5:
                        break

        return VectorResponse(
            message="Query processed successfully.",
            chunks=chunk_response,
            keywords=response,
        )

    async def hybrid_search(
        self, query: str, document_id: str, rules: list[Rule]
    ) -> VectorResponse:
        """Perform a hybrid search on the Milvus database."""
        logger.info("Performing hybrid search.")

        keywords: list[str] = []
        sorted_keyword_chunks = []
        max_length: Optional[int] = None

        # Process the rules
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
                elif rule.type == "max_length":
                    max_length = rule.length

        # If no keywords are provided, extract them from the query
        if not keywords:
            logger.info(
                "No keywords provided, extracting keywords from the query."
            )
            try:
                extracted_keywords = await get_keywords(
                    self.llm_service, query
                )
                if extracted_keywords and isinstance(extracted_keywords, list):
                    keywords = extracted_keywords
                else:
                    logger.info("No keywords found in the query.")
            except Exception as e:
                logger.error(f"An error occurred while getting keywords: {e}")

        logger.info(f"Using keywords: {keywords}")
        if max_length:
            logger.info(f"Max length set to: {max_length}")

        # Run the keyword search (if keywords exist)
        if keywords:
            like_conditions = " || ".join(
                [f'text like "%{keyword}%"' for keyword in keywords]
            )
            filter_string = (
                f'({like_conditions}) && document_id == "{document_id}"'
            )

            logger.info("Running query with keyword filters.")

            # Query the collection
            keyword_response = self.client.query(
                collection_name=settings.index_name,
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

            # Count the keywords in the chunks
            def count_keywords(text: str, keywords: List[str]) -> int:
                return sum(
                    text.lower().count(keyword.lower()) for keyword in keywords
                )

            # Sort the chunks by the number of keywords
            sorted_keyword_chunks = sorted(
                deserialized_keyword_chunks,
                key=lambda chunk: count_keywords(
                    chunk["text"], keywords or []
                ),
                reverse=True,
            )

        # Embed the query
        embedded_query = await self.get_embeddings(query)

        try:
            # First, let's check if there are any vectors for this document_id
            count_response = self.client.query(
                collection_name=settings.index_name,
                filter=f'document_id == "{document_id}"',
                output_fields=["count(*)"],
            )
            vector_count = count_response[0]["count(*)"]
            logger.info(
                f"Number of vectors for document_id {document_id}: {vector_count}"
            )

            if vector_count == 0:
                logger.warning(
                    f"No vectors found for document_id: {document_id}"
                )
                return VectorResponse(
                    message="No data found for the given document.", chunks=[]
                )

            # Now let's perform the search
            # Ensure that embedded_query is wrapped in a list
            semantic_response = self.client.search(
                collection_name=settings.index_name,
                data=[embedded_query],
                filter=f'document_id == "{document_id}"',
                limit=40,
                output_fields=[
                    "text",
                    "page_number",
                    "document_id",
                    "chunk_number",
                ],
            )
            logger.info(
                f"Number of results from semantic search: {len(semantic_response)}"
            )

            # Flatten the semantic response
            flattened_semantic_chunks = [
                hit["entity"] for result in semantic_response for hit in result
            ]

            logger.info(
                f"Found {len(flattened_semantic_chunks)} semantic chunks."
            )

            # Combine the keyword and semantic chunks
            combined_chunks = (
                sorted_keyword_chunks[:20] if sorted_keyword_chunks else []
            ) + flattened_semantic_chunks

            # Sort the chunks by chunk number if available
            if combined_chunks and "chunk_number" in combined_chunks[0]:
                combined_sorted_chunks = sorted(
                    combined_chunks, key=lambda chunk: chunk["chunk_number"]
                )
            else:
                combined_sorted_chunks = combined_chunks

            seen_chunks = set()
            formatted_output = []

            # Format the output
            for chunk in combined_sorted_chunks:
                chunk_id = chunk.get("chunk_number") or chunk.get("id")
                if chunk_id not in seen_chunks:
                    formatted_output.append(
                        Chunk(
                            content=chunk["text"],
                            page=chunk.get("page_number", 0),
                        )
                    )
                    seen_chunks.add(chunk_id)

            logger.info(f"Retrieved {len(formatted_output)} unique chunks.")

            return VectorResponse(
                message="Query processed successfully.",
                chunks=formatted_output,
            )

        except Exception as e:
            logger.error(f"Error during Milvus search: {e}")
            logger.error(
                f"Milvus search parameters: collection_name={settings.index_name}, data shape=1x{len(embedded_query)}"
            )
            raise

    async def decomposed_search(
        self, query: str, document_id: str, rules: List[Rule]
    ) -> Dict[str, Any]:
        """Decomposition query."""
        logger.info("Decomposing query into smaller sub-queries.")

        # Break the question into simpler sub-questions
        decomposition_response = await self.llm_service.decompose_query(
            query=query
        )

        # Get the chunks for each sub-query
        sub_query_chunks = await self.vector_search(
            decomposition_response["sub-queries"], document_id
        )

        return {
            "sub_queries": decomposition_response["sub-queries"],
            "chunks": [
                chunk.model_dump() for chunk in sub_query_chunks.chunks
            ],
        }

    async def delete_document(self, document_id: str) -> Dict[str, str]:
        """Delete a document from the Milvus."""
        self.client.delete(
            collection_name=settings.index_name,
            filter=f'document_id == "{document_id}"',
        )

        # Confirm the deletion
        confirm_delete = self.client.query(
            collection_name=settings.index_name,
            filter=f'document_id == "{document_id}"',
        )

        # Check if the document was deleted
        chunks = json.dumps(confirm_delete, indent=2)

        if len(json.loads(chunks)) == 0:
            return {
                "status": "success",
                "message": "Document deleted successfully.",
            }
        else:
            return {"status": "error", "message": "Document deletion failed."}
