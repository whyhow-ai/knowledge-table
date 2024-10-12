import pytest
from pydantic import ValidationError

from app.models.llm import (
    ArrayResponseModel,
    BaseResponseModel,
    BoolResponseModel,
    IntArrayResponseModel,
    IntResponseModel,
    KeywordsResponseModel,
    SchemaRelationship,
    SchemaResponseModel,
    StrArrayResponseModel,
    StrResponseModel,
    SubQueriesResponseModel,
)


class TestBaseResponseModel:
    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            (None, None),
            ("none", None),
            ("NONE", None),
            ("value", "value"),
            (42, 42),
        ],
    )
    def test_validate_none(self, input_value, expected_output):
        # Given
        # input_value and expected_output from parametrize

        # When
        result = BaseResponseModel.validate_none(input_value)

        # Then
        assert result == expected_output


class TestBoolResponseModel:
    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            (True, True),
            (False, False),
            ("true", True),
            ("false", False),
            ("TRUE", True),
            ("FALSE", False),
            (None, None),
            ("none", None),
        ],
    )
    def test_valid_bool(self, input_value, expected_output):
        # Given
        # input_value and expected_output from parametrize

        # When
        model = BoolResponseModel(answer=input_value)

        # Then
        assert model.answer == expected_output

    @pytest.mark.parametrize("invalid_input", ["invalid", 42, 1.5])
    def test_invalid_bool(self, invalid_input):
        # Given
        # invalid_input from parametrize

        # When / Then
        with pytest.raises(ValidationError):
            BoolResponseModel(answer=invalid_input)


class TestIntResponseModel:
    @pytest.mark.parametrize(
        "input_value, expected_output",
        [
            (42, 42),
            ("42", 42),
            (None, None),
            ("none", None),
        ],
    )
    def test_valid_int(self, input_value, expected_output):
        # Given
        # input_value and expected_output from parametrize

        # When
        model = IntResponseModel(answer=input_value)

        # Then
        assert model.answer == expected_output

    @pytest.mark.parametrize("invalid_input", ["invalid", 1.5, "1.5"])
    def test_invalid_int(self, invalid_input):
        # Given
        # invalid_input from parametrize

        # When / Then
        with pytest.raises(ValidationError):
            IntResponseModel(answer=invalid_input)


class TestArrayResponseModel:
    def test_validate_array(self):
        # Given
        input_array = [1, 2, 3]
        max_length = 2

        # When
        result_none = ArrayResponseModel.validate_array(None)
        result_normal = ArrayResponseModel.validate_array(input_array)
        result_max_length = ArrayResponseModel.validate_array(
            input_array, max_length
        )

        # Then
        assert result_none is None
        assert result_normal == [1, 2, 3]
        assert result_max_length == [1, 2]

    def test_validate_array_invalid_input(self):
        # Given
        invalid_input = "not a list"

        # When / Then
        with pytest.raises(ValueError):
            ArrayResponseModel.validate_array(invalid_input)


class TestIntArrayResponseModel:
    def test_valid_int_array(self):
        # Given
        valid_input = [1, 2, 3]

        # When
        model = IntArrayResponseModel(answer=valid_input)

        # Then
        assert model.answer == [1, 2, 3]

    def test_invalid_int_array(self):
        # Given
        invalid_input = ["1", "2", "3a"]

        # When / Then
        with pytest.raises(ValueError):
            IntArrayResponseModel(answer=invalid_input)


class TestStrArrayResponseModel:
    def test_valid_str_array(self):
        # Given
        input_array = ["a", "b", "c"]

        # When
        model = StrArrayResponseModel(answer=input_array)

        # Then
        assert model.answer == ["a", "b", "c"]

    def test_str_array_with_rules(self):
        # Given
        # class DummyRule:
        #     type = "must_return"
        #     options = ["a", "b"]

        # input_array = ["a", "b", "c"]

        # # When
        # model = StrArrayResponseModel(answer=input_array, str_rule=DummyRule())

        # # Then
        # assert model.answer == ["a", "b"]

        # TODO: Implement this test when str_rule functionality is added
        pass


class TestStrResponseModel:
    def test_valid_str(self):
        # Given
        input_str = "test"

        # When
        model = StrResponseModel(answer=input_str)

        # Then
        assert model.answer == "test"

    def test_str_with_rules(self):
        # # Given
        # class DummyRule:
        #     type = "must_return"
        #     options = ["a", "b"]

        # # When
        # model_valid = StrResponseModel(answer="a", str_rule=DummyRule())
        # model_invalid = StrResponseModel(answer="c", str_rule=DummyRule())

        # # Then
        # assert model_valid.answer == "a"
        # assert model_invalid.answer is None

        # TODO: Implement this test when str_rule functionality is added
        pass


class TestKeywordsResponseModel:
    def test_valid_keywords(self):
        # Given
        keywords = ["key1", "key2"]

        # When
        model = KeywordsResponseModel(keywords=keywords)

        # Then
        assert model.keywords == ["key1", "key2"]


class TestSubQueriesResponseModel:
    def test_valid_sub_queries(self):
        # Given
        sub_queries = ["query1", "query2"]

        # When
        model = SubQueriesResponseModel(sub_queries=sub_queries)

        # Then
        assert model.sub_queries == ["query1", "query2"]


class TestSchemaRelationship:
    def test_valid_schema_relationship(self):
        # Given
        head = "Entity1"
        relation = "relates_to"
        tail = "Entity2"

        # When
        relationship = SchemaRelationship(
            head=head, relation=relation, tail=tail
        )

        # Then
        assert relationship.head == "Entity1"
        assert relationship.relation == "relates_to"
        assert relationship.tail == "Entity2"


class TestSchemaResponseModel:
    def test_valid_schema_response(self):
        # Given
        relationships = [
            SchemaRelationship(
                head="Entity1", relation="relates_to", tail="Entity2"
            ),
            SchemaRelationship(
                head="Entity2", relation="belongs_to", tail="Entity3"
            ),
        ]

        # When
        model = SchemaResponseModel(relationships=relationships)

        # Then
        assert len(model.relationships) == 2
        assert model.relationships[0].head == "Entity1"
        assert model.relationships[1].tail == "Entity3"


def test_logging(caplog):
    # Given
    input_array = [1, 2, 3, 4, 5]
    max_length = 3

    # When
    ArrayResponseModel.validate_array(input_array, max_length=max_length)

    # Then
    assert "Length of response is greater than 3" in caplog.text
