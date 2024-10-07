"""The functions for generating responses from the language model."""

import json
import logging
import os
from typing import Any, Literal

from dotenv import load_dotenv
from openai import OpenAI

from knowledge_table_api.models.llm_response import (
    BoolResponseModel,
    IntArrayResponseModel,
    IntResponseModel,
    StrArrayResponseModel,
)
from knowledge_table_api.models.query import Rule
from knowledge_table_api.models.graph import Table

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_response(
    query: str,
    chunks: str,
    rules: list[Rule],
    format: Literal["int", "str", "bool", "int_array", "str_array"],
) -> dict[str, Any]:
    """Generate a response from the language model."""
    logger.info(f"Generating response for query: {query} in format: {format}")

    str_rule = None
    int_rule = None

    if rules:
        for rule in rules:
            # Assumes "must_return" or "may_return" could be provided, but not both
            if rule.type in ["must_return", "may_return"]:
                str_rule = rule
            elif rule.type == "max_length":
                int_rule = rule

    base_prompt = """
    Your job is to answer the following question using only the raw context provided in the raw text chunks below.

    """

    question_and_context = f"""

    Question: {query}

    Raw Text Chunks: {chunks}

    """

    if format == "bool":
        prompt = (
            base_prompt
            + """
            If the question is not asking for a verification or boolean answer, respond with "not found".
            You should only return "True", "False", or "not found". Do not provide any supporting information. Do not wrap the response in JSON or Python markers. Just the answer.
            """
            + question_and_context
        )
    elif format == "str_array" or format == "str":
        str_rule_line = ""
        int_rule_line = ""

        if str_rule:
            if str_rule.type == "must_return" and str_rule.options:
                str_rule_line = f"""
                You should only consider these possible values when answering the qustion: {", ".join([f'"{option}"' for option in str_rule.options])}.
                If these values do not exist in the raw text chunks, or if they do not correctly answer the question, respond with "not found".
                """

            elif str_rule.type == "may_return" and str_rule.options:
                str_rule_line = f"""
                For example:
                Query: {query}
                Response: {", ".join(str_rule.options)}, etc...

                If you cannot find a related, correct answer in the raw text chunks, respond with "not found".
                """
        if int_rule:
            int_rule_line = f"Your answer should only return up to {int_rule.length} strings. If you have to choose between muliple, return those that answer the question the best."

        if format == "str_array" or format == "str":
            prompt = (
                base_prompt
                + f"""
                Your answer should be in the format of a JSON array of strings.

                {str_rule_line}

                {int_rule_line}

                If the question can be answered in a single string, then answer with a JSON array containing a single string.

                Do not provide any supporting information. Do not wrap the response in JSON or Python markers. Ensure the output is in plain JSON and parsable via `json.loads()`.

                """
                + question_and_context
            )

    elif format == "int" or format == "int_array":
        int_rule_line = ""
        if int_rule:
            int_rule_line = f"Your answer should only return up to {int_rule.length} integers. If you have to choose between muliple, return those that answer the question the best."
        if format == "int_array":
            prompt = (
                base_prompt
                + f"""
                Your answer should be in the format of a JSON array of integers. If it can be answered in a single integer, then answer with a JSON array containing a single integer.

                {int_rule_line}

                Do not provide any supporting information. Do not wrap the response in JSON or Python markers. The response should be parsable by `json.loads()`.

                """
                + question_and_context
            )
        elif format == "int":
            prompt = (
                base_prompt
                + """
                Your answer should be in the format of a single integer.

                Do not provide any supporting information. Do not wrap the response in JSON or Python markers.

                """
                + question_and_context
            )

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=512,
    )

    llm_response = response.choices[0].message.content

    logger.info(f"Response generated: {llm_response}")

    # validated_response: int | str | list[str]
    if llm_response in [None, "not found", ["not found"]]:
        logger.error("No answer generated. Returning None")
        return {"answer": None}

    elif format == "int":
        try:
            if llm_response is not None:
                validated_int_response = IntResponseModel.validate_response(
                    int(llm_response)
                )
            return {"answer": validated_int_response}
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {"answer": None}

    elif format == "int_array":
        try:
            if llm_response is None:
                return {"answer": None}
            validated_int_arr_response = (
                IntArrayResponseModel.validate_response(
                    json.loads(llm_response), int_rule
                )
            )
            return {"answer": validated_int_arr_response}
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {"answer": None}

    elif format == "bool":
        try:
            if llm_response is None:
                return {"answer": None}
            validated_bool_response = BoolResponseModel.validate_response(
                llm_response
            )
            return {"answer": validated_bool_response}
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {"answer": None}

    elif format == "str":
        try:
            if llm_response is None:
                return {"answer": None}
            validated_str_response = StrArrayResponseModel.validate_response(
                json.loads(llm_response), str_rule, int_rule
            )
            if validated_str_response is not None:
                string_out = ", ".join(validated_str_response)
            else:
                string_out = ""
            return {"answer": string_out}
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {"answer": None}

    elif format == "str_array":
        try:
            if llm_response is None:
                return {"answer": None}
            validated_str_arr_response = (
                StrArrayResponseModel.validate_response(
                    json.loads(llm_response), str_rule, int_rule
                )
            )
            return {"answer": validated_str_arr_response}
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {"answer": None}

    else:
        logger.error("Invalid response format provided.")
        return {"answer": None}


