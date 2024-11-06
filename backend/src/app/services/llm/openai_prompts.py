"""The prompts for the language model."""

from string import Template

BASE_PROMPT = Template(
    """
You are an expert assistant whose job is to answer the following question using **only** the information provided in the **Context**. Do not use any prior knowledge or external information.

---

**Question**: $query

---

**Context**:
$chunks

---

$format_specific_instructions

**Instructions**:

- Provide your answer based strictly on the given context.
- Be concise and accurate.
- Do not include any introductory or concluding remarks.
- If the answer is not present in the context, respond exactly with "None".

**Answer**:
"""
)

INFERRED_BASE_PROMPT = Template(
    """
Answer the following question following the formatting instructions at the bottom. Do not include, quotes, formatting, or any explanation or extra information. Just answer the question.

**Question**: $query
**Answer**:

$format_specific_instructions

"""
)

BOOL_INSTRUCTIONS = """
**Special Instructions for Boolean Questions**:

- If the question is asking for a verification or requires a boolean answer, respond with True or False.
- If you cannot answer the question, respond exactly with 'None'.
- Do not provide any explanations or additional information.
"""

STR_ARRAY_INSTRUCTIONS = Template(
    """
$str_rule_line
$int_rule_line

**Special Instructions for String Responses**:

- If the answer is a single string, provide a single string.
- If multiple strings are required, provide them as a JSON array of strings.
- If you cannot find an answer, respond exactly with 'None'.
- Do not include any additional text or explanation.
"""
)

INT_ARRAY_INSTRUCTIONS = Template(
    """
$int_rule_line

**Special Instructions for Integer Responses**:

- If the answer is a single integer, provide the integer as a number.
- If multiple integers are required, provide them as a JSON array of integers.
- If you cannot find an answer, respond exactly with 'None'.
- Do not include any additional text or explanation.
"""
)

KEYWORD_PROMPT = Template(
    """
You are tasked with extracting the most relevant keywords from the following query. Focus on the main nouns and verbs that capture the essence of the query.

---

**Query**: $query

---

**Instructions**:

- Provide the keywords as a JSON array of strings.
- Ensure all words are in their base (lemmatized) form.
- If you cannot extract any relevant keywords, respond exactly with 'None'.
- Do not include any additional text or explanation.

**Keywords**:
"""
)

SIMILAR_KEYWORDS_PROMPT = Template(
    """
You are tasked with finding additional keywords that are semantically similar to the provided keywords, using only the **Context** below.

---

**Provided Keywords**: $rule

---

**Context**:
$chunks

---

**Instructions**:

- Provide the similar keywords as a JSON array of strings.
- Only include words that are present in the context and are semantically related to the provided keywords.
- If you cannot find any similar keywords in the context, respond exactly with 'None'.
- Do not include any additional text or explanation.

**Similar Keywords**:
"""
)

DECOMPOSE_QUERY_PROMPT = Template(
    """
You are tasked with decomposing the following question into simpler, relevant sub-questions that capture different aspects of the original question.

---

**Original Question**: $query

---

**Instructions**:

- Provide up to 3 sub-questions as a JSON array of strings.
- If the question is already simple or cannot be decomposed, respond exactly with 'None'.
- Do not include any additional text or explanation.

**Sub-Questions**:
"""
)

SCHEMA_PROMPT = Template(
    """
Given the information about columns in a knowledge table, generate a schema that includes relationships between the columns if relevant.

---

**Documents**: $documents

**Columns**: $columns

**Available Column Names**: $entity_types

---

**Instructions**:

- Use **only** the exact column names provided in `$entity_types`.
- For each relationship, create an object with `"head"`, `"relation"`, and `"tail"` fields.
- The `"head"` and `"tail"` must be one of the provided column names.
- Create meaningful `"relation"` names based on the column information and questions.
- Do not use any names not in the provided column list.
- If you cannot generate any meaningful relationships, respond exactly with `"None"`.
- Do not include any additional text or explanation.

**Schema Relationships**:
"""
)
