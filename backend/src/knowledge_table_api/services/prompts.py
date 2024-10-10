"""The prompts for the language model."""

from string import Template

BASE_PROMPT = Template(
    """
Your job is to answer the following question using only the raw context provided in the raw text chunks below.

Question: $query

Raw Text Chunks: $chunks

$format_specific_instructions

Provide your answer based on the given instructions. Be concise and accurate. If you cannot find an answer in the provided context, return None.
"""
)

BOOL_INSTRUCTIONS = """
If the question is asking for a verification or boolean answer, respond with "True" or "False".
If the question is not asking for a verification or boolean answer, or if you can't find an answer, respond with None.
Do not provide any supporting information.
"""

STR_ARRAY_INSTRUCTIONS = Template(
    """
$str_rule_line
$int_rule_line
If the question can be answered in a single string, then provide that string as the answer.
If multiple strings are required, provide them as a list.
If you cannot find an answer, return None.
"""
)

INT_ARRAY_INSTRUCTIONS = Template(
    """
$int_rule_line
If the question can be answered with a single integer, provide that integer as the answer.
If multiple integers are required, provide them as a list.
If you cannot find an answer, return None.
"""
)

KEYWORD_PROMPT = Template(
    """
Your job is to extract the most relevant keywords from the query below.
Make sure the words are in their simplest, most common form. Focus on verbs and nouns.

Query: $query

Provide the keywords as a list of strings. If you cannot extract any relevant keywords, return None.
"""
)

SIMILAR_KEYWORDS_PROMPT = Template(
    """
Your job is to retrieve additional keywords which are similar to these words: $rule from the raw text chunks below.
Return only words that are semantically related to these terms and their respective domain. Use only the context provided in the text chunks below.

Raw Text Chunks: $chunks

Provide the similar keywords as a list of strings. If you cannot find any similar keywords, return None.
"""
)

DECOMPOSE_QUERY_PROMPT = Template(
    """
Your job is to decompose the question below into simple, relevant sub questions. The sub-questions should capture semantic variations of the original question.

If the query is simple enough as is, just return the original query.

Your response should contain at most 3 sub-queries.

Question: $query

Provide the sub-queries as a list of strings. If you cannot decompose the query or if it's already simple enough, return None.
"""
)

SCHEMA_PROMPT = Template(
    """
Given the following information about columns in a knowledge table:

Documents: $documents
Columns: $columns

Generate a schema that includes relationships between columns if relevant (e.g., "Diseases, treated_by, Treatments")

For each relationship:
- Use ONLY the exact column names as provided. The available column names are: $entity_types
- The 'head' and 'tail' in each relationship MUST be one of these exact column names
- Create meaningful 'relation' names based on the column information and questions provided
- Create a relationship between columns if it makes sense based on the questions

Do not use entity types or any other names not in the provided column list.
Do not provide any supporting information.

Provide the relationships as a list of objects, each containing 'head', 'relation', and 'tail' fields. If you cannot generate any meaningful relationships, return None.
"""
)
