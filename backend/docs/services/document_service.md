# Document Service

The `DocumentService` handles document uploads, processing, and storage in the Knowledge Table backend.

The service uses:

- **VectorDBService**: For storing document vectors.
- **LLMService**: For language model operations.
- **LoaderFactory** and **RecursiveCharacterTextSplitter**: For document loading and splitting.

---

## Core Functions

**upload_document**  
 Uploads and processes a document.

```python
async def upload_document(self, filename: str, file_content: bytes) -> Optional[str]
```

Parameters:

- `filename`: The name of the file.
- `file_content`: Binary file content.

Returns:

- Document ID (`str`) if successful, otherwise `None`.

Process:

1. Generates a document ID.
2. Saves file content temporarily.
3. Splits the document into chunks.
4. Uses LLM service (if available) to process and store chunks.
5. Deletes temporary file.

**\_process_document**  
 Loads and splits a document into chunks.

```python
async def _process_document(self, file_path: str) -> List[LangchainDocument]
```

**\_load_document**  
 Loads the document using the designated loader.

```python
async def _load_document(self, file_path: str) -> List[LangchainDocument]
```

_Raises `ValueError` if no loader is found._

**\_generate_document_id**  
 Generates a unique document ID.

```python
@staticmethod
def _generate_document_id() -> str
```

---

## Usage

```python
vector_db_service = VectorDBFactory.create_vector_db_service(...)
llm_service = LLMFactory.get_llm_service(...)
document_service = DocumentService(vector_db_service, llm_service)

document_id = await document_service.upload_document("example.pdf", file_content)
if document_id:
    print(f"Document uploaded successfully with ID: {document_id}")
else:
    print("Failed to upload document")
```

---

## Configuration

Settings used by `DocumentService`:

- `chunk_size`: Size for document chunks.
- `chunk_overlap`: Overlap between chunks.
- `loader`: Document loader type.

Configure these in the application’s configuration file.

---

## Error Handling

Includes error handling and logging for:

- Upload and processing failures
- LLM service unavailability
- Document loading issues

Errors are logged with levels (`INFO`, `WARNING`, `ERROR`) to aid debugging. Exceptions are managed to ensure stability, with detailed messages in `upload_document` for specific failure scenarios.

---

## Dependencies

- **settings** from `app.core.config`: Manages configuration options like `chunk_size`, `chunk_overlap`, and loader type.
- **LoaderFactory** from `app.services.loaders.factory`: Creates loaders based on configuration.
- **VectorDBService** and **LLMService**: Provide vector embedding and language model functionality.
- **RecursiveCharacterTextSplitter** from `langchain.text_splitter`: Splits documents into manageable chunks.

---

## Models

### Document

The `Document` model, built with Pydantic, validates and represents document data within the application.

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

Attributes:

- `id` (str): Unique identifier for the document.
- `name` (str): Document name.
- `author` (str): Document author.
- `tag` (str): Tag associated with the document.
- `page_count` (int): Total number of pages in the document.
