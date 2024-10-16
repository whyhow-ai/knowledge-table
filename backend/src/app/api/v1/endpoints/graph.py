"""Graph API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_llm_service
from app.models.table import Table
from app.schemas.graph_api import (
    ExportTriplesRequestSchema,
    ExportTriplesResponseSchema,
)
from app.services.graph_service import generate_triples
from app.services.llm.base import LLMService
from app.services.llm_service import generate_schema

router = APIRouter(tags=["Graph"])
logger = logging.getLogger(__name__)


@router.post("/export-triples", response_model=ExportTriplesResponseSchema)
async def export_triples(
    request: ExportTriplesRequestSchema,
    llm_service: LLMService = Depends(get_llm_service),
) -> ExportTriplesResponseSchema:
    """
    Generate and export triples from a table.

    This endpoint processes the input table data, generates a schema using the LLM service,
    and then creates triples and chunks based on the generated schema.

    Parameters
    ----------
    request : ExportTriplesRequestSchema
        The request body containing the table data (columns, rows, and cells).
    llm_service : LLMService
        The language model service used for generating the schema, injected by FastAPI.

    Returns
    -------
    ExportTriplesResponseSchema
        A schema containing the generated triples and chunks.

    Raises
    ------
    HTTPException
        If an error occurs during the processing of the table data or generation of triples.
        The exception will have a status code of 500 and the error message as its detail.

    Notes
    -----
    The function logs the generated schema and the number of triples and chunks created.
    """
    try:
        table = Table(
            columns=request.columns, rows=request.rows, cells=request.cells
        )

        schema_result = await generate_schema(llm_service, table)
        schema = schema_result["schema"]
        logger.info(f"Generated schema: {schema}")

        export_data = await generate_triples(schema, table)
        logger.info(
            f"Generated {len(export_data.triples)} triples and {len(export_data.chunks)} chunks"
        )

        return export_data

    except Exception as e:
        logger.error(f"Error generating triples: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
