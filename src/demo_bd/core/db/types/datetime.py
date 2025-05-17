"""Custom SQLAlchemy type for timezone-aware UTC DateTime columns."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator

if TYPE_CHECKING:
    from sqlalchemy.engine import Dialect


class DateTimeUTC(TypeDecorator[datetime.datetime]):
    """Timezone Aware DateTime.

    Ensure UTC is stored in the database and that TZ aware dates are returned for all dialects.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    @property
    def python_type(self) -> type[datetime.datetime]:
        """Return the Python type handled by this custom type (datetime.datetime)."""
        return datetime.datetime

    def process_bind_param(
        self, value: datetime.datetime | None, dialect: Dialect
    ) -> datetime.datetime | None:
        """Process a value before sending to the database, ensuring it is timezone-aware and in UTC."""
        if value is None:
            return value
        if not value.tzinfo:
            msg = "tzinfo is required"
            raise TypeError(msg)
        return value.astimezone(datetime.UTC)

    def process_result_value(
        self, value: datetime.datetime | None, dialect: Dialect
    ) -> datetime.datetime | None:
        """Process a value after retrieving from the database, ensuring it is timezone-aware and in UTC."""
        if value is None:
            return value
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.UTC)
        return value
