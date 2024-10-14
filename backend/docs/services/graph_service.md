# Graph Service

The Graph Service module is responsible for processing table data, generating schemas, and creating triples (subject-predicate-object relationships) from the data. It's a crucial component in transforming structured table data into a graph representation.

## Functions

### parse_table

````python
async def parse_table(data: Table) -> Dict[str, Any]:
````


Prepares the table data for schema generation.

**Parameters:**
- `data` (Table): The input table data containing rows, columns, and cells.

**Returns:**
- `Dict[str, Any]`: A dictionary containing parsed table data with document information and answers for each cell.

### generate_triples

````python
async def generate_triples(schema: SchemaResponseModel, table_data: Table) -> Dict[str, Any]:
````


Generates triples and chunks from the given schema and table data.

**Parameters:**
- `schema` (SchemaResponseModel): The schema containing relationships between entities.
- `table_data` (Table): The table data to process.

**Returns:**
- `Dict[str, Any]`: A dictionary containing generated triples and chunks.

### generate_triples_for_relationship

````python
def generate_triples_for_relationship(relationship: SchemaRelationship, table_data: Table) -> List[Triple]:
````


Generates triples for a single relationship across all rows in the table.

**Parameters:**
- `relationship` (SchemaRelationship): The relationship schema to use for triple generation.
- `table_data` (Table): The table data containing rows to process.

**Returns:**
- `List[Triple]`: A list of generated Triple objects for the given relationship.

### create_triple_for_row

````python
def create_triple_for_row(relationship: SchemaRelationship, row: Row, table_data: Table) -> Optional[Triple]:
````


Creates a single triple for a given relationship and row.

**Parameters:**
- `relationship` (SchemaRelationship): The relationship schema to use for triple creation.
- `row` (Row): The row data to process.
- `table_data` (Table): The complete table data for context.

**Returns:**
- `Optional[Triple]`: A Triple object if both head and tail values are found, None otherwise.

### get_cell_value

````python
def get_cell_value(entity_type: str, row: Row, table_data: Table) -> Optional[str]:
````


Gets the cell value for a given entity type and row.

**Parameters:**
- `entity_type` (str): The entity type to look for in the table columns.
- `row` (Row): The row data to process.
- `table_data` (Table): The complete table data for context.

**Returns:**
- `Optional[str]`: The cell value if found, None otherwise.

### get_label

````python
def get_label(entity_type: str) -> str:
````


Gets the label for an entity type.

**Parameters:**
- `entity_type` (str): The entity type to get the label for.

**Returns:**
- `str`: 'Document' if the entity_type is 'Document', otherwise returns the entity_type itself.

### generate_chunks_for_triples

````python
def generate_chunks_for_triples(triples: List[Triple], table_data: Table) -> List[Dict[str, Any]]:
````


Generates chunks for a list of triples.

**Parameters:**
- `triples` (List[Triple]): The list of triples to generate chunks for.
- `table_data` (Table): The complete table data for context.

**Returns:**
- `List[Dict[str, Any]]`: A list of chunk dictionaries generated for all triples.

### generate_chunks_for_triple

````python
def generate_chunks_for_triple(triple: Triple, table_data: Table) -> List[Dict[str, Any]]:
````


Generates chunks for a single triple.

**Parameters:**
- `triple` (Triple): The triple to generate chunks for.
- `table_data` (Table): The complete table data for context.

**Returns:**
- `List[Dict[str, Any]]`: A list of chunk dictionaries generated for the given triple.

### process_table_and_generate_triples

````python
async def process_table_and_generate_triples(table_data: Table) -> ExportData:
````


Processes the table data, generates a schema, and creates triples.

**Parameters:**
- `table_data` (Table): The input table data to process.

**Returns:**
- `ExportData`: An ExportData object containing the generated triples and chunks.

## Usage

The main entry point for using this service is the `process_table_and_generate_triples` function. It orchestrates the entire process of generating triples from table data:

1. Obtains an LLM (Language Model) service.
2. Generates a schema using the LLM service.
3. Creates triples based on the generated schema and table data.

Example usage:

````python
table_data = Table(...)  # Your table data
export_data = await process_table_and_generate_triples(table_data)
````


## Error Handling

The service includes extensive error handling and logging. Errors are logged for debugging purposes, and the service aims to gracefully handle exceptions to prevent application crashes.

## Dependencies

This service depends on:
- `whyhow` library for Node, Relation, and Triple classes
- `app.core.dependencies` for getting the LLM service
- `app.models.graph` for ExportData model
- `app.models.llm` for SchemaRelationship and SchemaResponseModel
- `app.schemas.graph` for Row and Table schemas
- `app.services.llm_service` for generating schemas

Ensure all these dependencies are properly installed and configured in your environment.