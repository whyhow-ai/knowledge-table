"""Document service."""

import logging
import os
import tempfile
import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)

from knowledge_table_api.services.vector import prepare_chunks, upsert_vectors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

loader_types = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": Docx2txtLoader,
    "application/msword": Docx2txtLoader,
    "application/pdf": PyPDFLoader,
    "text/plain": TextLoader,
}


async def upload_document(
    content_type: str | None, filename: str, file_content: bytes
) -> str | None:
    """Upload a document and process it."""
    document_id = uuid.uuid4().hex
    logger.info(f"Created document_id: {document_id}")
    if content_type is None:
        raise ValueError("Content type is missing")
    loader = loader_types.get(content_type)
    if loader is None:
        raise ValueError(f"Unsupported file type: {content_type}")

    logger.info(f"{content_type} detected, using loader: {loader}")

    try:

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(str(filename))[1]
        ) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

            logger.info(f"Temp file stored at: {temp_file_path}")

        logger.info("Processing document.")

        document_loader = loader(temp_file_path)
        docs = document_loader.load()

        logger.info("Splitting document.")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=512, chunk_overlap=64
        )
        chunks = splitter.split_documents(docs)

        prepared_chunks = await prepare_chunks(document_id, chunks)

        logger.info(f"Created {len(prepared_chunks)} vectors.")

        upserted_response = await upsert_vectors(prepared_chunks)

        logger.info(upserted_response["message"])

        return document_id

    except Exception as e:
        logger.info(f"An error occurred: {e}")
        return None

    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            if not os.path.exists(temp_file_path):
                logger.info(
                    f"Temporary file {temp_file_path} has been successfully deleted."
                )
            else:
                logger.error(
                    f"Failed to delete temporary file {temp_file_path}."
                )
