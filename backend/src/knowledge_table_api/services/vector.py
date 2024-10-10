"""The functions for interacting with the Milvus database."""

import json
import logging
import re
import uuid
from typing import Any, Dict, List, Optional

import numpy as np
from langchain.schema import Document
from pydantic import BaseModel, Field
from pymilvus import DataType, MilvusClient

from knowledge_table_api.config import Settings
from knowledge_table_api.dependencies import get_milvus_client, get_settings
from knowledge_table_api.models.query import Chunk, Rule, VectorResponse
from knowledge_table_api.services.llm import decompose_query, get_keywords
from knowledge_table_api.services.llm_service import LLMService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MilvusMetadata(BaseModel, extra="forbid"):
    """Metadata for Milvus documents."""

    text: str
    page_number: int
    chunk_number: int
    document_id: str
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))


def get_embeddings(llm_service: LLMService) -> Any:
    """Get the embedding function from the LLM service."""
    return llm_service.get_embeddings()


def ensure_collection_exists(client: MilvusClient, settings: Settings) -> None:
    """Ensure the collection exists in the Milvus database."""
    if not client.has_collection(collection_name=settings.index_name):
        schema = client.create_schema(
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
            dim=settings.dimensions,
        )
        index_params = client.prepare_index_params()
        index_params.add_index(
            index_type="AUTOINDEX",
            field_name="vector",
            metric_type="COSINE",
        )

        client.create_collection(
            collection_name=settings.index_name,
            schema=schema,
            index_params=index_params,
            consistency_level=0,
        )


async def upsert_vectors(vectors: List[Dict[str, Any]]) -> Dict[str, str]:
    """Upsert the vectors into the Milvus database."""
    logger.info(f"Upserting {len(vectors)} chunks")

    client = get_milvus_client()
    settings = get_settings()

    upsert_response = client.insert(
        collection_name=settings.index_name, data=vectors
    )

    return {
        "message": f"Successfully upserted {upsert_response['insert_count']} chunks."
    }


