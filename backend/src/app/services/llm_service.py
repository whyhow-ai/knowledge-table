"""The functions for generating responses from the language model."""

import json
import logging
from typing import Any, List, Tuple, Type, Union

from app.models.llm_responses import (
    BoolResponseModel,
    IntArrayResponseModel,
    IntResponseModel,
    KeywordsResponseModel,
    SchemaResponseModel,
    StrArrayResponseModel,
    StrResponseModel,
    SubQueriesResponseModel,
)
from app.models.query_core import FormatType, Rule
from app.models.table import Table
from app.services.llm.base import CompletionService
from app.services.llm.openai_prompts import (
    BASE_PROMPT,
    BOOL_INSTRUCTIONS,
    DECOMPOSE_QUERY_PROMPT,
    INFERRED_BASE_PROMPT,
    INT_ARRAY_INSTRUCTIONS,
    KEYWORD_PROMPT,
    SCHEMA_PROMPT,
    SIMILAR_KEYWORDS_PROMPT,
    STR_ARRAY_INSTRUCTIONS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_model_and_instructions(
    format: str, rules: list[Rule], query: str
) -> Tuple[
    Type[
        Union[
            BoolResponseModel,
            IntArrayResponseModel,
            IntResponseModel,
            StrArrayResponseModel,
            StrResponseModel,
        ]
    ],
    str,
]:
    """
    Get the appropriate output model and instructions based on the format.

    Parameters
    ----------
    format : str
        The desired format of the response.
    rules : list[Rule]
        A list of rules to apply when generating the response.
    query : str
        The user's query to be answered.

    Returns
    -------
    Tuple[Type[Union[BoolResponseModel, IntArrayResponseModel, IntResponseModel, StrArrayResponseModel, StrResponseModel]], str]
        A tuple containing the appropriate output model and format-specific instructions.
    """
    str_rule = next(
        (rule for rule in rules if rule.type in ["must_return", "may_return"]),
        None,
    )
    int_rule = next(
        (rule for rule in rules if rule.type == "max_length"), None
    )

    if format == "bool":
        return BoolResponseModel, BOOL_INSTRUCTIONS
    elif format in ["str_array", "str"]:
        str_rule_line = _get_str_rule_line(str_rule, query)
        int_rule_line = _get_int_rule_line(int_rule)
        instructions = STR_ARRAY_INSTRUCTIONS.substitute(
            str_rule_line=str_rule_line, int_rule_line=int_rule_line
        )
        return (
            StrArrayResponseModel
            if format == "str_array"
            else StrResponseModel
        ), instructions
    elif format in ["int", "int_array"]:
        int_rule_line = _get_int_rule_line(int_rule)
        instructions = INT_ARRAY_INSTRUCTIONS.substitute(
            int_rule_line=int_rule_line
        )
        return (
            IntArrayResponseModel
            if format == "int_array"
            else IntResponseModel
        ), instructions
    else:
        raise ValueError(f"Unsupported format: {format}")


async def generate_response(
    llm_service: CompletionService,
    query: str,
    chunks: str,
    rules: list[Rule],
    format: FormatType,
) -> dict[str, Any]:
    """
    Generate a response from the language model based on the given query and format.

    Parameters
    ----------
    llm_service : CompletionService
        The language model service to use for generating the response.
    query : str
        The user's query to be answered.
    chunks : str
        The context or relevant text chunks for answering the query.
    rules : list[Rule]
        A list of rules to apply when generating the response.
    format : Literal["int", "str", "bool", "int_array", "str_array"]
        The desired format of the response.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the generated answer or None if an error occurs.
    """
    logger.info(f"Generating response for query: {query} in format: {format}")

    output_model, format_specific_instructions = _get_model_and_instructions(
        format, rules, query
    )

    prompt = BASE_PROMPT.substitute(
        query=query,
        chunks=chunks,
        format_specific_instructions=format_specific_instructions,
    )

    try:
        response = await llm_service.generate_completion(prompt, output_model)
        logger.info(f"Raw response from LLM: {response}")

        if response is None or response.answer is None:
            logger.warning("LLM returned None response")
            return {"answer": None}

        logger.info(f"Processed response: {response.answer}")
        return {"answer": response.answer}
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}", exc_info=True)
        return {"answer": None}


