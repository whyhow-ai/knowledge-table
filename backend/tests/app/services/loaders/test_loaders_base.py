"""Tests for the base loader"""

"""Tests for the base loader service."""

from typing import List

import pytest
from langchain.schema import Document as LangchainDocument

from app.services.loaders.base import LoaderService


class ConcreteLoaderService(LoaderService):
    """Concrete implementation of LoaderService for testing purposes."""

    async def load(self, file_path: str) -> List[LangchainDocument]:
        """Mock implementation of load method."""
        return [
            LangchainDocument(
                page_content="Test content", metadata={"source": file_path}
            )
        ]


@pytest.mark.asyncio
async def test_cannot_instantiate_abstract_loader_service():
    """
    Given: The abstract LoaderService class
    When: An attempt is made to instantiate it directly
    Then: A TypeError should be raised
    """
    with pytest.raises(TypeError) as exc_info:
        LoaderService()

    assert (
        "Can't instantiate abstract class LoaderService with abstract method load"
        in str(exc_info.value)
    )


@pytest.mark.asyncio
async def test_concrete_loader_service_instantiation():
    """
    Given: A concrete implementation of LoaderService
    When: The class is instantiated
    Then: It should not raise any errors
    """
    try:
        ConcreteLoaderService()
    except Exception as e:
        pytest.fail(
            f"ConcreteLoaderService instantiation raised an unexpected exception: {e}"
        )


@pytest.mark.asyncio
async def test_concrete_loader_service_load_method():
    """
    Given: An instance of ConcreteLoaderService
    When: The load method is called with a file path
    Then: It should return a list of LangchainDocument objects
    """
    # Given
    loader_service = ConcreteLoaderService()
    file_path = "test_file.txt"

    # When
    result = await loader_service.load(file_path)

    # Then
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], LangchainDocument)
    assert result[0].page_content == "Test content"
    assert result[0].metadata == {"source": file_path}


@pytest.mark.asyncio
async def test_loader_service_abstract_method():
    """
    Given: The abstract LoaderService class
    When: We check its load method
    Then: It should be an abstract method
    """
    # Given/When
    load_method = LoaderService.load

    # Then
    assert getattr(load_method, "__isabstractmethod__", False)
