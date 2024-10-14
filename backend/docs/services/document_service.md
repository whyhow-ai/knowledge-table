# Document Service

The `DocumentService` is responsible for handling document-related operations in the Knowledge Table backend. It manages the process of uploading, processing, and storing documents in the vector database.

## Class: DocumentService

### Initialization

```python
def __init__(self, vector_db_service: VectorDBService, llm_service: LLMService):
```

- `vector_db_service`: An instance of a `VectorDBService` for storing document vectors.
- `llm_service`: An instance of an `LLMService` for language model operations.

The service also initializes a `LoaderFactory` and a `RecursiveCharacterTextSplitter` for document processing.

### Methods

#### upload_document

```python
async def upload_document(self, filename: str, file_content: bytes) -> Optional[str]:
```

Uploads and processes a document.

- `filename`: The name of the file being uploaded.
- `file_content`: The binary content of the file.

Returns:
- A `str` containing the generated document ID if successful, or `None` if an error occurred.

Process:
1. Generates a unique document ID.
2. Saves the file content to a temporary file.
3. Processes the document, splitting it into chunks.
4. If the LLM service is available, prepares and upserts the chunks into the vector database.
5. Cleans up the temporary file.

#### _process_document (private)

```python
async def _process_document(self, file_path: str) -> List[LangchainDocument]:
```

Processes a document by loading and splitting it into chunks.

- `file_path`: The path to the document file.

Returns:
- A list of `LangchainDocument` objects representing the document chunks.

#### _load_document (private)

```python
async def _load_document(self, file_path: str) -> List[LangchainDocument]:
```

Loads a document using the appropriate loader.

- `file_path`: The path to the document file.

Returns:
- A list of `LangchainDocument` objects representing the loaded document.

Raises:
- `ValueError` if no loader is available for the configured loader type.

#### _generate_document_id (static method)

```python
@staticmethod
def _generate_document_id() -> str:
```

Generates a unique document ID.

Returns:
- A string containing a hexadecimal UUID.

## Usage

The `DocumentService` is typically instantiated with a `VectorDBService` and an `LLMService`, and then used to upload and process documents:

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

## Configuration

The `DocumentService` uses the following configuration settings:

- `settings.chunk_size`: The size of document chunks for splitting.
- `settings.chunk_overlap`: The overlap between document chunks.
- `settings.loader`: The type of document loader to use.

These settings can be adjusted in the application's configuration file.

## Error Handling

The service includes error handling and logging for various scenarios, including:
- Failures during document upload or processing
- Unavailability of the LLM service
- Issues with document loading

Errors are logged for debugging purposes, and the service aims to gracefully handle exceptions to prevent application crashes.