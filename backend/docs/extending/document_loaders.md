# Extending Document Loaders

This guide covers adding new document loaders to the Knowledge Table backend, detailing the setup and configuration.

---

## Steps

### **1. Create a Loader Service Class**

In `src/app/services/loaders/`, create a new file, e.g., `your_loader_service.py`.

```python
# your_loader_service.py
from typing import List, Optional
from langchain.schema import Document
from app.services.loaders.base import LoaderService

class YourLoader(LoaderService):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    async def load(self, file_path: str) -> List[Document]:
        # Implement loading logic here
        pass

    async def load_and_split(self, file_path: str) -> List[Document]:
        # Implement loading and splitting logic here
        pass
```

### **2. Update the Loader Factory**

In `src/app/services/loaders/factory.py`, add an import and update the factory method.

```python
# factory.py
from app.services.loaders.your_loader_service import YourLoader

class LoaderFactory:
    @staticmethod
    def create_loader() -> Optional[LoaderService]:
        loader_type = settings.loader
        if loader_type == "your_loader":
            return YourLoader(api_key=settings.your_loader_api_key)
        # existing loader conditions...
```

### **3. Configure the Service**

In `src/app/core/config.py`, add configurations for the new loader:

```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    loader: str = "unstructured"
    your_loader_api_key: Optional[str] = None

settings = Settings()
```

Update your environment variables or `.env` file:

```
LOADER=your_loader
YOUR_LOADER_API_KEY=your_api_key_here
```

### **4. Implement Loader Logic**

Define `load` and `load_and_split` in `YourLoader` for your loader requirements.

```python
async def load(self, file_path: str) -> List[Document]:
    raw_document = YourLoaderLibrary(api_key=self.api_key).load_file(file_path)
    return [Document(page_content=raw_document, metadata={"source": file_path})]

async def load_and_split(self, file_path: str) -> List[Document]:
    raw_document = YourLoaderLibrary(api_key=self.api_key).load_file(file_path)
    splits = YourLoaderLibrary().split_document(raw_document)
    return [Document(page_content=split, metadata={"source": file_path, "split": i}) for i, split in enumerate(splits)]
```

---

## Considerations

- **Error Handling**: Ensure robust error handling.
- **Testing**: Write unit tests for your loader.
- **Performance**: Optimize for large documents.
- **Metadata**: Capture relevant document metadata.
- **Compatibility**: Return `langchain.schema.Document` objects for system compatibility.

## Example

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
