"""Base loader service."""

from abc import ABC, abstractmethod
from typing import List

from langchain.schema import Document as LangchainDocument


class LoaderService(ABC):
    """Base loader service."""

    @abstractmethod
    async def load(self, file_path: str) -> List[LangchainDocument]:
        """Load document from file path."""
        pass
