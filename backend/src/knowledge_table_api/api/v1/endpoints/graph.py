"""Graph router."""

import json
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from whyhow import Chunk, ChunkMetadata

from knowledge_table_api.core.dependencies import get_llm_service
from knowledge_table_api.models.graph import Table
from knowledge_table_api.services.graph import generate_triples
from knowledge_table_api.services.llm import generate_schema

router = APIRouter(tags=["Graph"], prefix="/graph")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def to_dict(obj: Any) -> Dict[str, Any]:
    """Convert a Pydantic object or dictionary to a dictionary."""
    return obj.dict() if hasattr(obj, "dict") else obj.model_dump()


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle special object types like datetime, Decimal, and Chunk."""

    def default(self, obj: Any) -> Any:
        """Handle various types for JSON encoding, such as datetime, Decimal, Chunk, and ChunkMetadata."""
        if isinstance(obj, bool):
            return str(obj).lower()
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (set, frozenset)):
            return list(obj)
        elif isinstance(obj, Chunk):
            return self.encode_chunk(obj)
        elif isinstance(obj, ChunkMetadata):
            return self.encode_chunk_metadata(obj)
        elif hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)

    def encode_chunk(self, chunk: Chunk) -> Dict[str, Any]:
        """Encode Chunk objects for JSON serialization."""
        return {
            "chunk_id": chunk.chunk_id,
            "created_at": (
                chunk.created_at.isoformat() if chunk.created_at else None
            ),
            "updated_at": (
                chunk.updated_at.isoformat() if chunk.updated_at else None
            ),
            "document_id": chunk.document_id,
            "workspace_ids": chunk.workspace_ids,
            "metadata": (
                self.encode_chunk_metadata(chunk.metadata)
                if chunk.metadata
                else None
            ),
            "content": chunk.content,
            "embedding": chunk.embedding,
            "tags": chunk.tags,
            "user_metadata": chunk.user_metadata,
        }

    def encode_chunk_metadata(self, metadata: ChunkMetadata) -> Dict[str, Any]:
        """Encode ChunkMetadata objects for JSON serialization."""
        return {
            "language": metadata.language,
            "length": metadata.length,
            "size": metadata.size,
            "data_source_type": metadata.data_source_type,
            "index": metadata.index,
            "page": metadata.page,
            "start": metadata.start,
            "end": metadata.end,
        }


@router.post("/export-triples")
async def export_triples(request: Table) -> Response:
    """Handle POST requests to export triples from the given table data."""
    try:
        logger.info("Received request for exporting triples")
        logger.debug(
            f"Raw request data: {json.dumps(jsonable_encoder(request), indent=2)}"
        )

        llm_service = get_llm_service()  # Get the LLMService instance
        schema_result = await generate_schema(llm_service, request)
        schema = schema_result["schema"]
        logger.info(f"Generated schema: {json.dumps(schema, indent=2)}")

        export_data = await generate_triples(schema, request)
        logger.info(
            f"Generated {len(export_data['triples'])} triples and {len(export_data['chunks'])} chunks"
        )

        # Convert export data to JSON format
        json_content = json.dumps(export_data, indent=2)

        headers = {
            "Content-Disposition": 'attachment; filename="triples_and_chunks.json"',
            "Content-Type": "application/json",
        }

        logger.info("Sending response with triples and chunks")
        return Response(content=json_content, headers=headers)

    except ValidationError as e:
        """Handle validation errors from Pydantic models."""
        logger.error(f"Validation error: {e.json()}")
        error_details = e.errors()
        logger.error(
            f"Detailed validation errors: {json.dumps(jsonable_encoder(error_details), indent=2)}"
        )
        raise HTTPException(status_code=422, detail=error_details)
    except Exception as e:
        """Handle unexpected errors and raise an HTTP 500 error."""
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )
