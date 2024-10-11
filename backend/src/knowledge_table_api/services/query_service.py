"""Query service."""

import logging
from typing import Any, Dict, List, Literal

from knowledge_table_api.core.dependencies import get_llm_service, get_settings
from knowledge_table_api.models.query import Rule
from knowledge_table_api.services.llm_service import (
    LLMService,
    generate_response,
)
from knowledge_table_api.services.vector_db.factory import VectorDBFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_vector_db_service() -> Any:
    """
    Get the vector database service.

    Returns
    -------
    Any
        An instance of the vector database service.

    Raises
    ------
    ValueError
        If the vector database service creation fails.
    """
    # Get the LLM service
    llm_service = get_llm_service()

    # Get the settings
    settings = get_settings()

    # Create the vector database service
    vector_db_service = VectorDBFactory.create_vector_db_service(
        settings.vector_db_provider, llm_service, settings
    )
    if vector_db_service is None:
        raise ValueError("Failed to create vector database service")
    return vector_db_service


async def process_query(
    query_type: Literal["decomposition", "hybrid", "simple_vector"],
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
    """
    Process the query based on the specified type.

    Parameters
    ----------
    query_type : Literal["decomposition", "hybrid", "simple_vector"]
        The type of query to perform.
    query : str
        The query string.
    document_id : str
        The ID of the document to search.
    rules : List[Rule]
        A list of rules to apply to the query.
    format : Literal["int", "str", "bool", "int_array", "str_array"]
        The desired format of the answer.
    llm_service : LLMService
        The language model service to use for generating responses.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the answer and relevant chunks.
    """
    # Get the vector database service
    vector_db_service = await get_vector_db_service()

    # Define the search methods
    search_methods = {
        "decomposition": vector_db_service.decomposed_search,
        "hybrid": vector_db_service.hybrid_search,
        "simple_vector": lambda q, d, r: vector_db_service.vector_search(
            [q], d
        ),
    }

    # Execute the search
    search_response = await search_methods[query_type](
        query, document_id, rules
    )

    # Get the chunks
    chunks = (
        search_response["chunks"]
        if query_type == "decomposition"
        else search_response.chunks
    )
    concatenated_chunks = " ".join([chunk.content for chunk in chunks])

    # Generate the answer
    answer = await generate_response(
        llm_service, query, concatenated_chunks, rules, format
    )
    answer_value = answer["answer"]

    result_chunks = (
        []
        if answer_value in ("not found", None)
        and query_type != "decomposition"
        else chunks
    )

    return {"answer": answer_value, "chunks": result_chunks[:10]}


# Wrapper functions for specific query types
async def decomposition_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
    """
    Perform a decomposition query.

    This is a wrapper function that calls process_query with the "decomposition" query type.

    Parameters
    ----------
    query : str
        The query string.
    document_id : str
        The ID of the document to search.
    rules : List[Rule]
        A list of rules to apply to the query.
    format : Literal["int", "str", "bool", "int_array", "str_array"]
        The desired format of the answer.
    llm_service : LLMService
        The language model service to use for generating responses.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the answer and relevant chunks.
    """
    return await process_query(
        "decomposition", query, document_id, rules, format, llm_service
    )


async def hybrid_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
    """
    Perform a hybrid query.

    This is a wrapper function that calls process_query with the "hybrid" query type.

    Parameters
    ----------
    query : str
        The query string.
    document_id : str
        The ID of the document to search.
    rules : List[Rule]
        A list of rules to apply to the query.
    format : Literal["int", "str", "bool", "int_array", "str_array"]
        The desired format of the answer.
    llm_service : LLMService
        The language model service to use for generating responses.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the answer and relevant chunks.
    """
    return await process_query(
        "hybrid", query, document_id, rules, format, llm_service
    )


async def simple_vector_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
    llm_service: LLMService,
) -> Dict[str, Any]:
    """
    Perform a simple vector query.

    This is a wrapper function that calls process_query with the "simple_vector" query type.

    Parameters
    ----------
    query : str
        The query string.
    document_id : str
        The ID of the document to search.
    rules : List[Rule]
        A list of rules to apply to the query.
    format : Literal["int", "str", "bool", "int_array", "str_array"]
        The desired format of the answer.
    llm_service : LLMService
        The language model service to use for generating responses.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the answer and relevant chunks.
    """
    return await process_query(
        "simple_vector", query, document_id, rules, format, llm_service
    )
