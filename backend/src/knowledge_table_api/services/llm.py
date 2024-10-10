"""The functions for generating responses from the language model."""

import json
import logging
from typing import Any, List, Literal, Type, Union

from knowledge_table_api.models.graph import Table
from knowledge_table_api.models.llm_response import (
    BoolResponseModel,
    IntArrayResponseModel,
    IntResponseModel,
    KeywordsResponseModel,
    SchemaResponseModel,
    StrArrayResponseModel,
    StrResponseModel,
    SubQueriesResponseModel,
)
from knowledge_table_api.models.query import Rule
from knowledge_table_api.services.llm_service import LLMService
from knowledge_table_api.services.prompts import (
    BASE_PROMPT,
    BOOL_INSTRUCTIONS,
    DECOMPOSE_QUERY_PROMPT,
    INT_ARRAY_INSTRUCTIONS,
    KEYWORD_PROMPT,
    SCHEMA_PROMPT,
    SIMILAR_KEYWORDS_PROMPT,
    STR_ARRAY_INSTRUCTIONS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_response(
    llm_service: LLMService,
    query: str,
    chunks: str,
    rules: list[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
) -> dict[str, Any]:
    """Generate a response from the language model."""
    logger.info(f"Generating response for query: {query} in format: {format}")

    # Set the output model based on the format
    output_model: Type[
        Union[
            BoolResponseModel,
            IntArrayResponseModel,
            IntResponseModel,
            StrArrayResponseModel,
            StrResponseModel,
        ]
    ]

    str_rule = next(
        (rule for rule in rules if rule.type in ["must_return", "may_return"]),
        None,
    )
    int_rule = next(
        (rule for rule in rules if rule.type == "max_length"), None
    )

    format_specific_instructions = ""
    if format == "bool":
        format_specific_instructions = BOOL_INSTRUCTIONS
        output_model = BoolResponseModel
    elif format in ["str_array", "str"]:
        str_rule_line = _get_str_rule_line(str_rule, query)
        int_rule_line = _get_int_rule_line(int_rule)
        format_specific_instructions = STR_ARRAY_INSTRUCTIONS.substitute(
            str_rule_line=str_rule_line, int_rule_line=int_rule_line
        )
        output_model = (
            StrArrayResponseModel
            if format == "str_array"
            else StrResponseModel
        )
    elif format in ["int", "int_array"]:
        int_rule_line = _get_int_rule_line(int_rule)
        format_specific_instructions = INT_ARRAY_INSTRUCTIONS.substitute(
            int_rule_line=int_rule_line
        )
        output_model = (
            IntArrayResponseModel
            if format == "int_array"
            else IntResponseModel
        )

    prompt = BASE_PROMPT.substitute(
        query=query,
        chunks=chunks,
        format_specific_instructions=format_specific_instructions,
    )

    try:
        model = "gpt-4o"
        response = await llm_service.generate_completion(
            prompt, output_model, model
        )
        result = response.model_dump()
        return {
            "answer": (
                result.get("answer")
                if result.get("answer") not in ["None", ["None"]]
                else None
            )
        }
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return {"answer": None}


async def get_keywords(
    llm_service: LLMService, query: str
) -> dict[str, list[str] | None]:
    """Extract keywords from a query using the language model."""
    prompt = KEYWORD_PROMPT.substitute(query=query)

    try:
        response = await llm_service.generate_completion(
            prompt, KeywordsResponseModel
        )
        keywords = response.keywords
        return {
            "keywords": keywords if keywords and keywords != ["None"] else None
        }
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return {"keywords": None}


async def get_similar_keywords(
    llm_service: LLMService, chunks: str, rule: list[str]
) -> dict[str, Any]:
    """Retrieve keywords similar to the provided keywords from the text chunks."""
    logger.info(
        f"Retrieving keywords which are similar to the provided keywords: {rule}"
    )

    prompt = SIMILAR_KEYWORDS_PROMPT.substitute(
        rule=rule,
        chunks=chunks,
    )

    try:
        response = await llm_service.generate_completion(
            prompt, KeywordsResponseModel
        )
        keywords = response.keywords
        return {
            "keywords": keywords if keywords and keywords != ["None"] else None
        }
    except Exception as e:
        logger.error(f"Error getting similar keywords: {e}")
        return {"keywords": None}


async def decompose_query(
    llm_service: LLMService, query: str
) -> dict[str, Any]:
    """Decompose a query into multiple sub-queries."""
    logger.info("Decomposing query into multiple sub-queries.")

    prompt = DECOMPOSE_QUERY_PROMPT.substitute(query=query)

    try:
        response = await llm_service.generate_completion(
            prompt, SubQueriesResponseModel
        )
        sub_queries = response.sub_queries
        return {
            "sub-queries": (
                sub_queries
                if sub_queries and sub_queries != ["None"]
                else None
            )
        }
    except Exception as e:
        logger.error(f"Error decomposing query: {e}")
        return {"sub-queries": None}


async def generate_schema(
    llm_service: LLMService, data: Table
) -> dict[str, Any]:
    """Generate a schema for the table based on column information and questions."""
    logger.info("Generating schema.")

    # Ensure documents is a list of strings
    documents: List[str] = list(
        set(str(row.document.name) for row in data.rows)
    )

    prepared_data = {
        "documents": documents,
        "columns": [
            {
                "id": column.id,
                "entity_type": column.prompt.entityType,
                "type": column.prompt.type,
                "question": column.prompt.query,
            }
            for column in data.columns
        ],
    }

    # Ensure prepared_data["columns"] is a list
    if not isinstance(prepared_data["columns"], list):
        logger.error("prepared_data['columns'] is not a list")
        return {"schema": None}

    entity_types: List[str] = [
        column["entity_type"] for column in prepared_data["columns"]
    ]

    # Ensure we're joining a list of strings
    prompt = SCHEMA_PROMPT.substitute(
        documents=", ".join(documents) if documents else "",
        entity_types=", ".join(entity_types) if entity_types else "",
        columns=json.dumps(prepared_data["columns"]),
    )

    try:
        response = await llm_service.generate_completion(
            prompt, SchemaResponseModel
        )
        schema = response.model_dump()
        return {"schema": schema if schema.get("relationships") else None}
    except Exception as e:
        logger.error(f"Error generating schema: {e}")
        return {"schema": None}


def _get_str_rule_line(str_rule: Rule | None, query: str) -> str:
    if str_rule:
        if str_rule.type == "must_return" and str_rule.options:
            options_str = ", ".join(
                f'"{option}"' for option in str_rule.options
            )
            return f"You should only consider these possible values when answering the question: {options_str}. If these values do not exist in the raw text chunks, or if they do not correctly answer the question, respond with None."
        elif str_rule.type == "may_return" and str_rule.options:
            options_str = ", ".join(str_rule.options)
            return f"For example: Query: {query} Response: {options_str}, etc... If you cannot find a related, correct answer in the raw text chunks, respond with None."
    return ""


def _get_int_rule_line(int_rule: Rule | None) -> str:
    if int_rule and int_rule.length is not None:
        return f"Your answer should only return up to {int_rule.length} items. If you have to choose between multiple, return those that answer the question the best. If you cannot find any suitable answer, respond with None."
    return ""
