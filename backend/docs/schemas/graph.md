# Graph Schemas

This file defines Pydantic schemas for the graph API, including structures for prompts, table components, and export requests/responses.

## Class: Prompt

Represents a prompt used to extract specific information.

### Attributes:
- `entityType` (str): The type of entity the prompt is associated with.
- `id` (str): Unique identifier for the prompt.
- `query` (str): The query text of the prompt.
- `rules` (List[Any]): List of rules associated with the prompt.
- `type` (str): The type of the prompt.

## Class: Cell

Represents a cell in a table.

### Attributes:
- `answer` (Dict[str, Any]): The answer content of the cell.
- `columnId` (str): The ID of the column this cell belongs to.
- `dirty` (Union[bool, str]): Indicates if the cell has been modified.
- `rowId` (str): The ID of the row this cell belongs to.

## Class: Column

Represents a column in a table.

### Attributes:
- `id` (str): Unique identifier for the column.
- `prompt` (Prompt): The prompt associated with this column.
- `width` (Union[int, str]): The width of the column.
- `hidden` (Union[bool, str]): Indicates if the column is hidden.

## Class: Document

Represents a document.

### Attributes:
- `id` (str): Unique identifier for the document.
- `name` (str): The name of the document.
- `author` (str): The author of the document.
- `tag` (str): A tag associated with the document.
- `page_count` (Union[int, str]): The number of pages in the document.

## Class: Row

Represents a row in a table.

### Attributes:
- `id` (str): Unique identifier for the row.
- `document` (Document): The document associated with this row.
- `hidden` (Union[bool, str]): Indicates if the row is hidden.

## Class: Table

Represents a table.

### Attributes:
- `columns` (List[Column]): List of columns in the table.
- `rows` (List[Row]): List of rows in the table.
- `cells` (List[Cell]): List of cells in the table.

## Class: ExportTriplesRequest

Schema for export triples request.

### Attributes:
- `columns` (List[Column]): List of columns in the table.
- `rows` (List[Row]): List of rows in the table.
- `cells` (List[Cell]): List of cells in the table.

## Class: ExportTriplesResponse

Schema for export triples response.

### Attributes:
- `triples` (List[Dict[str, Any]]): List of triples exported.
- `chunks` (List[Dict[str, Any]]): List of chunks associated with the triples.

## Usage

```python
from app.schemas.graph import Prompt, Cell, Column, Document, Row, Table, ExportTriplesRequest, ExportTriplesResponse

# Creating a prompt
prompt = Prompt(entityType="Person", id="1", query="What is the person's name?", rules=[], type="text")

# Creating a cell
cell = Cell(answer={"text": "John Doe"}, columnId="1", dirty=False, rowId="1")

# Creating a column
column = Column(id="1", prompt=prompt, width=100, hidden=False)

# Creating a document
document = Document(id="1", name="Sample Doc", author="Jane Doe", tag="sample", page_count=10)

# Creating a row
row = Row(id="1", document=document, hidden=False)

# Creating a table
table = Table(columns=[column], rows=[row], cells=[cell])

# Creating an export request
export_request = ExportTriplesRequest(columns=[column], rows=[row], cells=[cell])

# Creating an export response
export_response = ExportTriplesResponse(triples=[{"subject": "John", "predicate": "is", "object": "Person"}], chunks=[{"id": "1", "text": "John is a person"}])
````


These schemas are used to validate and structure data for the graph API in the application, including table structures and export operations.