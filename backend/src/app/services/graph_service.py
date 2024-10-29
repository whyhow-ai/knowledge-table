"""Graph service."""

import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.core.dependencies import get_llm_service
from app.models.graph import GraphChunk, Node, Relation, Triple
from app.models.llm_responses import SchemaRelationship, SchemaResponseModel
from app.models.table import Table, TableRow
from app.schemas.graph_api import ExportTriplesResponseSchema
from app.services.llm_service import generate_schema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def parse_table(data: Table) -> Dict[str, Any]:
    """
    Prepare the table data for schema generation.

    Parameters
    ----------
    data : Table
        The input table data containing rows, columns, and cells.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing parsed table data with document
        information and answers for each cell.
    """
    table_data: List[Dict[str, Any]] = []

    # Parse the table data into a list of dictionaries
    for row in data.rows:
        document_data: Dict[str, Any] = {
            "document_name": row.document.name,
            "document_id": row.document.id,
            "answers": [],
        }

        # Parse the cells into answer data
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
                            cell.answer.get("answer")
                            if cell.answer.get("answer") is not None
                            else ""
                        ),
                        "type": column.prompt.type,
                        "query": column.prompt.query,
                        "chunks": cell.answer.get("chunks", []),
                    }
                    document_data["answers"].append(answer_data)

        table_data.append(document_data)

    return {"table_data": table_data}


async def generate_triples(
    schema: SchemaResponseModel, table_data: Table
) -> ExportTriplesResponseSchema:
    """
    Generate triples and chunks from the given schema and table data.

    Parameters
    ----------
    schema : SchemaResponseModel
        The schema containing relationships between entities.
    table_data : Table
        The table data to process, containing rows, columns, and cells.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing generated triples and chunks.
        The 'triples' key contains a list of triple dictionaries, and the 'chunks'
        key contains a list of chunk dictionaries.
    """
    # Convert the schema to a SchemaResponseModel if it's a dictionary
    if isinstance(schema, dict):
        try:
            schema = SchemaResponseModel(**schema)
        except Exception as e:
            logger.error(f"Error converting dict to SchemaResponseModel: {e}")
            raise ValueError(f"Invalid schema format: {e}")
    elif not isinstance(schema, SchemaResponseModel):
        raise TypeError(
            f"Expected SchemaResponseModel or dict, got {type(schema)}"
        )

    # Check if relationships is None and set it to an empty list if it is
    if schema.relationships is None:
        schema.relationships = []

    logger.info(
        f"Processing schema with {len(schema.relationships)} relationships"
    )
    logger.info(
        f"Table data has {len(table_data.rows)} rows, {len(table_data.columns)} columns, and {len(table_data.cells)} cells"
    )

    triples: List[Triple] = []
    chunks: List[GraphChunk] = []

    # Generate triples and chunks for each relationship
    for relationship in schema.relationships:
        logger.info(f"Processing relationship: {relationship}")
        triples_for_relationship = generate_triples_for_relationship(
            relationship, table_data
        )

        # for triple in triples_for_relationship:
        #     print(f"Triple: {triple}")
        #     head_node = Node(
        #         label=relationship.head,
        #         name=str(triple.head.name)
        #     )
        #     tail_node = Node(
        #         label=relationship.tail,
        #         name=str(triple.tail.name)
        #     )
        #     relation = Relation(name=relationship.relation)
        #     triples.append(
        #         Triple(
        #             triple_id=str(uuid.uuid4()),
        #             head=head_node,
        #             tail=tail_node,
        #             relation=relation,
        #             chunk_ids=[],
        #         )
        #     )

        chunks.extend(
            generate_chunks_for_triples(triples_for_relationship, table_data)
        )

    logger.info(f"Generated {len(triples)} triples and {len(chunks)} chunks")

    return ExportTriplesResponseSchema(
        triples=triples_for_relationship, chunks=chunks
    )


def generate_triples_for_relationship(
    relationship: SchemaRelationship, table_data: Table
) -> List[Triple]:
    """
    Generate triples for a single relationship across all rows in the table.

    Parameters
    ----------
    relationship : SchemaRelationship
        The relationship schema to use for triple generation.
    table_data : Table
        The table data containing rows to process.

    Returns
    -------
    List[Triple]
        A list of generated Triple objects for the given relationship.
    """
    triples = []
    for row in table_data.rows:
        try:
            triple = create_triple_for_row(relationship, row, table_data)
            if triple:
                triples.append(triple)
        except Exception as e:
            logger.error(f"Error creating triple for row {row.id}: {str(e)}")
    return triples


def create_triple_for_row(
    relationship: SchemaRelationship, row: TableRow, table_data: Table
) -> Optional[Triple]:
    """
    Create a single triple for a given relationship and row.

    Parameters
    ----------
    relationship : SchemaRelationship
        The relationship schema to use for triple creation.
    row : Row
        The row data to process.
    table_data : Table
        The complete table data for context.

    Returns
    -------
    Optional[Triple]
        A Triple object if both head and tail values are found, None otherwise.
    """
    head_value = get_cell_value(relationship.head, row, table_data)
    tail_value = get_cell_value(relationship.tail, row, table_data)

    if head_value and tail_value:
        triple_id = f"t{uuid.uuid4()}"
        return Triple(
            triple_id=triple_id,
            head=Node(
                label=get_label(relationship.head),
                name=str(head_value),
                properties=(
                    {"document": row.document.name} if row.document else {}
                ),
            ),
            tail=Node(
                label=relationship.tail,
                name=str(tail_value),
                properties=(
                    {"document": row.document.name} if row.document else {}
                ),
            ),
            relation=Relation(name=relationship.relation),
            chunk_ids=[],
        )
    return None


