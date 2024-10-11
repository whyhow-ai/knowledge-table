"""Graph router."""

import json
import logging

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import ValidationError

from knowledge_table_api.core.dependencies import get_llm_service
from knowledge_table_api.models.graph import ExportData
from knowledge_table_api.routing_schemas.graph import (
    ExportTriplesRequest,
    ExportTriplesResponse,
    Table,
)
from knowledge_table_api.services.graph_service import generate_triples
from knowledge_table_api.services.llm_service import generate_schema

router = APIRouter(tags=["Graph"], prefix="/graph")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/export-triples", response_model=ExportTriplesResponse)
async def export_triples(request: Request) -> Response:
    """Export triples from a table."""
    try:
        body = await request.json()

        # Now manually validate the request
        try:
            export_request = ExportTriplesRequest(**body)
            # Create a Table object from the ExportTriplesRequest
            table = Table(
                columns=export_request.columns,
                rows=export_request.rows,
                cells=export_request.cells,
            )
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=str(e))

        llm_service = get_llm_service()  # Get the LLMService instance
        schema_result = await generate_schema(llm_service, table)
        schema = schema_result["schema"]
        print(f"Generated schema: {json.dumps(schema, indent=2)}")

        export_data = await generate_triples(schema, table)
        print(
            f"Generated {len(export_data['triples'])} triples and {len(export_data['chunks'])} chunks"
        )

        # Convert export data to ExportData model
        export_data_model = ExportData(**export_data)

        # Convert to ExportTriplesResponse
        response_data = ExportTriplesResponse(
            triples=[
                triple.model_dump() for triple in export_data_model.triples
            ],
            chunks=export_data_model.chunks,
        )

        # Convert response data to JSON format
        json_content = json.dumps(
            response_data.model_dump(), indent=2, default=str
        )

        headers = {
            "Content-Disposition": 'attachment; filename="triples_and_chunks.json"',
            "Content-Type": "application/json",
        }

        print("Sending response with triples and chunks")
        return Response(content=json_content, headers=headers)

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {str(e)}")
        raise HTTPException(
            status_code=400, detail="Invalid JSON in request body"
        )
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
