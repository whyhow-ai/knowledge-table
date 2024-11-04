"""Query service."""

import logging
import re
from typing import Any, Awaitable, Callable, Dict, List, Union

from app.models.query_core import Chunk, FormatType, QueryType, Rule
from app.schemas.query_api import (
    QueryResult,
    ResolvedEntitySchema,
    SearchResponse,
)
from app.services.llm_service import (
    CompletionService,
    generate_inferred_response,
    generate_response,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SearchMethod = Callable[[str, str, List[Rule]], Awaitable[SearchResponse]]


def get_search_method(
    query_type: QueryType, vector_db_service: Any
) -> SearchMethod:
    """Get the search method based on the query type."""
    if query_type == "decomposition":
        return vector_db_service.decomposed_search
    elif query_type == "hybrid":
        return vector_db_service.hybrid_search
    else:  # simple_vector
        return lambda q, d, r: vector_db_service.vector_search([q], d)


def extract_chunks(search_response: SearchResponse) -> List[Chunk]:
    """Extract chunks from the search response."""
    return (
        search_response["chunks"]
        if isinstance(search_response, dict)
        else search_response.chunks
    )


def replace_keywords(
    text: Union[str, List[str]],
    keyword_replacements: Dict[str, str],
    conditional_replacements: List[tuple[List[str], str]] = [],
) -> tuple[Union[str, List[str]], Dict[str, Union[str, List[str]]]]:
    """Replace keywords in text and return both the modified text and transformation details."""
    if not text or (not keyword_replacements and not conditional_replacements):
        return text, {"original": text, "resolved": text}

    # Handle list of strings
    if isinstance(text, list):
        original_text = text.copy()
        result = []
        modified = False

        # Create a single regex pattern for all keywords
        # pattern = "|".join(map(re.escape, keyword_replacements.keys()))
        # regex = re.compile(f"\\b({pattern})\\b")

        for item in text:
            new_item, _ = replace_keywords_in_string(
                item, keyword_replacements, conditional_replacements
            )
            result.append(new_item)
            if new_item != item:
                modified = True

        if modified:
            return result, {"original": original_text, "resolved": result}
        return result, {"original": original_text, "resolved": result}

    # Handle single string
    return replace_keywords_in_string(
        text, keyword_replacements, conditional_replacements
    )


def parse_conditional_replacement(option: str) -> tuple[List[str], str]:
    """Parse a conditional replacement rule like 'word a + word b : word c'."""
    conditions, replacement = option.split(":")
    required_words = [word.strip() for word in conditions.split("+")]
    return required_words, replacement.strip()


def replace_keywords_in_string(
    text: str,
    keyword_replacements: Dict[str, str],
    conditional_replacements: List[tuple[List[str], str]] = [],
) -> tuple[str, Dict[str, Union[str, List[str]]]]:
    """Keywords for single string."""
    if not text or (not keyword_replacements and not conditional_replacements):
        return text, {"original": text, "resolved": text}

    result = text

    # First check conditional replacements
    for required_words, replacement in conditional_replacements:
        # Check if all required words are present
        if all(word.lower() in text.lower() for word in required_words):
            # Create a pattern that matches any of the required words
            pattern = "|".join(map(re.escape, required_words))
            # Replace all occurrences of the required words with the replacement
            result = re.sub(
                f"\\b({pattern})\\b", replacement, result, flags=re.IGNORECASE
            )

    # Then do normal replacements
    if keyword_replacements:
        pattern = "|".join(map(re.escape, keyword_replacements.keys()))
        regex = re.compile(f"\\b({pattern})\\b")
        result = regex.sub(lambda m: keyword_replacements[m.group()], result)

    if result != text:
        return result, {"original": text, "resolved": result}
    return text, {"original": text, "resolved": text}


async def process_query(
    query_type: QueryType,
    query: str,
    document_id: str,
    rules: List[Rule],
    format: FormatType,
    llm_service: CompletionService,
    vector_db_service: Any,
) -> QueryResult:
    """Process the query based on the specified type."""
    search_method = get_search_method(query_type, vector_db_service)

    search_response = await search_method(query, document_id, rules)
    chunks = extract_chunks(search_response)
    concatenated_chunks = " ".join(chunk.content for chunk in chunks)

    answer = await generate_response(
        llm_service, query, concatenated_chunks, rules, format
    )
    answer_value = answer["answer"]

    transformations: Dict[str, Union[str, List[str]]] = {
        "original": "",
        "resolved": "",
    }

    result_chunks = []

    if format in ["str", "str_array"]:
        # Extract rules by type
        resolve_entity_rules = [
            rule for rule in rules if rule.type == "resolve_entity"
        ]
        conditional_rules = [
            rule for rule in rules if rule.type == "resolve_conditional"
        ]

        result_chunks = (
            []
            if answer_value in ("not found", None)
            and query_type != "decomposition"
            else chunks
        )

        # Process both types of replacements if we have an answer
        if answer_value and (resolve_entity_rules or conditional_rules):
            # Build regular replacements dictionary
            replacements: Dict[str, str] = {}
            if resolve_entity_rules:
                for rule in resolve_entity_rules:
                    if rule.options:
                        rule_replacements = dict(
                            option.split(":") for option in rule.options
                        )
                        replacements.update(rule_replacements)

            # Build conditional replacements list
            conditional_replacements: List[tuple[List[str], str]] = []
            if conditional_rules:
                for rule in conditional_rules:
                    if rule.options:
                        for option in rule.options:
                            required_words, replacement = (
                                parse_conditional_replacement(option)
                            )
                            conditional_replacements.append(
                                (required_words, replacement)
                            )

            # Apply replacements if we have any
            if replacements or conditional_replacements:
                print(f"Resolving entities in answer: {answer_value}")
                if isinstance(answer_value, list):
                    transformed_list, transform_dict = replace_keywords(
                        answer_value, replacements, conditional_replacements
                    )
                    transformations = transform_dict
                    answer_value = transformed_list
                else:
                    transformed_value, transform_dict = replace_keywords(
                        answer_value, replacements, conditional_replacements
                    )
                    transformations = transform_dict
                    answer_value = transformed_value

    return QueryResult(
        answer=answer_value,
        chunks=result_chunks[:10],
        resolved_entities=(
            [
                ResolvedEntitySchema(
                    original=transformations["original"],
                    resolved=transformations["resolved"],
                    source={"type": "column", "id": "some-id"},
                    entityType="some-type",
                )
            ]
            if transformations["original"] or transformations["resolved"]
            else None
        ),
    )


# Convenience functions for specific query types
async def decomposition_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: FormatType,
    llm_service: CompletionService,
    vector_db_service: Any,
) -> QueryResult:
    """Process the query based on the decomposition type."""
    return await process_query(
        "decomposition",
        query,
        document_id,
        rules,
        format,
        llm_service,
        vector_db_service,
    )


