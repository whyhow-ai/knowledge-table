# Document Schemas

This file defines Pydantic schemas for API requests and responses related to documents.

## Class: DocumentCreate

Schema for creating a new document.

### Attributes:
- `name` (str): The name of the document.
- `author` (str): The author of the document.
- `tag` (str): A tag associated with the document.
- `page_count` (Annotated[int, Field(strict=True, gt=0)]): The number of pages in the document. This field is strictly validated to ensure it's a positive integer.

## Class: DocumentResponse

Schema for document response, inheriting from the Document model.

### Attributes:
Inherits all attributes from the `Document` model:
- `id` (str): The unique identifier for the document.
- `name` (str): The name of the document.
- `author` (str): The author of the document.
- `tag` (str): A tag associated with the document.
- `page_count` (int): The number of pages in the document.

## Class: DeleteDocumentResponse

Schema for delete document response.

### Attributes:
- `id` (str): The ID of the deleted document.
- `status` (str): The status of the delete operation.
- `message` (str): A message describing the result of the delete operation.

## Usage

```python
from app.schemas.document import DocumentCreate, DocumentResponse, DeleteDocumentResponse

# Creating a new document
new_doc = DocumentCreate(
    name="Sample Document",
    author="John Doe",
    tag="sample",
    page_count=10
)

# Document response
doc_response = DocumentResponse(
    id="123",
    name="Sample Document",
    author="John Doe",
    tag="sample",
    page_count=10
)

# Delete document response
delete_response = DeleteDocumentResponse(
    id="123",
    status="success",
    message="Document successfully deleted"
)
````


These schemas are used to validate and structure data for API requests and responses related to documents in the application.