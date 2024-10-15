"""Document service."""

import logging
import os
import tempfile
import uuid
from typing import List, Optional

from langchain.schema import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import get_settings, Settings
from app.services.llm.base import LLMService
from app.services.loaders.factory import LoaderFactory
from app.services.vector_db.base import VectorDBService

logger = logging.getLogger(__name__)


class DocumentService:
    """Document service."""

    def __init__(
        self,
        vector_db_service: VectorDBService,
        llm_service: LLMService,
    ):
        """Document service."""
        self.vector_db_service = vector_db_service
        self.llm_service = llm_service
        self.loader_factory = LoaderFactory()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

    async def upload_document(
        self,
        filename: str,
        file_content: bytes,
    ) -> Optional[str]:
        """Upload a document."""
        try:

            # Generate a document ID
            document_id = self._generate_document_id()
            logger.info(f"Created document_id: {document_id}")

            # Save the file to a temporary location
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=os.path.splitext(filename)[1]
            ) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            # Process the document
            try:

                chunks = await self._process_document(temp_file_path)

                if self.llm_service.is_available():
                    prepared_chunks = (
                        await self.vector_db_service.prepare_chunks(
                            document_id, chunks
                        )
                    )
                    await self.vector_db_service.upsert_vectors(
                        prepared_chunks
                    )
                else:
                    logger.warning(
                        "LLM service is not available. Skipping vector embedding."
                    )
                    # Implement fallback behavior here
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

            return document_id

        except Exception as e:
            logger.error(f"Error uploading document: {e}", exc_info=True)
            return None

    async def _process_document(
        self, file_path: str
    ) -> List[LangchainDocument]:
        """Process a document."""
        # Load the document
        docs = await self._load_document(file_path)

        # Split the document into chunks
        chunks = self.splitter.split_documents(docs)
        logger.info(f"Document split into {len(chunks)} chunks")
        return chunks

    async def _load_document(self, file_path: str) -> List[LangchainDocument]:

        # Create a loader
        loader = self.loader_factory.create_loader()

        if loader is None:
            raise ValueError(
                f"No loader available for configured loader type: {settings.loader}"
            )

        # Load the document
        try:
            return await loader.load(file_path)
        except Exception as e:
            logger.error(f"Loader failed: {e}. Unable to load document.")
            raise

    @staticmethod
    def _generate_document_id() -> str:
        return uuid.uuid4().hex
