"""Document service."""

import logging
import os
import tempfile
import uuid
from typing import List, Optional

from langchain.schema import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter

from knowledge_table_api.core.config import Settings
from knowledge_table_api.services.loaders.factory import LoaderFactory
from knowledge_table_api.services.vector_db.base import VectorDBService

logger = logging.getLogger(__name__)


class DocumentService:
    """Document service."""

    def __init__(
        self,
        settings: Settings,
        vector_db_service: VectorDBService,
    ):
        """Document service."""
        self.settings = settings
        self.vector_db_service = vector_db_service
        self.loader_factory = LoaderFactory()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
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
                prepared_chunks = await self.vector_db_service.prepare_chunks(
                    document_id, chunks
                )
                await self.vector_db_service.upsert_vectors(prepared_chunks)
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
        loader = self.loader_factory.create_loader(self.settings)

        if loader is None:
            raise ValueError(
                f"No loader available for configured loader type: {self.settings.loader}"
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
