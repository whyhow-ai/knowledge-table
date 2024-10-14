"""Tests for the LLM prompts"""

from app.services.llm.prompts import (
    BASE_PROMPT,
    BOOL_INSTRUCTIONS,
    DECOMPOSE_QUERY_PROMPT,
    INT_ARRAY_INSTRUCTIONS,
    KEYWORD_PROMPT,
    SCHEMA_PROMPT,
    SIMILAR_KEYWORDS_PROMPT,
    STR_ARRAY_INSTRUCTIONS,
)


def test_base_prompt_format():
    """Test that BASE_PROMPT is correctly formatted."""
    # Given
    query = "Test query"
    chunks = "Test chunks"
    format_specific_instructions = "Test instructions"

    # When
    result = BASE_PROMPT.safe_substitute(
        query=query,
        chunks=chunks,
        format_specific_instructions=format_specific_instructions,
    )

    # Then
    assert query in result
    assert chunks in result
    assert format_specific_instructions in result
    assert "**Question**" in result
    assert "**Context**" in result
    assert "**Instructions**" in result


def test_bool_instructions_content():
    """Test that BOOL_INSTRUCTIONS contains expected content."""
    assert "True" in BOOL_INSTRUCTIONS
    assert "False" in BOOL_INSTRUCTIONS
    assert "None" in BOOL_INSTRUCTIONS


def test_str_array_instructions_format():
    """Test that STR_ARRAY_INSTRUCTIONS is correctly formatted."""
    # Given
    str_rule_line = "Test str rule"
    int_rule_line = "Test int rule"

    # When
    result = STR_ARRAY_INSTRUCTIONS.safe_substitute(
        str_rule_line=str_rule_line, int_rule_line=int_rule_line
    )

    # Then
    assert str_rule_line in result
    assert int_rule_line in result
    assert "JSON array of strings" in result


def test_int_array_instructions_format():
    """Test that INT_ARRAY_INSTRUCTIONS is correctly formatted."""
    # Given
    int_rule_line = "Test int rule"

    # When
    result = INT_ARRAY_INSTRUCTIONS.safe_substitute(
        int_rule_line=int_rule_line
    )

    # Then
    assert int_rule_line in result
    assert "JSON array of integers" in result


def test_keyword_prompt_format():
    """Test that KEYWORD_PROMPT is correctly formatted."""
    # Given
    query = "Test query"

    # When
    result = KEYWORD_PROMPT.safe_substitute(query=query)

    # Then
    assert query in result
    assert "JSON array of strings" in result


def test_similar_keywords_prompt_format():
    """Test that SIMILAR_KEYWORDS_PROMPT is correctly formatted."""
    # Given
    rule = "Test rule"
    chunks = "Test chunks"

    # When
    result = SIMILAR_KEYWORDS_PROMPT.safe_substitute(rule=rule, chunks=chunks)

    # Then
    assert rule in result
    assert chunks in result
    assert "JSON array of strings" in result


def test_decompose_query_prompt_format():
    """Test that DECOMPOSE_QUERY_PROMPT is correctly formatted."""
    # Given
    query = "Test query"

    # When
    result = DECOMPOSE_QUERY_PROMPT.safe_substitute(query=query)

    # Then
    assert query in result
    assert "JSON array of strings" in result


def test_schema_prompt_format():
    """Test that SCHEMA_PROMPT is correctly formatted."""
    # Given
    documents = "Test documents"
    columns = "Test columns"
    entity_types = "Test entity types"

    # When
    result = SCHEMA_PROMPT.safe_substitute(
        documents=documents, columns=columns, entity_types=entity_types
    )

    # Then
    assert documents in result
    assert columns in result
    assert entity_types in result
    assert "head" in result
    assert "relation" in result
    assert "tail" in result
