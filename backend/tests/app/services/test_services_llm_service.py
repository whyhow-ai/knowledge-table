"""Tests for the LLM service"""

from unittest.mock import AsyncMock

import pytest

from app.models.llm import (
    KeywordsResponseModel,
    SchemaResponseModel,
    StrResponseModel,
    SubQueriesResponseModel,
)
from app.models.query import Rule
from app.schemas.graph import Cell, Column, Document, Prompt, Row, Table
from app.services.llm.base import LLMService
from app.services.llm_service import (
    _get_int_rule_line,
    _get_str_rule_line,
    decompose_query,
    generate_response,
    generate_schema,
    get_keywords,
    get_similar_keywords,
)


@pytest.fixture
def mock_llm_service():
    return AsyncMock(spec=LLMService)


@pytest.mark.asyncio
async def test_generate_response(mock_llm_service):
    # Given
    query = "Test query"
    chunks = "Test chunks"
    rules = [Rule(type="must_return", options=["option1", "option2"])]
    format = "str"
    mock_llm_service.generate_completion.return_value = StrResponseModel(
        answer="Test answer"
    )

    # When
    result = await generate_response(
        mock_llm_service, query, chunks, rules, format
    )

    # Then
    assert result == {"answer": "Test answer"}
    mock_llm_service.generate_completion.assert_called_once()


@pytest.mark.asyncio
async def test_get_keywords(mock_llm_service):
    # Given
    query = "Test query"
    mock_llm_service.generate_completion.return_value = KeywordsResponseModel(
        keywords=["keyword1", "keyword2"]
    )

    # When
    result = await get_keywords(mock_llm_service, query)

    # Then
    assert result == {"keywords": ["keyword1", "keyword2"]}
    mock_llm_service.generate_completion.assert_called_once()


@pytest.mark.asyncio
async def test_get_similar_keywords(mock_llm_service):
    # Given
    chunks = "Test chunks"
    rule = ["keyword1", "keyword2"]
    mock_llm_service.generate_completion.return_value = KeywordsResponseModel(
        keywords=["similar1", "similar2"]
    )

    # When
    result = await get_similar_keywords(mock_llm_service, chunks, rule)

    # Then
    assert result == {"keywords": ["similar1", "similar2"]}
    mock_llm_service.generate_completion.assert_called_once()


@pytest.mark.asyncio
async def test_decompose_query(mock_llm_service):
    # Given
    query = "Complex test query"
    mock_llm_service.generate_completion.return_value = (
        SubQueriesResponseModel(sub_queries=["sub1", "sub2"])
    )

    # When
    result = await decompose_query(mock_llm_service, query)

    # Then
    assert result == {"sub-queries": ["sub1", "sub2"]}
    mock_llm_service.generate_completion.assert_called_once()


@pytest.mark.asyncio
async def test_generate_schema(mock_llm_service):
    # Given
    data = Table(
        rows=[
            Row(
                id="1",
                document=Document(
                    id="doc1",
                    name="Document 1",
                    author="Author",
                    tag="Tag",
                    page_count=10,
                ),
                hidden=False,
            )
        ],
        columns=[
            Column(
                id="col1",
                prompt=Prompt(
                    entityType="Entity1",
                    id="prompt1",
                    query="Query1",
                    rules=[],
                    type="Type1",
                ),
                width=100,
                hidden=False,
            )
        ],
        cells=[
            Cell(
                rowId="1",
                columnId="col1",
                answer={
                    "answer": "Answer1",
                    "chunks": [{"content": "Chunk1", "page": 1}],
                },
                dirty=False,
            )
        ],
    )
    mock_llm_service.generate_completion.return_value = SchemaResponseModel(
        relationships=[
            {"head": "Entity1", "relation": "relates_to", "tail": "Entity2"}
        ]
    )

    # When
    result = await generate_schema(mock_llm_service, data)

    # Then
    assert result == {
        "schema": {
            "relationships": [
                {
                    "head": "Entity1",
                    "relation": "relates_to",
                    "tail": "Entity2",
                }
            ]
        }
    }
    mock_llm_service.generate_completion.assert_called_once()


def test_get_str_rule_line():
    # Given
    str_rule_must_return = Rule(
        type="must_return", options=["option1", "option2"]
    )
    str_rule_may_return = Rule(
        type="may_return", options=["option1", "option2"]
    )
    query = "Test query"

    # When
    result_must_return = _get_str_rule_line(str_rule_must_return, query)
    result_may_return = _get_str_rule_line(str_rule_may_return, query)
    result_none = _get_str_rule_line(None, query)

    # Then
    assert (
        "You should only consider these possible values" in result_must_return
    )
    assert "For example: Query: Test query Response:" in result_may_return
    assert result_none == ""


def test_get_int_rule_line():
    # Given
    int_rule = Rule(type="max_length", length=5)

    # When
    result = _get_int_rule_line(int_rule)
    result_none = _get_int_rule_line(None)

    # Then
    assert "Your answer should only return up to 5 items" in result
    assert result_none == ""