def get_cell_value(
    entity_type: str, row: TableRow, table_data: Table
) -> Optional[str]:
    """
    Get the cell value for a given entity type and row.

    Parameters
    ----------
    entity_type : str
        The entity type to look for in the table columns.
    row : Row
        The row data to process.
    table_data : Table
        The complete table data for context.

    Returns
    -------
    Optional[str]
        The cell value if found, None otherwise.
    """
    try:
        column = next(
            (
                col
                for col in table_data.columns
                if col.prompt.entityType == entity_type
            ),
            None,
        )
        if not column:
            logger.warning(f"No column found for entity type: {entity_type}")
            return None

        cell = next(
            (
                cell
                for cell in table_data.cells
                if cell.rowId == row.id and cell.columnId == column.id
            ),
            None,
        )
        return cell.answer.get("answer") if cell else None
    except Exception as e:
        logger.error(
            f"Error getting cell value for entity type {entity_type}: {str(e)}"
        )
        return None


def get_label(entity_type: str) -> str:
    """
    Get the label for an entity type.

    Parameters
    ----------
    entity_type : str
        The entity type to get the label for.

    Returns
    -------
    str
        'Document' if the entity_type is 'Document', otherwise returns the entity_type itself.
    """
    return "Document" if entity_type == "Document" else entity_type


def generate_chunks_for_triples(
    triples: List[Triple], table_data: Table
) -> List[GraphChunk]:
    """
    Generate chunks for a list of triples.

    Parameters
    ----------
    triples : List[Triple]
        The list of triples to generate chunks for.
    table_data : Table
        The complete table data for context.

    Returns
    -------
    List[GraphChunk]
        A list of chunk dictionaries generated for all triples.
    """
    chunks = []
    for triple in triples:
        chunks.extend(generate_chunks_for_triple(triple, table_data))
    return chunks


def generate_chunks_for_triple(
    triple: Triple, table_data: Table
) -> List[GraphChunk]:
    """
    Generate chunks for a single triple.

    Parameters
    ----------
    triple : Triple
        The triple to generate chunks for.
    table_data : Table
        The complete table data for context.

    Returns
    -------
    List[GraphChunk]
        A list of chunk dictionaries generated for the given triple.
        Each chunk dictionary contains 'chunk_id', 'content', 'page', and 'triple_id'.
    """
    chunks = []

    # Find the chunks for the head and tail nodes
    for node in [triple.head, triple.tail]:
        column = next(
            (
                col
                for col in table_data.columns
                if col.prompt.entityType == node.label
            ),
            None,
        )
        if column:
            cell = next(
                (
                    cell
                    for cell in table_data.cells
                    if cell.columnId == column.id
                    and cell.answer.get("answer") == node.name
                ),
                None,
            )
            if cell and cell.answer.get("chunks"):
                for i, chunk in enumerate(cell.answer["chunks"]):
                    chunk_id = f"{triple.triple_id}_{column.id}_c{i+1}"
                    chunks.append(
                        GraphChunk(
                            chunk_id=chunk_id,
                            content=chunk.content,
                            page=chunk.page,
                            triple_id=triple.triple_id,
                        )
                    )
                    if triple.chunk_ids is None:
                        triple.chunk_ids = []
                    triple.chunk_ids.append(chunk_id)
    return chunks


async def process_table_and_generate_triples(
    table_data: Table,
) -> ExportTriplesResponseSchema:
    """
    Process the table data, generate a schema, and create triples.

    This function orchestrates the entire process of generating triples from table data:
    1. Obtains an LLM service.
    2. Generates a schema using the LLM service.
    3. Creates triples based on the generated schema and table data.

    Parameters
    ----------
    table_data : Table
        The input table data to process.

    Returns
    -------
    ExportData
        An ExportData object containing the generated triples and chunks.
    """
    # Get the LLM service
    llm_service = get_llm_service()
    if llm_service is None:
        logger.error("Failed to create LLM service")
        return ExportTriplesResponseSchema(triples=[], chunks=[])

    try:
        # Generate the schema
        schema_result = await generate_schema(llm_service, table_data)

        if not schema_result or "schema" not in schema_result:
            logger.error("Failed to generate schema: Invalid schema result")
            return ExportTriplesResponseSchema(triples=[], chunks=[])

        # Convert the schema to a SchemaResponseModel
        schema_dict = schema_result["schema"]
        schema = SchemaResponseModel(
            relationships=[
                SchemaRelationship(**rel)
                for rel in schema_dict.get("relationships", [])
            ]
        )

        logger.info("Generated Schema:")
        logger.info(json.dumps(schema.model_dump(), indent=2))

        if not schema.relationships:
            logger.warning("Generated schema has no relationships")
            return ExportTriplesResponseSchema(triples=[], chunks=[])

        # Generate triples
        triples_data = await generate_triples(schema, table_data)

        if not triples_data:
            logger.warning("No triples generated from the schema")
            return ExportTriplesResponseSchema(triples=[], chunks=[])

        return triples_data

    except Exception as e:
        logger.exception(
            f"Unexpected error in process_table_and_generate_triples: {e}"
        )
        return ExportTriplesResponseSchema(triples=[], chunks=[])
