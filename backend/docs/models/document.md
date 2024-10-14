# Document Model

This file defines the `Document` model using Pydantic.

## Class: Document

Inherits from: `pydantic.BaseModel`

### Attributes:

- `id` (str): The unique identifier for the document.
- `name` (str): The name of the document.
- `author` (str): The author of the document.
- `tag` (str): A tag associated with the document.
- `page_count` (int): The number of pages in the document.

### Usage:

```python
from app.models.document import Document

doc = Document(
    id="123",
    name="Sample Document",
    author="John Doe",
    tag="sample",
    page_count=10
)
```

This model is used to represent and validate document data in the application.