async def hybrid_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: FormatType,
    llm_service: CompletionService,
    vector_db_service: Any,
) -> QueryResult:
    """Process the query based on the hybrid type."""
    return await process_query(
        "hybrid",
        query,
        document_id,
        rules,
        format,
        llm_service,
        vector_db_service,
    )


async def simple_vector_query(
    query: str,
    document_id: str,
    rules: List[Rule],
    format: FormatType,
    llm_service: CompletionService,
    vector_db_service: Any,
) -> QueryResult:
    """Process the query based on the simple vector type."""
    return await process_query(
        "simple_vector",
        query,
        document_id,
        rules,
        format,
        llm_service,
        vector_db_service,
    )


async def inference_query(
    query: str,
    rules: List[Rule],
    format: FormatType,
    llm_service: CompletionService,
) -> QueryResult:
    """Generate a response, no need for vector retrieval."""
    answer = await generate_inferred_response(
        llm_service, query, rules, format
    )
    answer_value = answer["answer"]

    # Extract rules by type
    resolve_entity_rules = [
        rule for rule in rules if rule.type == "resolve_entity"
    ]
    conditional_rules = [
        rule for rule in rules if rule.type == "resolve_conditional"
    ]

    if answer_value and (resolve_entity_rules or conditional_rules):
        # Build regular replacements
        replacements = {}
        if resolve_entity_rules:
            for rule in resolve_entity_rules:
                if rule.options:
                    rule_replacements = dict(
                        option.split(":") for option in rule.options
                    )
                    replacements.update(rule_replacements)

        # Build conditional replacements
        conditional_replacements = []
        if conditional_rules:
            for rule in conditional_rules:
                if rule.options:
                    for option in rule.options:
                        required_words, replacement = (
                            parse_conditional_replacement(option)
                        )
                        conditional_replacements.append(
                            (required_words, replacement)
                        )

        if replacements or conditional_replacements:
            print(f"Resolving entities in answer: {answer_value}")
            answer_value, _ = replace_keywords(
                answer_value, replacements, conditional_replacements
            )

    return QueryResult(answer=answer_value, chunks=[])
