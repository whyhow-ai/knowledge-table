"""Tests for the query routing schema"""

"""Tests for the query API routing schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.query import QueryPrompt, QueryRequest, VectorResponse, QueryResponse
from app.models.query import Chunk, Rule


class TestQueryPrompt:
    def test_valid_query_prompt(self):
        prompt_data = {
            "id": "1",
            "query": "What is the patient's age?",
            "type": "int",
            "entity_type": "patient",
            "rules": [Rule(type="max_length", length=120)]
        }
        prompt = QueryPrompt(**prompt_data)
        assert prompt.id == "1"
        assert prompt.query == "What is the patient's age?"
        assert prompt.type == "int"
        assert prompt.entity_type == "patient"
        assert len(prompt.rules) == 1
        assert prompt.rules[0].type == "max_length"
        assert prompt.rules[0].length == 120

    def test_invalid_query_prompt_type(self):
        invalid_data = {
            "id": "1",
            "query": "What is the patient's age?",
            "type": "float",  # Invalid type
            "entity_type": "patient"
        }
        with pytest.raises(ValidationError):
            QueryPrompt(**invalid_data)

    def test_query_prompt_without_rules(self):
        prompt_data = {
            "id": "1",
            "query": "What is the patient's name?",
            "type": "str",
            "entity_type": "patient"
        }
        prompt = QueryPrompt(**prompt_data)
        assert prompt.rules is None


class TestQueryRequest:
    def test_valid_query_request(self):
        request_data = {
            "document_id": "doc123",
            "previous_answer": 25,
            "prompt": {
                "id": "1",
                "query": "What is the patient's age?",
                "type": "int",
                "entity_type": "patient"
            },
            "rag_type": "hybrid"
        }
        request = QueryRequest(**request_data)
        assert request.document_id == "doc123"
        assert request.previous_answer == 25
        assert isinstance(request.prompt, QueryPrompt)
        assert request.rag_type == "hybrid"

    def test_query_request_default_rag_type(self):
        request_data = {
            "document_id": "doc123",
            "prompt": {
                "id": "1",
                "query": "What is the patient's name?",
                "type": "str",
                "entity_type": "patient"
            }
        }
        request = QueryRequest(**request_data)
        assert request.rag_type == "hybrid"

    def test_invalid_query_request_rag_type(self):
        invalid_data = {
            "document_id": "doc123",
            "prompt": {
                "id": "1",
                "query": "What is the patient's name?",
                "type": "str",
                "entity_type": "patient"
            },
            "rag_type": "invalid_type"
        }
        with pytest.raises(ValidationError):
            QueryRequest(**invalid_data)


class TestVectorResponse:
    def test_valid_vector_response(self):
        response_data = {
            "message": "Success",
            "chunks": [
                Chunk(content="Sample content", page=1),
                Chunk(content="More content", page=2)
            ]
        }
        response = VectorResponse(**response_data)
        assert response.message == "Success"
        assert len(response.chunks) == 2
        assert response.chunks[0].content == "Sample content"
        assert response.chunks[0].page == 1


class TestQueryResponse:
    def test_valid_query_response(self):
        response_data = {
            "id": "resp1",
            "document_id": "doc123",
            "prompt_id": "1",
            "answer": 25,
            "chunks": [
                Chunk(content="Sample content", page=1),
                Chunk(content="More content", page=2)
            ],
            "type": "int"
        }
        response = QueryResponse(**response_data)
        assert response.id == "resp1"
        assert response.document_id == "doc123"
        assert response.prompt_id == "1"
        assert response.answer == 25
        assert len(response.chunks) == 2
        assert response.type == "int"

    def test_query_response_with_different_answer_types(self):
        test_cases = [
            ("int", 42),
            ("str", "John Doe"),
            ("bool", True),
            ("int_array", [1, 2, 3]),
            ("str_array", ["apple", "banana", "cherry"])
        ]
        for type_, answer in test_cases:
            response_data = {
                "id": "resp1",
                "document_id": "doc123",
                "prompt_id": "1",
                "answer": answer,
                "chunks": [],
                "type": type_
            }
            response = QueryResponse(**response_data)
            assert response.answer == answer
            assert response.type == type_

    def test_query_response_with_no_answer(self):
        response_data = {
            "id": "resp1",
            "document_id": "doc123",
            "prompt_id": "1",
            "answer": None,
            "chunks": [],
            "type": "str"
        }
        response = QueryResponse(**response_data)
        assert response.answer is None