"""Document service."""

import logging
from typing import Any, Dict, List, Literal

from knowledge_table_api.models.query import Rule
from knowledge_table_api.services.llm import generate_response
from knowledge_table_api.services.vector import (
    decomposed_search,
    hybrid_search,
    vector_search,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Decomposing the query into sub-queries, performing a vector search on each sub-query, and then using the chunks from all to generate an answer to the original question.
async def decomposition_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
) -> Dict[str, Any]:
    """Decompose the query and generate a response."""
    decomposition_query_response = await decomposed_search(
        query, document_id, rules
    )

    concatenated_chunks = " ".join(
        [chunk["content"] for chunk in decomposition_query_response["chunks"]]
    )

    answer = await generate_response(
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


# Keyword search and vector search are performed, using chunks from both to generate an answer.
async def hybrid_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
) -> Dict[str, Any]:
    """Perform a hybrid search and generate a response."""
    hybrid_query_response = await hybrid_search(query, document_id, rules)

    concatenated_chunks = " ".join(
        [chunk.content for chunk in hybrid_query_response.chunks]
    )

    answer = await generate_response(
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


# Vector search is performed and the resulting chunks are used to generate an answer.
async def simple_vector_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
) -> Dict[str, Any]:
    """Perform a simple vector search and generate a response."""
    simple_vector_query_response = await vector_search([query], document_id)

    concatenated_chunks = " ".join(
        [chunk["content"] for chunk in simple_vector_query_response["chunks"]]
    )

    answer = await generate_response(
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
