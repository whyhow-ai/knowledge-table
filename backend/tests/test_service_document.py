from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_upload_document(document_service, mocker):
    mocker.patch.object(
        document_service, "_generate_document_id", return_value="test_id"
    )
    mocker.patch.object(document_service, "_process_document", return_value=[])
    document_service.vector_db_service.prepare_chunks = AsyncMock(
        return_value=[]
    )
    document_service.vector_db_service.upsert_vectors = AsyncMock()

    result = await document_service.upload_document(
        "test.pdf", b"test content"
    )

    assert result == "test_id"
    document_service._process_document.assert_called_once()
    document_service.vector_db_service.prepare_chunks.assert_called_once()
    document_service.vector_db_service.upsert_vectors.assert_called_once()


@pytest.mark.asyncio
async def test_delete_document(document_service):
    document_service.vector_db_service.delete_document = AsyncMock(
        return_value=True
    )

    result = await document_service.delete_document("test_id")

    assert result is True
    document_service.vector_db_service.delete_document.assert_called_once_with(
        "test_id"
    )


@pytest.mark.asyncio
async def test_delete_document_failure(document_service):
    document_service.vector_db_service.delete_document = AsyncMock(
        return_value=False
    )

    result = await document_service.delete_document("test_id")

    assert result is False
    document_service.vector_db_service.delete_document.assert_called_once_with(
        "test_id"
    )


@pytest.mark.asyncio
async def test_upload_document_unstructured_not_available(
    document_service, mocker
):
    mocker.patch.object(
        document_service, "_generate_document_id", return_value="test_id"
    )
    mocker.patch.object(document_service, "_process_document", return_value=[])
    document_service.vector_db_service.prepare_chunks = AsyncMock(
        return_value=[]
    )
    document_service.vector_db_service.upsert_vectors = AsyncMock()

    with patch(
        "app.services.loaders.unstructured_service.UNSTRUCTURED_AVAILABLE",
        False,
    ):
        result = await document_service.upload_document(
            "test.pdf", b"test content"
        )

    assert result == "test_id"
    document_service._process_document.assert_called_once()
    document_service.vector_db_service.prepare_chunks.assert_called_once_with(
        "test_id", []
    )
    document_service.vector_db_service.upsert_vectors.assert_called_once_with(
        []
    )  # Remove 'test_id' from here


@pytest.mark.asyncio
async def test_process_document_unstructured_not_available(
    document_service, mocker
):
    mocker.patch.object(
        document_service.loader_factory, "create_loader", return_value=None
    )

    with pytest.raises(
        ValueError,
        match="No loader available for configured loader type: test_loader",
    ):
        await document_service._process_document("test_file_path")
