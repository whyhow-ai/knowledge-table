"""Pydantic models for validating responses from the LLM API."""

import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BoolResponseModel(BaseModel):
    """Pydantic model for validating boolean responses."""

    answer: bool | None = Field(
        ..., description="The boolean answer to the query"
    )

    @validator("answer", pre=True)
    def validate_bool(cls, v: str | bool | None) -> bool | None:
        """Validate the boolean response."""
        if v is None or (isinstance(v, str) and v.lower() == "none"):
            return None
        if isinstance(v, str):
            if v.lower() == "true":
                return True
            elif v.lower() == "false":
                return False
        elif isinstance(v, bool):
            return v
        raise ValueError("Must be a boolean value or None")


class IntResponseModel(BaseModel):
    """Pydantic model for validating integer responses."""

    answer: int | None = Field(
        ..., description="The integer answer to the query"
    )

    @validator("answer", pre=True)
    def validate_int(cls, v: str | int | None) -> int | None:
        """Validate the integer response."""
        if v is None or (isinstance(v, str) and v.lower() == "none"):
            return None
        try:
            return int(v)
        except ValueError:
            raise ValueError("Must be an integer value or None")


class IntArrayResponseModel(BaseModel):
    """Pydantic model for validating integer array responses."""

    answer: Optional[List[int]] = Field(
        ..., description="The list of integer answers to the query"
    )

    @validator("answer", pre=True)
    def validate_int_array(
        cls,
        v: Union[List[int], str, None],
        values: Dict[str, Any],
        **kwargs: Any,
    ) -> Optional[List[int]]:
        """Validate the integer array response."""
        if v is None or (isinstance(v, str) and v.lower() == "none"):
            return None
        if isinstance(v, list):
            int_rule = kwargs.get("int_rule")
            if (
                int_rule
                and int_rule.length is not None
                and len(v) > int_rule.length
            ):
                logger.error(
                    f"Length of response is greater than {int_rule.length}"
                )
                return v[: int_rule.length]
            return v
        raise ValueError("Must be a list of integers or None")


class StrArrayResponseModel(BaseModel):
    """Pydantic model for validating string array responses."""

    answer: Optional[List[str]] = Field(
        ..., description="The list of string answers to the query"
    )

    @validator("answer", pre=True)
    def validate_str_array(
        cls,
        v: Union[List[str], str, None],
        values: Dict[str, Any],
        **kwargs: Any,
    ) -> Optional[List[str]]:
        """Validate the string array response."""
        if v is None or (isinstance(v, str) and v.lower() == "none"):
            return None
        if isinstance(v, list):
            str_rule = kwargs.get("str_rule")
            int_rule = kwargs.get("int_rule")

            if (
                str_rule
                and str_rule.type == "must_return"
                and str_rule.options
            ):
                v = [i for i in v if i in str_rule.options]
                if not v or v == ["not found"]:
                    return []

            if (
                int_rule
                and int_rule.length is not None
                and len(v) > int_rule.length
            ):
                logger.error(
                    f"Length of response is greater than {int_rule.length}"
                )
                return v[: int_rule.length]

            return v
        raise ValueError("Must be a list of strings or None")


class StrResponseModel(BaseModel):
    """Pydantic model for validating string responses."""

    answer: str | None = Field(
        ..., description="The string answer to the query"
    )

    @validator("answer", pre=True)
    def validate_str(
        cls, v: str | None, values: Dict[str, Any], **kwargs: Any
    ) -> str | None:
        """Validate the string response."""
        if v is None or (isinstance(v, str) and v.lower() == "none"):
            return None
        str_rule = kwargs.get("str_rule")
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

    keywords: Optional[List[str]] = Field(
        ..., description="The extracted keywords from the query"
    )

    @validator("keywords", pre=True)
    def validate_keywords(
        cls, v: Union[List[str], str, None]
    ) -> Optional[List[str]]:
        """Validate the keywords response."""
        if v is None or (isinstance(v, str) and v.lower() == "none"):
            return None
        if isinstance(v, list):
            return v
        raise ValueError("Must be a list of strings or None")


class SubQueriesResponseModel(BaseModel):
    """Pydantic model for validating sub-query responses."""

    sub_queries: Optional[List[str]] = Field(
        ..., description="The decomposed sub-queries"
    )

    @validator("sub_queries", pre=True)
    def validate_sub_queries(
        cls, v: Union[List[str], str, None]
    ) -> Optional[List[str]]:
        """Validate the sub-queries response."""
        if v is None or (isinstance(v, str) and v.lower() == "none"):
            return None
        if isinstance(v, list):
            return v
        raise ValueError("Must be a list of strings or None")


class SchemaRelationship(BaseModel):
    """Pydantic model for a schema relationship."""

    head: str = Field(..., description="The head entity of the relationship")
    relation: str = Field(
        ..., description="The relation between the head and tail entities"
    )
    tail: str = Field(..., description="The tail entity of the relationship")


class SchemaResponseModel(BaseModel):
    """Pydantic model for validating schema responses."""

    relationships: Optional[List[SchemaRelationship]] = Field(
        ..., description="The relationships in the schema"
    )

    @validator("relationships", pre=True)
    def validate_relationships(
        cls, v: Union[List[SchemaRelationship], str, None]
    ) -> Optional[List[SchemaRelationship]]:
        """Validate the schema relationships response."""
        if v is None or (isinstance(v, str) and v.lower() == "none"):
            return None
        if isinstance(v, list):
            return v
        raise ValueError("Must be a list of SchemaRelationship or None")