async def get_keywords(query: str) -> list[str]:
    """Extract keywords from a query using the language model."""
    keyword_prompt = f"""
    Your job is to extract the most relevant keywords from the query below. Return the keywords as a JSON array of strings.
    Make sure the words are in their simplest, most common form. Focus on verbs and nouns.
    Do not wrap the response in JSON or Python markers. If you cannot find any keywords, return an empty array.

    Query: {query}
    Keywords:"""

    keyword_response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": keyword_prompt}],
        max_tokens=256,
    )

    if keyword_response.choices[0].message.content is None:
        return []
    keywords = json.loads(keyword_response.choices[0].message.content)
    return keywords


async def get_similar_keywords(chunks: str, rule: list[str]) -> dict[str, Any]:
    """Retrieve keywords similar to the provided keywords from the text chunks."""
    logger.info(
        f"Retrieving keywords which are similar to the provided keywords: {rule}"
    )

    similar_keywords_prompt = f"""
    Your job is to retrieve additional keywords which are similar to these words: {rule} from the raw text chunks below.
    Return only words that are semantically related to these terms and their respective domain. Use only the context provided in the text chunks below.

    Raw Text Chunks: {chunks}

    Your answer should be in the format of a JSON array of concise strings.
    Do not provide any supporting information. Do not wrap the response in JSON or Python markers. Just the answer.
    """

    similar_keyword_response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": similar_keywords_prompt}],
        max_tokens=512,
    )

    if similar_keyword_response.choices[0].message.content is None:
        return {"keywords": []}
    similar_keywords = json.loads(
        similar_keyword_response.choices[0].message.content
    )
    return {"keywords": similar_keywords}


async def decompose_query(query: str) -> dict[str, Any]:
    """Decompose a query into multiple sub-queries."""
    logger.info("Decomposing query into multiple sub-queries.")

    similar_keywords_prompt = f"""
    Your job is to decompose the question below into simple, relevant sub questions.The sub-questions should capture semantic variations of the original question.

    If the query is simple enough as is, just return the original query.

    Your response should be in the format of a JSON array of strings. At most, you should return 3 sub-queries.
    Do not provide any supporting information. Do not wrap the response in JSON or Python markers. The response should be parsable by `json.loads()`.

    Question: {query}
    Sub Questions:"""

    similar_keyword_response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": similar_keywords_prompt}],
        max_tokens=512,
    )

    if similar_keyword_response.choices[0].message.content is None:
        return {"sub-queries": []}
    sub_queries = json.loads(
        similar_keyword_response.choices[0].message.content
    )
    print(sub_queries)
    return {"sub-queries": sub_queries}

async def generate_schema(data: Table) -> dict[str, Any]:
    """Generate a schema for the table based on column information and questions."""
    logger.info("Generating schema.")

    prepared_data = {
        "documents": list(set(row.document.name for row in data.rows)),
        "columns": [
            {
                "id": column.id,
                "entity_type": column.prompt.entityType,
                "type": column.prompt.type,
                "question": column.prompt.query
            }
            for column in data.columns
        ]
    }

    # Extract entity types from the prepared data
    entity_types = [column['entity_type'] for column in prepared_data['columns']]

    schema_prompt = f"""
    Given the following information about columns in a knowledge table:
    
    Documents: {', '.join(prepared_data['documents'])}
    Columns: {json.dumps(prepared_data['columns'], indent=2)}
    
    Generate a schema that includes the following relationships:
    1. From Document to each entity type (e.g., "Document, contains, Disease")
    2. Between entity types (e.g., "Disease, treated_by, Treatment")
    3. Ensure that each entity type is used in at least one relationship with "Document"
    4. Create meaningful relationships based on the column information, entity types, and questions provided

    The output should be a JSON object containing:
    - 'relationships': An array of objects, each containing 'head', 'relation', and 'tail'

    For each relationship:
    - Use the actual entity types (e.g., "Disease", "Treatment") instead of column IDs
    - Ensure that the head and tail can only be the names of the columns provided: {', '.join(entity_types)}
    - Create meaningful relationships based on the column information, entity types, and questions provided
    - Ensure that each entity type is used in at least one relationship with "Document"
    - Create a relationship between entity types if it makes sense based on the questions

    Do not provide any supporting information. Ensure the output is in plain JSON and parsable via `json.loads()`.

    Schema:"""

    schema_response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": schema_prompt}],
        max_tokens=2000,
    )

    # Check if the response is valid
    if not schema_response.choices or not schema_response.choices[0].message.content:
        logger.error("Received an empty response from the OpenAI API.")
        return {"schema": {"relationships": []}}

    try:
        return {"schema": json.loads(schema_response.choices[0].message.content)}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response: {e}")
        return {"schema": {"relationships": []}}