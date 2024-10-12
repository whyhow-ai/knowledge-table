from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def mock_llm_service():
    return Mock()


@pytest.fixture
def mock_vector_db_service():
    mock = AsyncMock()
    mock.delete_document.return_value = {
        "status": "success",
        "message": "Document deleted successfully",
    }
    return mock


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "document_id, expected_status, expected_response",
    [
        (
            "test_doc_id",
            201,
            {
                "id": "test_doc_id",
                "name": "test.txt",
                "author": "author_name",
                "tag": "document_tag",
                "page_count": 10,
            },
        ),
        (
            None,
            500,
            {"detail": "An error occurred while processing the document"},
        ),
    ],
)
@patch(
    "app.api.v1.endpoints.document.VectorDBFactory.create_vector_db_service"
)
@patch("app.api.v1.endpoints.document.DocumentService")
@patch("app.api.v1.endpoints.document.get_llm_service")
async def test_upload_document_endpoint(
    mock_get_llm_service,
    mock_doc_service,
    mock_vector_db_factory,
    document_id,
    expected_status,
    expected_response,
):
    # Given
    mock_llm_service_instance = Mock()
    # Mock any methods of the LLM service that are called during the test
    mock_llm_service_instance.some_method = AsyncMock(
        return_value="mocked_response"
    )
    mock_get_llm_service.return_value = mock_llm_service_instance

    mock_vector_db_factory.return_value = Mock()
    mock_doc_service.return_value.upload_document = AsyncMock(
        return_value=document_id
    )

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/document",
            files={"file": ("test.txt", b"test content", "text/plain")},
        )

    # Then
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status",
    [
        (ValueError("Test error"), 400),
        (Exception("Unexpected error"), 500),
    ],
)
@patch(
    "app.api.v1.endpoints.document.VectorDBFactory.create_vector_db_service"
)
@patch("app.api.v1.endpoints.document.DocumentService")
@patch("app.api.v1.endpoints.document.get_llm_service")
async def test_upload_document_endpoint_errors(
    mock_get_llm_service,
    mock_doc_service,
    mock_vector_db_factory,
    exception,
    expected_status,
):
    # Given
    mock_llm_service_instance = Mock()
    mock_llm_service_instance.some_method = AsyncMock(side_effect=exception)
    mock_get_llm_service.return_value = mock_llm_service_instance

    mock_vector_db_factory.return_value = Mock()
    mock_doc_service.return_value.upload_document = AsyncMock(
        side_effect=exception
    )

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/document",
            files={"file": ("test.txt", b"test content", "text/plain")},
        )

    # Then
    assert response.status_code == expected_status
    assert str(exception) in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_document_endpoint_missing_filename():
    # Given
    # No specific setup required

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/document",
            files={"file": ("", b"test content", "text/plain")},
        )

    # Then
    assert response.status_code == 422
    assert "detail" in response.json()
    assert any("file" in error["loc"] for error in response.json()["detail"])


@pytest.mark.asyncio
@patch(
    "app.api.v1.endpoints.document.VectorDBFactory.create_vector_db_service"
)
@patch("app.api.v1.endpoints.document.DocumentService")
@patch("app.api.v1.endpoints.document.get_llm_service")
async def test_upload_document_endpoint_none_document_id(
    mock_get_llm_service, mock_doc_service, mock_vector_db_factory
):
    # Given
    mock_llm_service_instance = Mock()
    mock_llm_service_instance.some_method = AsyncMock(
        return_value="mocked_response"
    )
    mock_get_llm_service.return_value = mock_llm_service_instance

    mock_vector_db_factory.return_value = AsyncMock()
    mock_doc_service.return_value.upload_document = AsyncMock(
        return_value=None
    )

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/document",
            files={"file": ("test.txt", b"test content", "text/plain")},
        )

    # Then
    assert response.status_code == 500
    assert response.json() == {
        "detail": "An error occurred while processing the document"
    }