async def prepare_chunks(
    document_id: str, chunks: List[Document], llm_service: LLMService
) -> List[Dict[str, Any]]:
    """Prepare chunks for insertion into the Milvus database."""
    logger.info(f"Preparing {len(chunks)} chunks")

    embeddings = get_embeddings(llm_service)

    cleaned_chunks = []
    for chunk in chunks:
        cleaned_chunks.append(
            re.sub("/(\r\n|\n|\r)/gm", "", chunk.page_content)
        )

    logger.info("Generating embeddings.")

    texts = [chunk.page_content for chunk in chunks]

    embedded_chunks = [np.array(embeddings.embed_documents(texts)).tolist()]

    datas = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embedded_chunks[0])):
        # Use the existing page number if available, otherwise calculate a pseudo-page number
        if "page" in chunk.metadata:
            page = chunk.metadata["page"] + 1
        else:
            # Create a pseudo-page number based on chunk index
            # Adjust this calculation as needed
            page = (i // 5) + 1  # Assuming 5 chunks per "page"

        metadata = MilvusMetadata(
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

    logger.info("Chunks processed successfully.")

    return datas


async def vector_search(
    queries: List[str], document_id: str, llm_service: LLMService
) -> dict[str, Any]:
    """Perform a vector search on the Milvus database."""
    logger.info(f"Retrieving vectors for {len(queries)} queries.")

    client = get_milvus_client()
    settings = get_settings()
    embeddings = get_embeddings(llm_service)

    final_chunks: List[Dict[str, Any]] = []

    for query in queries:
        logger.info("Generating embedding.")
        embedded_query = [np.array(embeddings.embed_query(query)).tolist()]

        logger.info("Searching...")
        query_response = client.search(
            collection_name=settings.index_name,
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


async def keyword_search(
    query: str,
    document_id: str,
    keywords: list[str],
) -> dict[str, Any]:
    """Perform a keyword search on the Milvus database."""
    logger.info("Performing keyword search.")

    client = get_milvus_client()
    settings = get_settings()

    response = []
    chunk_response = []
    seen_chunks = set()

    if keywords:

        for keyword in keywords:
            logger.info(f"Running keyword search for: {keyword}")

            # Escape % character in keyword
            clean_keyword = keyword.replace("%", "\\%").replace("_", "\\_")

            # Build the filter string
            filter_string = f'(text like "%{clean_keyword}%") && document_id == "{document_id}"'

            keyword_response = client.query(
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

            if deserialized_chunks:

                # Keyword exists, add to response
                response.append(keyword)

                # Count up the keyword occurrences
                def count_keyword_occurrences(text: str, keyword: str) -> int:
                    return text.lower().count(keyword.lower())

                # Sort by the number of keyword occurrences
                sorted_keyword_chunks = sorted(
                    deserialized_chunks,
                    key=lambda chunk: count_keyword_occurrences(
                        chunk["text"], keyword
                    ),
                    reverse=True,
                )

                chunks_added = 0

                # Send back the top 5 chunks for this keyword match, don't duplicate chunks
                # Add in check here to make sure we're not exceeding context window for the model (128k)
                for chunk in sorted_keyword_chunks[:5]:
                    if chunk["chunk_number"] not in seen_chunks:
                        chunk_response.append(
                            {
                                "content": chunk["text"],
                                "page": chunk["page_number"],
                            }
                        )
                        seen_chunks.add(chunk["chunk_number"])
                        chunks_added += 1
                    if chunks_added >= 5:
                        break

    return {
        "message": "Query processed successfully.",
        "keywords": response,
        "chunks": chunk_response,
    }


async def hybrid_search(
    query: str, document_id: str, rules: list[Rule], llm_service: LLMService
) -> VectorResponse:
    """Perform a hybrid search on the Milvus database."""
    logger.info("Performing hybrid search.")

    client = get_milvus_client()
    settings = get_settings()
    embeddings = get_embeddings(llm_service)

    keywords: list[str] = []
    sorted_keyword_chunks = []
    max_length: Optional[int] = None

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

    # If no keywords were provided, extract them from the query
    if not keywords:
        logger.info(
            "No keywords provided, extracting keywords from the query."
        )
        try:
            extracted_keywords = await get_keywords(llm_service, query)
            if extracted_keywords and isinstance(extracted_keywords, list):
                keywords = extracted_keywords
            else:
                logger.info("No keywords found in the query.")
        except Exception as e:
            logger.error(f"An error occurred while getting keywords: {e}")

    logger.info(f"Using keywords: {keywords}")
    if max_length:
        logger.info(f"Max length set to: {max_length}")

    if keywords:

        # Build the filter string
        like_conditions = " || ".join(
            [f'text like "%{keyword}%"' for keyword in keywords]
        )
        filter_string = (
            f'({like_conditions}) && document_id == "{document_id}"'
        )

        # Run Milvus query
        logger.info("Running query with keyword filters.")

        keyword_response = client.query(
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

        # Count up the keyword occurrences
        def count_keywords(text: str, keywords: List[str]) -> int:
            return sum(
                text.lower().count(keyword.lower()) for keyword in keywords
            )

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
    semantic_response = client.search(
        collection_name=settings.index_name,
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
    query: str, document_id: str, rules: List[Rule], llm_service: LLMService
) -> Dict[str, Any]:
    """Decomposition query."""
    logger.info("Decomposing query into smaller sub-queries.")

    # Break the question into simpler sub-questions, and get the chunks for each
    decomposition_response = await decompose_query(
        llm_service=llm_service, query=query
    )

    sub_query_chunks = await vector_search(
        decomposition_response["sub-queries"], document_id, llm_service
    )

    return {
        "sub_queries": decomposition_response["sub-queries"],
        "chunks": sub_query_chunks["chunks"],
    }


async def delete_document(
    document_id: str,
) -> Dict[str, str]:
    """Delete a document from the Milvus."""
    client = get_milvus_client()
    settings = get_settings()

    client.delete(
        collection_name=settings.index_name,
        filter=f'document_id == "{document_id}"',
    )

    confirm_delete = client.query(
        collection_name=settings.index_name,
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
