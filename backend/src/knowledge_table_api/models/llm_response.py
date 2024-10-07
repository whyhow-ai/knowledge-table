"""Pydantic models for validating responses from the LLM API."""

import logging

from pydantic import BaseModel

from knowledge_table_api.models.query import Rule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BoolResponseModel(BaseModel):
    """Pydantic model for validating boolean responses."""

    @staticmethod
    def validate_response(value: str) -> bool | None:
        """Validate the response to ensure it is a boolean value."""
        allowed_values = {"True", "False"}

        # Ensure the input value is one of the allowed boolean-like strings
        if value not in allowed_values:
            return None

        # Convert the string to a boolean and return
        return value == "True"


class IntResponseModel(BaseModel):
    """Pydantic model for validating integer responses."""

    @staticmethod
    def validate_response(value: int) -> int:
        """Validate the response to ensure it is an integer."""
        return value


class IntArrayResponseModel(BaseModel):
    """Pydantic model for validating integer array responses."""

    @staticmethod
    def validate_response(
        values: list[int], int_rule: Rule | None = None
    ) -> list[int] | None:
        """Validate the response to ensure it is a list of integers and of the right length."""
        int_values = [int(i) for i in values if isinstance(i, (int, str))]

        # Apply int_rule if provided
        if (
            int_rule
            and int_rule.length is not None
            and len(int_values) > int_rule.length
        ):
            logger.error(
                f"Length of response is greater than {int_rule.length}"
            )
            int_values = int_values[: int_rule.length]

        return int_values or None


class StrArrayResponseModel(BaseModel):
    """Pydantic model for validating string array responses."""

    @staticmethod
    def validate_response(
        values: list[str],
        str_rule: Rule | None = None,
        int_rule: Rule | None = None,
    ) -> list[str] | None:
        """Validate the response to ensure it is a list of strings of the correct length and containing the allowed values."""
        # Ensure all elements are strings
        values = [str(i) for i in values]

        # Apply str_rule if provided and filter values
        if str_rule and str_rule.type == "must_return" and str_rule.options:
            values = [i for i in values if i in str_rule.options]
            if not values or values == ["not found"]:
                return None

        # Apply int_rule if provided and truncate the list if necessary
        if (
            int_rule
            and int_rule.length is not None
            and len(values) > int_rule.length
        ):
            logger.error(
                f"Length of response is greater than {int_rule.length}"
            )
            values = values[: int_rule.length]

        return values or None


class StrResponseModel(BaseModel):
    """Pydantic model for validating string responses."""

    @staticmethod
    def validate_response(
        value: str, str_rule: Rule | None = None
    ) -> str | None:
        """Validate the response to ensure it is a string and in the allowed values."""
        # Apply str_rule if provided and check if value is in the allowed options
        if (
            str_rule
            and str_rule.type == "must_return"
            and str_rule.options is not None
            and value not in str_rule.options
        ):
            logger.error(f"Value is not in the allowed options: {value}")
            return None

        return value
