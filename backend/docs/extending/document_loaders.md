# Extending Document Loaders

This guide explains how to add support for new document loader services in the Knowledge Table backend.

## Steps to Add a New Document Loader

1. **Create a new Loader service class**

   In `src/app/services/loaders/`, create a new file `your_loader_service.py`.

   ```python
   # your_loader_service.py
   from typing import List, Optional
   from langchain.schema import Document
   from app.services.loaders.base import LoaderService

   class YourLoader(LoaderService):
       def __init__(self, api_key: Optional[str] = None):
           """Initialize the YourLoader."""
           self.api_key = api_key

       async def load(self, file_path: str) -> List[Document]:
           """Load document from file path."""
           # Implement your loading logic here
           pass

       async def load_and_split(self, file_path: str) -> List[Document]:
           """Load and split document from file path."""
           # Implement your loading and splitting logic here
           pass
   ```

2. **Update the Loader Factory**

   In `src/app/services/loaders/factory.py`, import your new service and update the factory method.

   ```python
   # factory.py
   from app.services.loaders.your_loader_service import YourLoader

   class LoaderFactory:
       @staticmethod
       def create_loader() -> Optional[LoaderService]:
           loader_type = settings.loader
           logger.info(f"Creating loader of type: {loader_type}")

           try:
               if loader_type == "unstructured":
                   # ... existing unstructured loader code ...
               elif loader_type == "pypdf":
                   # ... existing pypdf loader code ...
               elif loader_type == "your_loader":
                   logger.info("Using YourLoader")
                   return YourLoader(api_key=settings.your_loader_api_key)
               else:
                   logger.warning(f"No loader found for type: {loader_type}")
                   return None
           except ValueError as ve:
               logger.error(f"Error creating loader: {str(ve)}")
               raise
           except Exception as e:
               logger.exception(f"Error creating loader: {str(e)}")
               return None
   ```

3. **Configure the Service**

   In `src/app/core/config.py`, add configuration options for your loader.

   ```python
   # config.py
   from pydantic import BaseSettings

   class Settings(BaseSettings):
       loader: str = "unstructured"  # Default to unstructured
       your_loader_api_key: Optional[str] = None

   settings = Settings()
   ```

   Update your environment variable or `.env` file accordingly:

   ```
   LOADER=your_loader
   YOUR_LOADER_API_KEY=your_api_key_here
   ```

4. **Implement the Loader Logic**

   In your `YourLoader` class, implement the `load` and `load_and_split` methods according to your loader's specific requirements.

   ```python
   async def load(self, file_path: str) -> List[Document]:
       # Example implementation
       your_loader = YourLoaderLibrary(api_key=self.api_key)
       raw_document = your_loader.load_file(file_path)
       return [Document(page_content=raw_document, metadata={"source": file_path})]

   async def load_and_split(self, file_path: str) -> List[Document]:
       # Example implementation
       your_loader = YourLoaderLibrary(api_key=self.api_key)
       raw_document = your_loader.load_file(file_path)
       splits = your_loader.split_document(raw_document)
       return [Document(page_content=split, metadata={"source": file_path, "split": i}) for i, split in enumerate(splits)]
   ```

## Additional Considerations

- **Error Handling**: Implement proper error handling in your loader service.
- **Testing**: Write unit tests for your new loader service.
- **Performance**: Consider optimizing your implementation for large documents.
- **Metadata**: Ensure your loader captures relevant metadata from the documents.
- **Compatibility**: Make sure your loader returns `langchain.schema.Document` objects for compatibility with the rest of the system.

## Example: Implementing a PDF Loader

Here's a simplified example of how the PDFLoader is implemented:

```python
from typing import List
from langchain.schema import Document
from langchain.document_loaders import PyPDFLoader as LangchainPyPDFLoader
from app.services.loaders.base import LoaderService

class PDFLoader(LoaderService):
    async def load(self, file_path: str) -> List[Document]:
        loader = LangchainPyPDFLoader(file_path)
        return loader.load()

    async def load_and_split(self, file_path: str) -> List[Document]:
        loader = LangchainPyPDFLoader(file_path)
        return loader.load_and_split()
```

This example shows how to leverage existing libraries (in this case, Langchain's PyPDFLoader) to implement the required functionality.