@pytest.mark.asyncio
@patch(
    "app.api.v1.endpoints.document.VectorDBFactory.create_vector_db_service"
)
@patch("app.api.v1.endpoints.document.get_llm_service")
async def test_delete_document_endpoint_none_vector_db_service(
    mock_get_llm_service, mock_vector_db_factory
):
    # Given
    mock_llm_service_instance = Mock()
    mock_llm_service_instance.some_method = AsyncMock(
        return_value="mocked_response"
    )
    mock_get_llm_service.return_value = mock_llm_service_instance

    mock_vector_db_factory.return_value = None

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/v1/document/test_doc_id")

    # Then
    assert response.status_code == 500
    assert response.json() == {
        "detail": "500: Failed to create vector database service"
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_return, expected_status, expected_response",
    [
        (
            {"status": "success", "message": "Document deleted successfully"},
            200,
            {
                "id": "test_doc_id",
                "status": "success",
                "message": "Document deleted successfully",
            },
        ),
        (
            None,
            500,
            {"detail": "500: Failed to create vector database service"},
        ),
    ],
)
@patch(
    "app.api.v1.endpoints.document.VectorDBFactory.create_vector_db_service"
)
@patch("app.api.v1.endpoints.document.get_llm_service")
async def test_delete_document_endpoint(
    mock_get_llm_service,
    mock_vector_db_factory,
    mock_return,
    expected_status,
    expected_response,
):
    # Given
    mock_llm_service_instance = Mock()
    mock_llm_service_instance.some_method = AsyncMock(
        return_value="mocked_response"
    )
    mock_get_llm_service.return_value = mock_llm_service_instance

    mock_vector_db_service = AsyncMock()
    mock_vector_db_service.delete_document.return_value = mock_return
    mock_vector_db_factory.return_value = (
        mock_vector_db_service if mock_return else None
    )

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/v1/document/test_doc_id")

    # Then
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_status",
    [
        (ValueError("Test ValueError"), 400),
        (Exception("Unexpected error"), 500),
    ],
)
@patch(
    "app.api.v1.endpoints.document.VectorDBFactory.create_vector_db_service"
)
@patch("app.api.v1.endpoints.document.get_llm_service")
async def test_delete_document_endpoint_errors(
    mock_get_llm_service, mock_vector_db_factory, exception, expected_status
):
    # Given
    mock_llm_service_instance = Mock()
    mock_llm_service_instance.some_method = AsyncMock(side_effect=exception)
    mock_get_llm_service.return_value = mock_llm_service_instance

    mock_vector_db_service = AsyncMock()
    mock_vector_db_service.delete_document.side_effect = exception
    mock_vector_db_factory.return_value = mock_vector_db_service

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/api/v1/document/test_doc_id")

    # Then
    assert response.status_code == expected_status
    assert str(exception) in response.json()["detail"]


@pytest.mark.asyncio
@patch(
    "app.api.v1.endpoints.document.VectorDBFactory.create_vector_db_service"
)
@patch("app.api.v1.endpoints.document.DocumentService")
@patch("app.api.v1.endpoints.document.logger")
@patch("app.api.v1.endpoints.document.get_llm_service")
async def test_upload_document_endpoint_logging(
    mock_get_llm_service, mock_logger, mock_doc_service, mock_vector_db_factory
):
    # Given
    mock_llm_service_instance = Mock()
    mock_llm_service_instance.some_method = AsyncMock(
        return_value="mocked_response"
    )
    mock_get_llm_service.return_value = mock_llm_service_instance

    mock_vector_db_factory.return_value = Mock()
    mock_doc_service.return_value.upload_document = AsyncMock(
        return_value="test_doc_id"
    )

    # When
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post(
            "/api/v1/document",
            files={"file": ("test.txt", b"test content", "text/plain")},
        )

    # Then
    mock_logger.info.assert_called_once_with(
        "Endpoint received file: test.txt, content type: text/plain"
    )
