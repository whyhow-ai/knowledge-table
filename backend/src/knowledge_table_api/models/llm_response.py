"""Pydantic models for validating responses from the LLM API."""

import logging
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from knowledge_table_api.models.query import Rule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BoolResponseModel(BaseModel):
    """Pydantic model for validating boolean responses."""

    answer: bool = Field(..., description="The boolean answer to the query")

    @validator('answer', pre=True)
    def validate_bool(cls, v):
        if isinstance(v, str):
            if v.lower() == 'true':
                return True
            elif v.lower() == 'false':
                return False
        elif isinstance(v, bool):
            return v
        raise ValueError('Must be a boolean value')

class IntResponseModel(BaseModel):
    """Pydantic model for validating integer responses."""

    answer: int = Field(..., description="The integer answer to the query")

class IntArrayResponseModel(BaseModel):
    """Pydantic model for validating integer array responses."""

    answer: List[int] = Field(..., description="The list of integer answers to the query")

    @validator('answer')
    def validate_int_array(cls, v, values, **kwargs):
        int_rule = kwargs.get('int_rule')
        if int_rule and int_rule.length is not None and len(v) > int_rule.length:
            logger.error(f"Length of response is greater than {int_rule.length}")
            return v[:int_rule.length]
        return v

class StrArrayResponseModel(BaseModel):
    """Pydantic model for validating string array responses."""

    answer: List[str] = Field(..., description="The list of string answers to the query")

    @validator('answer')
    def validate_str_array(cls, v, values, **kwargs):
        str_rule = kwargs.get('str_rule')
        int_rule = kwargs.get('int_rule')

        if str_rule and str_rule.type == "must_return" and str_rule.options:
            v = [i for i in v if i in str_rule.options]
            if not v or v == ["not found"]:
                return None

        if int_rule and int_rule.length is not None and len(v) > int_rule.length:
            logger.error(f"Length of response is greater than {int_rule.length}")
            return v[:int_rule.length]

        return v

class StrResponseModel(BaseModel):
    """Pydantic model for validating string responses."""

    answer: str = Field(..., description="The string answer to the query")

    @validator('answer')
    def validate_str(cls, v, values, **kwargs):
        str_rule = kwargs.get('str_rule')
        if (
            str_rule
            and str_rule.type == "must_return"
            and str_rule.options is not None
            and v not in str_rule.options
        ):
            logger.error(f"Value is not in the allowed options: {v}")
            return None
        return v

class KeywordsResponseModel(BaseModel):
    """Pydantic model for validating keyword responses."""

    keywords: List[str] = Field(..., description="The extracted keywords from the query")

class SubQueriesResponseModel(BaseModel):
    """Pydantic model for validating sub-query responses."""

    sub_queries: List[str] = Field(..., description="The decomposed sub-queries")

class SchemaRelationship(BaseModel):
    """Pydantic model for a schema relationship."""

    head: str = Field(..., description="The head entity of the relationship")
    relation: str = Field(..., description="The relation between the head and tail entities")
    tail: str = Field(..., description="The tail entity of the relationship")

class SchemaResponseModel(BaseModel):
    """Pydantic model for validating schema responses."""

    relationships: List[SchemaRelationship] = Field(..., description="The relationships in the schema")