async def generate_inferred_response(
    llm_service: CompletionService,
    query: str,
    rules: list[Rule],
    format: FormatType,
) -> dict[str, Any]:
    """
    Generate a response from the language model based on the given query and format.

    Parameters
    ----------
    llm_service : CompletionService
        The language model service to use for generating the response.
    query : str
        The user's query to be answered.
    rules : list[Rule]
        A list of rules to apply when generating the response.
    format : Literal["int", "str", "bool", "int_array", "str_array"]
        The desired format of the response.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the generated answer or None if an error occurs.
    """
    logger.info(
        f"Generating inferred response for query: {query} in format: {format}"
    )

    output_model, format_specific_instructions = _get_model_and_instructions(
        format, rules, query
    )
    prompt = INFERRED_BASE_PROMPT.substitute(
        query=query,
        format_specific_instructions=format_specific_instructions,
    )

    try:
        response = await llm_service.generate_completion(prompt, output_model)
        logger.info(f"Raw response from LLM: {response}")

        if response is None or response.answer is None:
            logger.warning("LLM returned None response")
            return {"answer": None}

        logger.info(f"Processed response: {response.answer}")
        return {"answer": response.answer}
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}", exc_info=True)
        return {"answer": None}


async def get_keywords(
    llm_service: CompletionService, query: str
) -> dict[str, list[str] | None]:
    """
    Extract keywords from a query using the language model.

    Parameters
    ----------
    llm_service : CompletionService
        The language model service to use for keyword extraction.
    query : str
        The query from which to extract keywords.

    Returns
    -------
    dict[str, list[str] | None]
        A dictionary containing the extracted keywords or None if an error occurs.
    """
    # Create the prompt
    prompt = KEYWORD_PROMPT.substitute(query=query)

    try:
        # Generate the response
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
    llm_service: CompletionService, chunks: str, rule: list[str]
) -> dict[str, Any]:
    """
    Retrieve keywords similar to the provided keywords from the given text chunks.

    Parameters
    ----------
    llm_service : CompletionService
        The language model service to use for finding similar keywords.
    chunks : str
        The text chunks to search for similar keywords.
    rule : list[str]
        The list of keywords to use as a reference for finding similar ones.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the similar keywords found or None if an error occurs.
    """
    logger.info(
        f"Retrieving keywords which are similar to the provided keywords: {rule}"
    )

    # Create the prompt
    prompt = SIMILAR_KEYWORDS_PROMPT.substitute(
        rule=rule,
        chunks=chunks,
    )

    try:

        # Generate the response
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
    llm_service: CompletionService, query: str
) -> dict[str, Any]:
    """
    Decompose a complex query into multiple simpler sub-queries.

    Parameters
    ----------
    llm_service : CompletionService
        The language model service to use for query decomposition.
    query : str
        The complex query to be decomposed.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the list of sub-queries or None if an error occurs.
    """
    logger.info("Decomposing query into multiple sub-queries.")

    # Create the prompt
    prompt = DECOMPOSE_QUERY_PROMPT.substitute(query=query)

    try:

        # Generate the response
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
    llm_service: CompletionService, data: Table
) -> dict[str, Any]:
    """
    Generate a schema for the table based on column information and questions.

    Parameters
    ----------
    llm_service : CompletionService
        The language model service to use for schema generation.
    data : Table
        The table data containing information about columns, rows, and documents.

    Returns
    -------
    dict[str, Any]
        A dictionary containing the generated schema or None if an error occurs.
    """
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
    """
    Generate a string rule line based on the given string rule and query.

    Parameters
    ----------
    str_rule : Rule | None
        The string rule to process.
    query : str
        The original query for context.

    Returns
    -------
    str
        A formatted string containing instructions based on the rule, or an empty string if no rule is provided.
    """
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
    """
    Generate an integer rule line based on the given integer rule.

    Parameters
    ----------
    int_rule : Rule | None
        The integer rule to process.

    Returns
    -------
    str
        A formatted string containing instructions based on the rule, or an empty string if no rule is provided.
    """
    if int_rule and int_rule.length is not None:
        return f"Your answer should only return up to {int_rule.length} items. If you have to choose between multiple, return those that answer the question the best. If you cannot find any suitable answer, respond with None."
    return ""
