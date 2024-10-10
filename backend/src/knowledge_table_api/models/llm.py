"""Pydantic models for validating responses from the LLM API."""

import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseResponseModel(BaseModel):
    """Base class for response models with common validation logic."""

    @classmethod
    def validate_none(cls, v: Any) -> Optional[Any]:
        """Validate if the value is None or "none"."""
        if v is None or (isinstance(v, str) and v.lower() == "none"):
            return None
        return v


class BoolResponseModel(BaseResponseModel):
    """Pydantic model for validating boolean responses."""

    answer: Optional[bool] = Field(
        description="The boolean answer to the query"
    )

    @validator("answer", pre=True)
    def validate_bool(cls, v: Union[str, bool, None]) -> Optional[bool]:
        """Validate if the value is a boolean or None."""
        v = cls.validate_none(v)
        if v is None:
            return None
        if isinstance(v, str):
            if v.lower() == "true":
                return True
            elif v.lower() == "false":
                return False
        elif isinstance(v, bool):
            return v
        raise ValueError("Must be a boolean value or None")


class IntResponseModel(BaseResponseModel):
    """Pydantic model for validating integer responses."""

    answer: Optional[int] = Field(
        description="The integer answer to the query"
    )

    @validator("answer", pre=True)
    def validate_int(cls, v: Union[str, int, None]) -> Optional[int]:
        """Validate if the value is an integer or None."""
        v = cls.validate_none(v)
        if v is None:
            return None
        try:
            return int(v)
        except ValueError:
            raise ValueError("Must be an integer value or None")


class ArrayResponseModel(BaseResponseModel):
    """Base class for array response models."""

    @classmethod
    def validate_array(
        cls, v: Any, max_length: Optional[int] = None
    ) -> Optional[List[Any]]:
        """Validate if the value is a list or None."""
        v = cls.validate_none(v)
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("Must be a list or None")
        if max_length and len(v) > max_length:
            logger.error(f"Length of response is greater than {max_length}")
            return v[:max_length]
        return v


class IntArrayResponseModel(ArrayResponseModel):
    """Pydantic model for validating integer array responses."""

    answer: Optional[List[int]] = Field(
        description="The list of integer answers to the query"
    )

    @validator("answer", pre=True)
    def validate_int_array(
        cls, v: Any, values: Dict[str, Any], **kwargs: Any
    ) -> Optional[List[int]]:
        """Validate if the value is an integer array or None."""
        int_rule = kwargs.get("int_rule")
        max_length = int_rule.length if int_rule else None
        return cls.validate_array(v, max_length)


class StrArrayResponseModel(ArrayResponseModel):
    """Pydantic model for validating string array responses."""

    answer: Optional[List[str]] = Field(
        description="The list of string answers to the query"
    )

    @validator("answer", pre=True)
    def validate_str_array(
        cls, v: Any, values: Dict[str, Any], **kwargs: Any
    ) -> Optional[List[str]]:
        """Validate if the value is a string array or None."""
        str_rule = kwargs.get("str_rule")
        int_rule = kwargs.get("int_rule")
        max_length = int_rule.length if int_rule else None
        v = cls.validate_array(v, max_length)
        if v is None:
            return None
        if str_rule and str_rule.type == "must_return" and str_rule.options:
            v = [i for i in v if i in str_rule.options]
            if not v or v == ["not found"]:
                return []
        return v


class StrResponseModel(BaseResponseModel):
    """Pydantic model for validating string responses."""

    answer: Optional[str] = Field(description="The string answer to the query")

    @validator("answer", pre=True)
    def validate_str(
        cls, v: Optional[str], values: Dict[str, Any], **kwargs: Any
    ) -> Optional[str]:
        """Validate if the value is a string or None."""
        v = cls.validate_none(v)
        if v is None:
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


class KeywordsResponseModel(ArrayResponseModel):
    """Pydantic model for validating keyword responses."""

    keywords: Optional[List[str]] = Field(
        description="The extracted keywords from the query"
    )

    @validator("keywords", pre=True)
    def validate_keywords(cls, v: Any) -> Optional[List[str]]:
        """Validate if the value is a string array or None."""
        return cls.validate_array(v)


class SubQueriesResponseModel(ArrayResponseModel):
    """Pydantic model for validating sub-query responses."""

    sub_queries: Optional[List[str]] = Field(
        description="The decomposed sub-queries"
    )

    @validator("sub_queries", pre=True)
    def validate_sub_queries(cls, v: Any) -> Optional[List[str]]:
        """Validate if the value is a string array or None."""
        return cls.validate_array(v)


class SchemaRelationship(BaseModel):
    """Pydantic model for a schema relationship."""

    head: str = Field(description="The head entity of the relationship")
    relation: str = Field(
        description="The relation between the head and tail entities"
    )
    tail: str = Field(description="The tail entity of the relationship")


class SchemaResponseModel(ArrayResponseModel):
    """Pydantic model for validating schema responses."""

    relationships: Optional[List[SchemaRelationship]] = Field(
        description="The relationships in the schema"
    )

    @validator("relationships", pre=True)
    def validate_relationships(
        cls, v: Any
    ) -> Optional[List[SchemaRelationship]]:
        """Validate if the value is a schema relationship array or None."""
        return cls.validate_array(v)
