"""Query service."""

import logging
from typing import Any, Dict, List, Literal

from knowledge_table_api.core.dependencies import get_llm_service
from knowledge_table_api.models.query import Rule
from knowledge_table_api.services.llm_service import (
    LLMService,
    generate_response,
)
from knowledge_table_api.services.vector_db.factory import VectorDBFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_vector_db_service() -> Any:
    """Get the vector database service."""
    llm_service = get_llm_service()
    vector_db_service = VectorDBFactory.create_vector_db_service(llm_service)
    if vector_db_service is None:
        raise ValueError("Failed to create vector database service")
    return vector_db_service


async def decomposition_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
    """Decompose the query and generate a response."""
    vector_db_service = await get_vector_db_service()
    decomposition_query_response = await vector_db_service.decomposed_search(
        query, document_id, rules
    )

    concatenated_chunks = " ".join(
        [chunk.content for chunk in decomposition_query_response["chunks"]]
    )

    answer = await generate_response(
        llm_service,
        query,
        concatenated_chunks,
        rules,
        format,
    )

    answer_value = answer["answer"]

    return {
        "answer": answer_value,
        "chunks": decomposition_query_response["chunks"][:10],
    }


async def hybrid_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
    """Perform a hybrid search and generate a response."""
    vector_db_service = await get_vector_db_service()
    hybrid_query_response = await vector_db_service.hybrid_search(
        query, document_id, rules
    )

    concatenated_chunks = " ".join(
        [chunk.content for chunk in hybrid_query_response.chunks]
    )

    answer = await generate_response(
        llm_service,
        query,
        concatenated_chunks,
        rules,
        format,
    )

    answer_value = answer["answer"]
    chunks = (
        []
        if answer_value == "not found" or answer_value is None
        else hybrid_query_response.chunks
    )

    return {"answer": answer_value, "chunks": chunks[:10]}


async def simple_vector_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
    """Perform a simple vector search and generate a response."""
    vector_db_service = await get_vector_db_service()
    simple_vector_query_response = await vector_db_service.vector_search(
        [query], document_id
    )

    concatenated_chunks = " ".join(
        [chunk.content for chunk in simple_vector_query_response["chunks"]]
    )

    answer = await generate_response(
        llm_service,
        query,
        concatenated_chunks,
        rules,
        format,
    )

    answer_value = answer["answer"]
    chunks = (
        []
        if answer_value == "not found" or answer_value is None
        else simple_vector_query_response["chunks"]
    )

    return {"answer": answer_value, "chunks": chunks[:10]}
