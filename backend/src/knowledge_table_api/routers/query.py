"""Query router."""

import logging
import uuid

from fastapi import APIRouter

from knowledge_table_api.models.query import Answer, QueryRequest
from knowledge_table_api.services.query import (
    decomposition_query,
    hybrid_query,
    simple_vector_query,
)

router = APIRouter(tags=["Query"], prefix="/query")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("", response_model=Answer)
async def run_query(request: QueryRequest) -> Answer:
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
        raise ValueError(f"Invalid query type: {query_type}")

    # Get the appropriate function based on query_type and call it
    query_response = await query_functions[query_type](
        request.prompt.query,
        request.document_id,
        rules,
        request.prompt.type,
    )

    if len(query_response["chunks"]) == 0:
        return Answer(
            id=uuid.uuid4().hex,
            document_id=request.document_id,
            prompt_id=request.prompt.id,
            answer=None,
            chunks=[],
            type=request.prompt.type,
        )

    answer = Answer(
        id=uuid.uuid4().hex,
        document_id=request.document_id,
        prompt_id=request.prompt.id,
        answer=query_response["answer"],
        chunks=query_response["chunks"],
        type=request.prompt.type,
    )
    return answer
