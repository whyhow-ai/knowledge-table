"""Graph service."""

import json
import logging
from typing import Any, Dict, List, Optional, Union

from whyhow import Node, Relation, Triple

from knowledge_table_api.dependencies import get_llm_service
from knowledge_table_api.models.graph import ExportData, Table
from knowledge_table_api.services.llm import generate_schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def to_dict(obj: Any) -> Dict[str, Any]:
    """Convert an object to a dictionary."""
    return obj.dict() if hasattr(obj, "dict") else obj.model_dump()


async def parse_table(data: Table) -> Dict[str, Any]:
    """Prepare the table data for schema generation."""
    # Parse and prepare data
    table_data = []

    for row in data.rows:
        document_data: Dict[str, Any] = {
            "document_name": row.document.name,
            "document_id": row.document.id,
            "answers": [],
        }

        for cell in data.cells:
            if cell.rowId == row.id:
                column = next(
                    (col for col in data.columns if col.id == cell.columnId),
                    None,
                )
                if column:
                    answer_data = {
                        "entity_type": column.prompt.entityType,
                        "answer": (
                            cell.answer.answer
                            if cell.answer.answer is not None
                            else ""
                        ),
                        "type": column.prompt.type,
                        "query": column.prompt.query,
                        "chunks": (
                            cell.answer.chunks
                            if cell.answer.chunks is not None
                            else []
                        ),
                    }
                    document_data["answers"].append(answer_data)

        table_data.append(document_data)

    return {"table_data": table_data}


def clean_answer(answer: Any) -> Union[str, int, float, bool, None]:
    """Clean and validate the answer."""
    if isinstance(answer, (int, float, bool)):
        return answer
    elif isinstance(answer, str):
        return answer.strip() if answer.strip() else None
    elif isinstance(answer, list):
        return ", ".join(str(item) for item in answer if item)
    return None


def triple_to_dict(triple: Triple) -> Optional[Dict[str, Any]]:
    """Convert a Triple object to a dictionary."""
    if triple.head.name == "" or triple.tail.name == "":
        logger.warning(f"Skipping triple with empty name: {triple}")
        return None
    return {
        "triple_id": triple.triple_id,
        "head": {"label": triple.head.label, "name": triple.head.name},
        "tail": {"label": triple.tail.label, "name": triple.tail.name},
        "relation": {"name": triple.relation.name},
        "chunk_ids": triple.chunk_ids,
    }


async def generate_triples(
    schema: Dict[str, Any], table_data: Table
) -> Dict[str, Any]:
    """Generate triples and chunks from the given schema and table data."""
    triples: List[Triple] = []
    chunks: List[Dict[str, Any]] = []
    logger.info(
        f"Processing schema with {len(schema['relationships'])} relationships"
    )
    logger.info(
        f"Table data has {len(table_data.rows)} rows, {len(table_data.columns)} columns, and {len(table_data.cells)} cells"
    )

    for relationship in schema["relationships"]:
        for row in table_data.rows:
            logger.info(f"Processing row: {row.id}")
            triple_id = f"t{len(triples) + 1}"
            # Set head_column and tail_column to the entityType directly
            head_entity_type = relationship["head"]
            tail_entity_type = relationship["tail"]

            # Find the corresponding columns based on entityType
            head_column = next(
                (
                    col
                    for col in table_data.columns
                    if col.prompt.entityType == head_entity_type
                ),
                None,
            )
            tail_column = next(
                (
                    col
                    for col in table_data.columns
                    if col.prompt.entityType == tail_entity_type
                ),
                None,
            )

            logger.info(
                f"Head column: {head_column.id if head_column else 'None'}, Tail column: {tail_column.id if tail_column else 'None'}"
            )
            # Initialize head_value and tail_value
            head_value = None
            tail_value = None

            if head_column:
                head_cell = next(
                    (
                        cell
                        for cell in table_data.cells
                        if cell.columnId == head_column.id
                        and cell.rowId == row.id
                    ),
                    None,
                )
                head_value = head_cell.answer.answer if head_cell else None
            else:
                logger.warning(
                    f"No head column found for relationship: {relationship}"
                )

            if tail_column:
                tail_cell = next(
                    (
                        cell
                        for cell in table_data.cells
                        if cell.columnId == tail_column.id
                        and cell.rowId == row.id
                    ),
                    None,
                )
                tail_value = tail_cell.answer.answer if tail_cell else None
            else:
                logger.warning(
                    f"No tail column found for relationship: {relationship}"
                )

            logger.info(f"Head value: {head_value}, Tail value: {tail_value}")

            if head_value is not None and tail_value is not None:

                # Remove empty values
                if head_value == "" or tail_value == "":
                    logger.warning(
                        f"Skipping triple creation due to empty value. Head: '{head_value}', Tail: '{tail_value}'"
                    )
                    continue

                head_label = (
                    "Document"
                    if relationship["head"] == "Document"
                    else relationship["head"]
                )
                tail_label = relationship["tail"]

                triple = Triple(
                    triple_id=triple_id,
                    head=Node(label=head_label, name=str(head_value)),
                    tail=Node(label=tail_label, name=str(tail_value)),
                    relation=Relation(name=relationship["relation"]),
                    chunk_ids=[],
                )
                triples.append(triple)
                logger.info(f"Created triple: {triple}")

                # Generate chunks for both head and tail
                for column_id, cell in [
                    (head_column.id if head_column else None, head_cell),
                    (tail_column.id if tail_column else None, tail_cell),
                ]:
                    if column_id and cell and cell.answer.chunks:
                        for i, chunk in enumerate(cell.answer.chunks):
                            chunk_id = f"{triple_id}_{column_id}_c{i+1}"
                            chunks.append(
                                {
                                    "chunk_id": chunk_id,
                                    "content": chunk.get("content", ""),
                                    "page": chunk.get("page", ""),
                                    "triple_id": triple_id,
                                }
                            )
                            if triple.chunk_ids is None:
                                triple.chunk_ids = []
                            triple.chunk_ids.append(chunk_id)
                        logger.info(
                            f"Added {len(cell.answer.chunks)} chunks for column {column_id}"
                        )
            else:
                logger.warning(
                    f"Skipping triple creation due to missing values. Head: {head_value}, Tail: {tail_value}"
                )

    logger.info(f"Generated {len(triples)} triples and {len(chunks)} chunks")
    # In the generate_triples function, modify the return statement:
    return {
        "triples": [
            t
            for t in (triple_to_dict(triple) for triple in triples)
            if t is not None
        ],
        "chunks": chunks,
    }


async def process_table_and_generate_triples(table_data: Table) -> ExportData:
    """Process the table data, generate a schema, and create triples."""
    llm_service = get_llm_service()
    schema_result = await generate_schema(llm_service, table_data)
    schema = schema_result["schema"]

    # Print the schema in a readable format
    logger.info("Generated Schema:")
    logger.info(json.dumps(schema, indent=2))

    triples_data = await generate_triples(schema, table_data)
    return ExportData(**triples_data)
