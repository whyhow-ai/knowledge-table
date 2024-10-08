"""Document service."""

import contextlib
import logging
import os
import tempfile
import uuid
from typing import Generator, List, Optional

from langchain.schema import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)

from knowledge_table_api.services.vector import prepare_chunks, upsert_vectors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UNSTRUCTURED_API_KEY = os.getenv("UNSTRUCTURED_API_KEY")

if UNSTRUCTURED_API_KEY:
    try:
        from unstructured.documents.elements import NarrativeText, Text, Title
        from unstructured.partition.auto import partition
    except ImportError:
        logger.warning(
            "Unstructured is not installed. Install with `pip install .[unstructured]`"
        )
        partition = None
        Text = Title = NarrativeText = None
else:
    partition = None
    Text = Title = NarrativeText = None

# Constants
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

loader_types = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": Docx2txtLoader,
    "application/msword": Docx2txtLoader,
    "application/pdf": PyPDFLoader,
    "text/plain": TextLoader,
}


@contextlib.contextmanager
def temp_file(content: bytes, suffix: str) -> Generator[str, None, None]:
    """Context manager for creating and cleaning up temporary files."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name
    try:
        yield temp_file_path
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Temporary file {temp_file_path} has been deleted.")


def unstructured_loader(file_path: str) -> List[LangchainDocument]:
    """
    Unstructured loader for processing documents.

    Parameters
    ----------
    file_path : str
        Path to the file to be processed.

    Returns
    -------
    List[LangchainDocument]
        List of processed document chunks.
    """
    elements = partition(filename=file_path)
    docs = []
    current_page = 1
    current_text = ""

    for element in elements:
        if isinstance(element, (Text, Title, NarrativeText)):
            current_text += element.text + "\n"

        if isinstance(element, Title) and current_text:
            docs.append(
                LangchainDocument(
                    page_content=current_text, metadata={"page": current_page}
                )
            )
            current_page += 1
            current_text = element.text + "\n"

    if current_text:
        docs.append(
            LangchainDocument(
                page_content=current_text, metadata={"page": current_page}
            )
        )

    return docs


async def upload_document(
    content_type: Optional[str], filename: str, file_content: bytes
) -> Optional[str]:
    """
    Upload and process a document.

    Parameters
    ----------
    content_type : Optional[str]
        MIME type of the uploaded file.
    filename : str
        Name of the uploaded file.
    file_content : bytes
        Content of the uploaded file.

    Returns
    -------
    Optional[str]
        Document ID if successful, None if an error occurred.

    Raises
    ------
    ValueError
        If content type is missing or unsupported.
    """
    document_id = uuid.uuid4().hex
    logger.info(f"Created document_id: {document_id}")

    if content_type is None:
        raise ValueError("Content type is missing")

    loader = loader_types.get(content_type)
    if loader is None:
        raise ValueError(f"Unsupported file type: {content_type}")

    logger.info(f"{content_type} detected, using loader: {loader}")

    try:
        with temp_file(
            file_content, os.path.splitext(str(filename))[1]
        ) as temp_file_path:
            logger.info(f"Temp file stored at: {temp_file_path}")
            logger.info("Processing document.")

            if UNSTRUCTURED_API_KEY:
                logger.info("Using UnstructuredLoader")
                try:
                    docs = unstructured_loader(temp_file_path)
                except Exception as e:
                    logger.error(
                        f"Unstructured loader failed: {e}. Falling back to default loader."
                    )
                    document_loader = loader(temp_file_path)
                    docs = document_loader.load()
            else:
                logger.info(f"Using {loader.__name__}")
                document_loader = loader(temp_file_path)
                docs = document_loader.load()

            logger.info("Splitting document.")
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
            )
            chunks = splitter.split_documents(docs)

            prepared_chunks = await prepare_chunks(document_id, chunks)

            logger.info(f"Created {len(prepared_chunks)} vectors.")

            upserted_response = await upsert_vectors(prepared_chunks)

            logger.info(upserted_response["message"])

            return document_id

    except ValueError as ve:
        logger.error(f"Value error: {ve}")
    except IOError as ioe:
        logger.error(f"IO error: {ioe}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)

    return None
