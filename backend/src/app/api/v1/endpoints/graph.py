"""Graph API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_llm_service
from app.models.document import Document
from app.models.table import (
    Table,
    TableCell,
    TableColumn,
    TablePrompt,
    TableRow,
)
from app.schemas.graph_api import (
    ExportTriplesRequestSchema,
    ExportTriplesResponseSchema,
)
from app.services.graph_service import generate_triples
from app.services.llm.base import CompletionService
from app.services.llm_service import generate_schema

router = APIRouter(tags=["Graph"])
logger = logging.getLogger(__name__)


@router.post("/export-triples", response_model=ExportTriplesResponseSchema)
async def export_triples(
    request: ExportTriplesRequestSchema,
    llm_service: CompletionService = Depends(get_llm_service),
) -> ExportTriplesResponseSchema:
    """
    Generate and export triples from a table.

    This endpoint processes the input table data, generates a schema using the LLM service,
    and then creates triples and chunks based on the generated schema.

    Parameters
    ----------
    request : ExportTriplesRequestSchema
        The request body containing the table data (columns, rows, and cells).
    llm_service : CompletionService
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
    # Convert column type
    converted_columns = []
    for column in request.columns:
        converted_columns.append(
            TableColumn(
                id=column.id,
                hidden=column.hidden,
                prompt=TablePrompt(
                    entityType=column.entityType,
                    query=column.query,
                    rules=column.rules,
                    type=column.type,
                ),
            )
        )

    # Convert row type
    converted_rows = []
    for row in request.rows:
        if (
            isinstance(row.sourceData, dict)
            and row.sourceData["type"] == "document"
        ):
            document = Document(
                id=row.sourceData["document"]["id"],
                name=row.sourceData["document"]["name"],
                author=row.sourceData["document"]["author"],
                tag=row.sourceData["document"]["tag"],
                page_count=row.sourceData["document"]["page_count"],
            )
        else:
            document = Document(
                id="",
                name="",
                author="",
                tag="",
                page_count=0,
            )

        converted_rows.append(
            TableRow(id=row.id, hidden=row.hidden, document=document)
        )

    # Converted cell type
    converted_cells = []
    columns_dict = {item.id: item for item in request.columns}
    for row in request.rows:
        for key, value in row.cells.items():
            # Skip if value is not a string or is "None" or "none"
            if not isinstance(value, str):
                continue

            # Remove any surrounding quotes and whitespace before checking
            cleaned_value = value.strip().strip("\"'") if value else ""
            if cleaned_value and cleaned_value.lower() != "none":
                chunk_key = "-".join([row.id, key])
                chunks = request.chunks.get(
                    chunk_key, []
                )  # Use .get() with default empty list

                converted_cells.append(
                    TableCell(
                        answer={
                            "answer": value,
                            "document_id": (
                                row.sourceData.document.id
                                if hasattr(row.sourceData, "document")
                                and hasattr(row.sourceData.document, "id")
                                else ""
                            ),
                            "id": "",
                            "prompt_id": "",
                            "type": columns_dict[key].type,
                            "chunks": chunks,
                        },
                        columnId=key,
                        dirty=False,
                        rowId=row.id,
                    )
                )

    try:
        table = Table(
            columns=converted_columns,
            rows=converted_rows,
            cells=converted_cells,
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
