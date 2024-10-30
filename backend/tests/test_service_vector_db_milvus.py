from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain.schema import Document

from app.core.config import Settings
from app.schemas.query_api import Chunk, VectorResponseSchema
from app.services.vector_db.milvus_service import MilvusService


@pytest.fixture
def mock_llm_service():
    return AsyncMock()


@pytest.fixture
def mock_milvus_client():
    return MagicMock()


@pytest.fixture
def milvus_service(mock_llm_service, mock_embeddings_servce, mock_milvus_client):
    settings = Settings(
        milvus_db_uri="test_uri",
        milvus_db_token="test_token",
        index_name="test_index",
        dimensions=1536,
    )
    with patch(
        "app.services.vector_db.milvus_service.MilvusClient",
        return_value=mock_milvus_client,
    ):
        service = MilvusService(mock_llm_service, mock_embeddings_servce, settings)
        yield service


@pytest.mark.asyncio
async def test_get_embeddings_single(milvus_service, mock_llm_service):
    mock_llm_service.get_embeddings.return_value = [[0.1, 0.2, 0.3]]
    result = await milvus_service.get_embeddings("test text")
    assert result == [[0.1, 0.2, 0.3]]
    mock_llm_service.get_embeddings.assert_called_once_with(["test text"])


@pytest.mark.asyncio
async def test_get_embeddings_multiple(milvus_service, mock_llm_service):
    mock_llm_service.get_embeddings.return_value = [[0.1, 0.2], [0.3, 0.4]]
    result = await milvus_service.get_embeddings(["text1", "text2"])
    assert result == [[0.1, 0.2], [0.3, 0.4]]
    mock_llm_service.get_embeddings.assert_called_once_with(["text1", "text2"])


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_ensure_collection_exists(milvus_service, mock_milvus_client):
    mock_milvus_client.has_collection.return_value = False
    mock_schema = MagicMock()
    mock_milvus_client.create_schema.return_value = mock_schema

    await milvus_service.ensure_collection_exists()

    mock_milvus_client.has_collection.assert_called_once_with(
        collection_name=milvus_service.settings.index_name
    )
    mock_milvus_client.create_schema.assert_called_once_with(
        auto_id=False,
        enable_dynamic_field=True,
    )
    mock_schema.add_field.assert_called()
    mock_milvus_client.prepare_index_params.assert_called_once()
    mock_milvus_client.create_collection.assert_called_once()


@pytest.mark.asyncio
async def test_upsert_vectors(milvus_service, mock_milvus_client):
    vectors = [
        {"id": "1", "vector": [0.1, 0.2]},
        {"id": "2", "vector": [0.3, 0.4]},
    ]
    mock_milvus_client.insert.return_value = {"insert_count": 2}

    result = await milvus_service.upsert_vectors(vectors)

    assert result == {"message": "Successfully upserted 2 chunks."}
    mock_milvus_client.insert.assert_called_once()


@pytest.mark.asyncio
async def test_prepare_chunks(milvus_service):
    document_id = "test_doc"
    chunks = [
        Document(page_content="chunk1", metadata={"page": 1}),
        Document(page_content="chunk2", metadata={"page": 2}),
    ]
    milvus_service.get_embeddings = AsyncMock(
        return_value=[[0.1, 0.2], [0.3, 0.4]]
    )

    result = await milvus_service.prepare_chunks(document_id, chunks)

    assert len(result) == 2
    assert all(
        key in result[0]
        for key in [
            "id",
            "vector",
            "text",
            "page_number",
            "chunk_number",
            "document_id",
        ]
    )
    assert result[0]["text"] == "chunk1"
    assert result[1]["text"] == "chunk2"


@pytest.mark.asyncio
async def test_hybrid_search(milvus_service, mock_milvus_client):
    query = "test query"
    document_id = "test_doc"
    rules = []

    milvus_service.get_embeddings = AsyncMock(return_value=[[0.1, 0.2]])
    mock_milvus_client.query.side_effect = [
        [{"count(*)": 10}],
        [
            {"text": "result1", "page_number": 1},
            {"text": "result2", "page_number": 2},
        ],
    ]
    mock_milvus_client.search.return_value = [
        [{"entity": {"text": "semantic1", "page_number": 3}}]
    ]

    result = await milvus_service.hybrid_search(query, document_id, rules)

    assert isinstance(result, VectorResponseSchema)
    assert len(result.chunks) > 0
    assert all(isinstance(chunk, Chunk) for chunk in result.chunks)


@pytest.mark.asyncio
async def test_decomposed_search(milvus_service, mock_llm_service):
    query = "complex query"
    document_id = "test_doc"
    rules = []

    mock_llm_service.decompose_query.return_value = {
        "sub-queries": ["sub1", "sub2"]
    }
    milvus_service.hybrid_search = AsyncMock(
        return_value=VectorResponseSchema(
            message="", chunks=[Chunk(content="result", page=1)]
        )
    )

    result = await milvus_service.decomposed_search(query, document_id, rules)

    assert "sub_queries" in result
    assert len(result["sub_queries"]) == 2
    assert all(
        "query" in sub_query and "chunks" in sub_query
        for sub_query in result["sub_queries"]
    )
    assert all(
        len(sub_query["chunks"]) == 1 for sub_query in result["sub_queries"]
    )
    assert all(
        sub_query["chunks"][0]["content"] == "result"
        for sub_query in result["sub_queries"]
    )


@pytest.mark.asyncio
async def test_delete_document(milvus_service, mock_milvus_client):
    document_id = "test_doc"
    mock_milvus_client.query.return_value = []

    result = await milvus_service.delete_document(document_id)

    assert result["status"] == "success"
    mock_milvus_client.delete.assert_called_once()
    mock_milvus_client.query.assert_called_once()
