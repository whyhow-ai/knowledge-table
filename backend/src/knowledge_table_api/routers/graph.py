"""Query router."""

import json
from datetime import date, datetime
from decimal import Decimal
import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError

from knowledge_table_api.models.graph import Table
from knowledge_table_api.services.graph import (
    generate_triples,
    parse_table,
)
from knowledge_table_api.services.llm import generate_schema
from knowledge_table_api.services.json_encoder import CustomJSONEncoder

from whyhow import Chunk, ChunkMetadata

router = APIRouter(tags=["Graph"], prefix="/graph")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def to_dict(obj):
    return obj.dict() if hasattr(obj, 'dict') else obj.model_dump()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
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
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)

    def encode_chunk(self, chunk: Chunk):
        return {
            "chunk_id": chunk.chunk_id,
            "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
            "updated_at": chunk.updated_at.isoformat() if chunk.updated_at else None,
            "document_id": chunk.document_id,
            "workspace_ids": chunk.workspace_ids,
            "metadata": self.encode_chunk_metadata(chunk.metadata) if chunk.metadata else None,
            "content": chunk.content,
            "embedding": chunk.embedding,
            "tags": chunk.tags,
            "user_metadata": chunk.user_metadata
        }

    def encode_chunk_metadata(self, metadata: ChunkMetadata):
        return {
            "language": metadata.language,
            "length": metadata.length,
            "size": metadata.size,
            "data_source_type": metadata.data_source_type,
            "index": metadata.index,
            "page": metadata.page,
            "start": metadata.start,
            "end": metadata.end
        }

@router.post("/export-triples")
async def export_triples(request: Table) -> Response:
    try:
        logger.info("Received request for exporting triples")
        logger.debug(f"Raw request data: {json.dumps(jsonable_encoder(request), indent=2)}")

        schema_result = await generate_schema(request)
        schema = schema_result['schema']
        logger.info(f"Generated schema: {json.dumps(schema, indent=2)}")

        export_data = await generate_triples(schema, request)
        logger.info(f"Generated {len(export_data['triples'])} triples and {len(export_data['chunks'])} chunks")

        # Use json.dumps directly as export_data is already a dictionary
        json_content = json.dumps(export_data, indent=2)
        
        headers = {
            "Content-Disposition": 'attachment; filename="triples_and_chunks.json"',
            "Content-Type": "application/json"
        }
        
        logger.info("Sending response with triples and chunks")
        return Response(content=json_content, headers=headers)

    except ValidationError as e:
        logger.error(f"Validation error: {e.json()}")
        error_details = e.errors()
        logger.error(f"Detailed validation errors: {json.dumps(jsonable_encoder(error_details), indent=2)}")
        raise HTTPException(status_code=422, detail=error_details)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")