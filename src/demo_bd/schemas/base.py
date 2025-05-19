"""Base schema definitions for the project."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from demo_bd.utils.formatters.datetime_formatter import fmt_datetime_into_iso8601_format
from demo_bd.utils.formatters.dict_formatter import fmt_dict_key_to_camel_case


class BaseSchemaModel(BaseModel):
    """Base schema model for all Pydantic schemas.

    Inherits from Pydantic's BaseModel and provides common configuration
    for serialization, validation, and field aliasing.
    """

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        populate_by_name=True,
        json_encoders={datetime: fmt_datetime_into_iso8601_format},
        alias_generator=fmt_dict_key_to_camel_case,
    )
