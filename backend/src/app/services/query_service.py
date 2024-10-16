"""Query service."""

import logging
from typing import Any, Awaitable, Callable, Dict, List, Literal, Union

from app.core.dependencies import get_vector_db_service
from app.models.query import Chunk, Rule
from app.schemas.query import VectorResponse
from app.services.llm_service import LLMService, generate_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QueryType = Literal["decomposition", "hybrid", "simple_vector"]
FormatType = Literal["int", "str", "bool", "int_array", "str_array"]
SearchResponse = Union[Dict[str, List[Chunk]], VectorResponse]
SearchMethod = Callable[[str, str, List[Rule]], Awaitable[SearchResponse]]


async def process_query(
    query_type: QueryType,
    query: str,
    document_id: str,
    rules: List[Rule],
    format: FormatType,
    llm_service: LLMService,
) -> Dict[str, Any]:
    """
    Process the query based on the specified type.

    Parameters
    ----------
    query_type : QueryType
        The type of search to perform.
    query : str
        The query string to process.
    document_id : str
        The ID of the document to search within.
    rules : List[Rule]
        A list of rules to apply during processing.
    format : FormatType
        The desired format of the answer.
    llm_service : LLMService
        The language model service to use for generating responses.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the answer and relevant chunks.
    """
    vector_db_service = get_vector_db_service()

    search_methods: Dict[QueryType, SearchMethod] = {
        "decomposition": vector_db_service.decomposed_search,
        "hybrid": vector_db_service.hybrid_search,
        "simple_vector": lambda q, d, r: vector_db_service.vector_search(
            [q], d
        ),
    }

    search_response = await search_methods[query_type](
        query, document_id, rules
    )
    chunks = (
        search_response["chunks"]
        if isinstance(search_response, dict)
        else search_response.chunks
    )
    concatenated_chunks = " ".join(chunk.content for chunk in chunks)

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


async def execute_query(
    query_type: QueryType,
    query: str,
    document_id: str,
    rules: List[Rule],
    format: FormatType,
    llm_service: LLMService,
) -> Dict[str, Any]:
    """
    Execute a query of the specified type.

    Parameters
    ----------
    query_type : QueryType
        The type of query to perform.
    query : str
        The query string.
    document_id : str
        The ID of the document to search.
    rules : List[Rule]
        A list of rules to apply to the query.
    format : FormatType
        The desired format of the answer.
    llm_service : LLMService
        The language model service to use for generating responses.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the answer and relevant chunks.
    """
    return await process_query(
        query_type, query, document_id, rules, format, llm_service
    )


# Convenience functions for specific query types
async def decomposition_query(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Execute a decomposition query."""
    return await execute_query("decomposition", *args, **kwargs)


async def hybrid_query(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Execute a hybrid query."""
    return await execute_query("hybrid", *args, **kwargs)


async def simple_vector_query(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Execute a simple vector query."""
    return await execute_query("simple_vector", *args, **kwargs)
