"""Query router."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException

from knowledge_table_api.core.dependencies import get_llm_service
from knowledge_table_api.models.query import Answer
from knowledge_table_api.schemas.query import QueryRequest, QueryResponse
from knowledge_table_api.services.llm_service import LLMService
from knowledge_table_api.services.query import (
    decomposition_query,
    hybrid_query,
    simple_vector_query,
)

router = APIRouter(tags=["Query"], prefix="/query")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("", response_model=QueryResponse)
async def run_query(
    request: QueryRequest, llm_service: LLMService = Depends(get_llm_service)
) -> QueryResponse:
    """
    Run a query and generate a response.

    We have three methods for generating answers:
    1. Simple Vector Search: Performs a vector search and uses the resulting chunks to generate an answer.
    2. Hybrid Search: Performs both a keyword search and a vector search, using chunks from both to generate an answer.
    3. Decomposed Search: Breaks down the query into sub-queries, performs a vector search on each sub-query, and then uses the answers and chunks from each to generate an answer to the original question.
    """
    query_type = request.rag_type  # vector, hybrid, decomposed

    # If there's rules, or if the answer is boolean, do hybrid
    if request.prompt.rules or request.prompt.type == "bool":
        query_type = "hybrid"

    # Define a mapping of query types to their corresponding functions
    query_functions = {
        "decomposed": decomposition_query,
        "hybrid": hybrid_query,
        "vector": simple_vector_query,
    }

    rules = request.prompt.rules or []

    if query_type not in query_functions:
        raise HTTPException(
            status_code=400, detail=f"Invalid query type: {query_type}"
        )

    # Get the appropriate function based on query_type and call it
    try:
        query_response = await query_functions[query_type](
            request.prompt.query,
            request.document_id,
            rules,
            request.prompt.type,
            llm_service,
        )
    except Exception as e:
        logger.error(f"Error in query function: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    if len(query_response["chunks"]) == 0:
        answer = Answer(
            id=uuid.uuid4().hex,
            document_id=request.document_id,
            prompt_id=request.prompt.id,
            answer=None,
            chunks=[],
            type=request.prompt.type,
        )
    else:
        answer = Answer(
            id=uuid.uuid4().hex,
            document_id=request.document_id,
            prompt_id=request.prompt.id,
            answer=query_response["answer"],
            chunks=query_response["chunks"],
            type=request.prompt.type,
        )

    return QueryResponse(**answer.dict())
