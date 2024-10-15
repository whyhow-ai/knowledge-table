"""Tests for the query model"""

import pytest
from pydantic import ValidationError

from app.models.query import Answer, Chunk, Rule


class TestRuleModel:
    def test_valid_rule_must_return(self):
        # Given
        rule_data = {"type": "must_return", "options": ["option1", "option2"]}

        # When
        rule = Rule(**rule_data)

        # Then
        assert rule.type == "must_return"
        assert rule.options == ["option1", "option2"]
        assert rule.length is None

    def test_valid_rule_max_length(self):
        # Given
        rule_data = {"type": "max_length", "length": 100}

        # When
        rule = Rule(**rule_data)

        # Then
        assert rule.type == "max_length"
        assert rule.options is None
        assert rule.length == 100

    def test_invalid_rule_type(self):
        # Given
        invalid_rule_data = {"type": "invalid_type", "options": ["option1"]}

        # When / Then
        with pytest.raises(ValidationError):
            Rule(**invalid_rule_data)


class TestChunkModel:
    def test_valid_chunk(self):
        # Given
        chunk_data = {"content": "This is a chunk of text.", "page": 1}

        # When
        chunk = Chunk(**chunk_data)

        # Then
        assert chunk.content == "This is a chunk of text."
        assert chunk.page == 1

    def test_invalid_chunk_missing_field(self):
        # Given
        invalid_chunk_data = {"content": "This is a chunk of text."}

        # When / Then
        with pytest.raises(ValidationError):
            Chunk(**invalid_chunk_data)


class TestAnswerModel:
    @pytest.mark.parametrize(
        "answer_value",
        [42, "text answer", True, [1, 2, 3], ["a", "b", "c"], None],
    )
    def test_valid_answer(self, answer_value):
        # Given
        answer_data = {
            "id": "answer_id",
            "document_id": "doc_id",
            "prompt_id": "prompt_id",
            "answer": answer_value,
            "chunks": [{"content": "chunk content", "page": 1}],
            "type": "answer_type",
        }

        # When
        answer = Answer(**answer_data)

        # Then
        assert answer.id == "answer_id"
        assert answer.document_id == "doc_id"
        assert answer.prompt_id == "prompt_id"
        assert answer.answer == answer_value
        assert len(answer.chunks) == 1
        assert answer.chunks[0].content == "chunk content"
        assert answer.chunks[0].page == 1
        assert answer.type == "answer_type"

    def test_invalid_answer_missing_field(self):
        # Given
        invalid_answer_data = {
            "id": "answer_id",
            "document_id": "doc_id",
            "prompt_id": "prompt_id",
            "answer": "text answer",
            "chunks": [{"content": "chunk content", "page": 1}],
            # Missing 'type' field
        }

        # When / Then
        with pytest.raises(ValidationError):
            Answer(**invalid_answer_data)

    def test_invalid_answer_wrong_type(self):
        # Given
        invalid_answer_data = {
            "id": "answer_id",
            "document_id": "doc_id",
            "prompt_id": "prompt_id",
            "answer": {
                "invalid": "type"
            },  # Dictionary is not a valid answer type
            "chunks": [{"content": "chunk content", "page": 1}],
            "type": "answer_type",
        }

        # When / Then
        with pytest.raises(ValidationError):
            Answer(**invalid_answer_data)
