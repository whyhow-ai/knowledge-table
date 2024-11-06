# Graph Service

The Graph Service processes table data, generates schemas, and creates triples (subject-predicate-object relationships) to represent data as a graph.

---

## Core Functions

**parse_table**  
 Prepares table data for schema generation.

```python
async def parse_table(data: Table) -> Dict[str, Any]
```

**generate_triples**  
 Generates triples and chunks based on the schema and table data.

```python
async def generate_triples(schema: SchemaResponseModel, table_data: Table) -> Dict[str, Any]
```

**generate_triples_for_relationship**  
 Creates triples for a specific relationship across all rows.

```python
def generate_triples_for_relationship(relationship: SchemaRelationship, table_data: Table) -> List[Triple]
```

**create_triple_for_row**  
 Generates a single triple for a relationship and row.

```python
def create_triple_for_row(relationship: SchemaRelationship, row: Row, table_data: Table) -> Optional[Triple]
```

**generate_chunks_for_triples**  
 Generates content chunks for each triple.

```python
def generate_chunks_for_triples(triples: List[Triple], table_data: Table) -> List[Dict[str, Any]]
```

---

## Helper Functions

**get_cell_value**  
 Retrieves the cell value for a specific entity type and row.

```python
def get_cell_value(entity_type: str, row: Row, table_data: Table) -> Optional[str]
```

**get_label**  
 Provides a label for an entity type, returning 'Document' if applicable.

```python
def get_label(entity_type: str) -> str
```

**generate_chunks_for_triple**  
 Generates chunks for a single triple, associating content snippets with it.

```python
def generate_chunks_for_triple(triple: Triple, table_data: Table) -> List[Dict[str, Any]]
```

---

## Usage

The primary function to use is `process_table_and_generate_triples`, which processes table data, generates a schema, and creates triples.

```python
table_data = Table(...)  # Your table data
export_data = await process_table_and_generate_triples(table_data)
```

---

## Configuration

The Graph Service relies on configurations set for processing data, schema generation, and LLM integration. Adjust these settings in the application’s configuration file.

---

## Error Handling

The Graph Service includes logging and error handling for:

- Data processing errors
- LLM service unavailability
- Table parsing and triple generation issues

Errors are logged for debugging, and exceptions are managed to maintain stability. Logs are categorized by levels (`INFO`, `WARNING`, `ERROR`) to trace processing steps.

---

## Dependencies

- **whyhow**: Provides `Node`, `Relation`, and `Triple` classes.
- **app.core.dependencies**: Includes `get_llm_service` for LLM integration.
- **app.services.llm_service**: Uses `generate_schema` for schema generation.

---

## Models

### Chunk

Represents a chunk of content with associated metadata.

```python
from app.models.graph import Chunk

chunk = Chunk(
    chunk_id="chunk1",
    content="John lives in New York.",
    page=1,
    triple_id="123"
)
```

Attributes:

- `chunk_id` (str): Unique identifier for the chunk.
- `content` (str): The content of the chunk.
- `page` (Union[int, str]): The page number or identifier.
- `triple_id` (str): The ID of the associated triple.

---

### Document

Represents a document in the system.

```python
from app.models.graph import Document

doc = Document(
    id="doc1",
    name="New York Travel Guide"
)
```

Attributes:

- `id` (str): Unique identifier for the document.
- `name` (str): The name of the document.

---

### Node

Represents a node in the knowledge graph.

```python
from app.models.graph import Node

node = Node(
    label="Person",
    name="John"
)
```

Attributes:

- `label` (str): The type of entity (e.g., "Person").
- `name` (str): The name of the node.

---

### Relation

Represents a relationship between two nodes in the knowledge graph.

```python
from app.models.graph import Relation

relation = Relation(
    name="lives_in"
)
```

Attributes:

- `name` (str): The name of the relation (e.g., "lives_in").

---

### Triple

Represents a triple in the knowledge graph.

```python
from app.models.graph import Triple

triple = Triple(
    triple_id="123",
    head=Node(label="Person", name="John"),
    tail=Node(label="City", name="New York"),
    relation=Relation(name="lives_in"),
    chunk_ids=["chunk1"]
)
```

Attributes:

- `triple_id` (str): Unique identifier for the triple.
- `head` (`Node`): The head node of the triple.
- `tail` (`Node`): The tail node of the triple.
- `relation` (`Relation`): The relation between the head and tail nodes.
- `chunk_ids` (List[str]): List of associated chunk IDs.

---

### ExportData

Represents the exported data containing triples and content chunks.

```python
from app.models.graph import ExportData, Triple, Node, Relation, Chunk

export_data = ExportData(
    triples=[
        Triple(
            triple_id="123",
            head=Node(label="Person", name="John"),
            tail=Node(label="City", name="New York"),
            relation=Relation(name="lives_in"),
            chunk_ids=["chunk1", "chunk2"]
        )
    ],
    chunks=[
        {
            "chunk_id": "chunk1",
            "content": "John lives in New York.",
            "page": 1,
            "triple_id": "123"
        }
    ]
)
```

Attributes:

- `triples` (List[`Triple`]): List of triples in the exported data.
- `chunks` (List[Dict[str, Any]]): List of chunks in the exported data, where each chunk includes `chunk_id`, `content`, `page`, and `triple_id`.
