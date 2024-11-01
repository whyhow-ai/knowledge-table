"""Query router."""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_llm_service, get_vector_db_service
from app.schemas.query_api import (
    QueryAnswer,
    QueryAnswerResponse,
    QueryRequestSchema,
    QueryResult,
)
from app.services.llm.base import CompletionService
from app.services.query_service import (
    decomposition_query,
    hybrid_query,
    inference_query,
    simple_vector_query,
)
from app.services.vector_db.base import VectorDBService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["query"])
logger.info("Query router initialized")


@router.post("", response_model=QueryAnswerResponse)
async def run_query(
    request: QueryRequestSchema,
    llm_service: CompletionService = Depends(get_llm_service),
    vector_db_service: VectorDBService = Depends(get_vector_db_service),
) -> QueryAnswerResponse:
    """
    Run a query and generate a response.

    This endpoint processes incoming query requests, determines the appropriate
    query type, and executes the corresponding query function. It supports
    vector, hybrid, and decomposition query types.

    Parameters
    ----------
    request : QueryRequestSchema
        The incoming query request.
    llm_service : CompletionService
        The language model service.
    vector_db_service : VectorDBService
        The vector database service.

    Returns
    -------
    QueryResponseSchema
        The generated response to the query.

    Raises
    ------
    HTTPException
        If there's an error processing the query.
    """
    if request.document_id == "00000000000000000000000000000000":
        query_response = await inference_query(
            request.prompt.query,
            request.prompt.rules,
            request.prompt.type,
            llm_service,
        )

        if not isinstance(query_response, QueryResult):
            query_response = QueryResult(**query_response)

        answer = QueryAnswer(
            id=uuid.uuid4().hex,
            document_id=request.document_id,
            prompt_id=request.prompt.id,
            answer=query_response.answer,
            type=request.prompt.type,
        )
        response_data = QueryAnswerResponse(
            answer=answer, chunks=query_response.chunks
        )

        return response_data

    try:
        logger.info(f"Received query request: {request.model_dump()}")

        # Determine query type
        query_type = (
            "hybrid"
            if request.prompt.rules or request.prompt.type == "bool"
            else "vector"
        )

        query_functions = {
            "decomposed": decomposition_query,
            "hybrid": hybrid_query,
            "vector": simple_vector_query,
        }

        query_response = await query_functions[query_type](
            request.prompt.query,
            request.document_id,
            request.prompt.rules,
            request.prompt.type,
            llm_service,
            vector_db_service,
        )

        if not isinstance(query_response, QueryResult):
            query_response = QueryResult(**query_response)

        # response_data = QueryResponseSchema(
        #     id=str(uuid.uuid4()),
        #     document_id=request.document_id,
        #     prompt_id=request.prompt.id,
        #     type=request.prompt.type,
        #     answer=query_response.answer,
        #     chunks=query_response.chunks,
        # )

        answer = QueryAnswer(
            id=uuid.uuid4().hex,
            document_id=request.document_id,
            prompt_id=request.prompt.id,
            answer=query_response.answer,
            type=request.prompt.type,
        )
        # Include resolved_entities in the response
        response_data = QueryAnswerResponse(
            answer=answer,
            chunks=query_response.chunks,
            resolved_entities=query_response.resolved_entities,  # Add this line
        )

        return response_data

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
