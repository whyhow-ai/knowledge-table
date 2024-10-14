# Graph Models

This file defines various models related to the knowledge graph using Pydantic.

## Class: Chunk

Represents a chunk of content with associated metadata.

### Attributes:
- `chunk_id` (str): Unique identifier for the chunk.
- `content` (str): The content of the chunk.
- `page` (Union[int, str]): The page number or identifier.
- `triple_id` (str): The ID of the associated triple.

## Class: Document

Represents a document in the system.

### Attributes:
- `id` (str): Unique identifier for the document.
- `name` (str): The name of the document.

## Class: Node

Represents a node in the knowledge graph.

### Attributes:
- `label` (str): The label of the node.
- `name` (str): The name of the node.

## Class: Relation

Represents a relationship between two nodes in the knowledge graph.

### Attributes:
- `name` (str): The name of the relation.

## Class: Triple

Represents a triple in the knowledge graph.

### Attributes:
- `triple_id` (str): Unique identifier for the triple.
- `head` (Node): The head node of the triple.
- `tail` (Node): The tail node of the triple.
- `relation` (Relation): The relation between the head and tail nodes.
- `chunk_ids` (List[str]): List of associated chunk IDs.

## Class: ExportData

Represents the exported data containing triples and content chunks.

### Attributes:
- `triples` (List[Triple]): List of triples in the exported data.
- `chunks` (List[Dict[str, Any]]): List of chunks in the exported data.

### Usage:

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
````


These models are used to represent and validate graph-related data in the application.