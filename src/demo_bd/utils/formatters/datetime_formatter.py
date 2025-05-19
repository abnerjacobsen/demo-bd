"""Datetime formatting utilities using Pendulum."""

import datetime

import pendulum

_TARGET_ISO8601_DATETIME_FORMAT = "YYYY-MM-DDTHH:mm:ss.SSSSSS[Z]"


def fmt_datetime_into_iso8601_format(
    date_time_obj: pendulum.DateTime | datetime.datetime,
) -> str:
    """
    Convert a datetime-like object to a full ISO 8601 string in UTC.

    The output format is precisely "YYYY-MM-DDTHH:mm:ss.SSSSSSZ", ensuring
    that microseconds are always present (zero-padded to 6 digits if necessary)
    and 'T' separates the date and time components, as per ISO 8601.

    This function intelligently handles both `pendulum.DateTime` and standard
    `datetime.datetime` objects:
    - If the input is a `pendulum.DateTime` instance, it's converted to the
      UTC timezone.
    - If the input is a naive `datetime.datetime` instance, it's explicitly
      interpreted as representing a UTC timestamp.
    - If the input is an aware `datetime.datetime` instance, it's converted
      to the UTC timezone.

    Args:
        date_time_obj: The datetime object to format. Can be either a
                       `pendulum.DateTime` or a standard `datetime.datetime`.

    Returns
    -------
        A string representing the datetime in the format
        "YYYY-MM-DDTHH:mm:ss.SSSSSSZ" (e.g., "2023-10-27T10:30:00.123456Z"
        or "2023-10-27T10:30:00.000000Z").

    Raises
    ------
        TypeError: If the input object is not a supported datetime type.
    """
    pdt_utc: pendulum.DateTime

    if isinstance(date_time_obj, pendulum.DateTime):
        pdt_utc = date_time_obj.in_timezone(pendulum.UTC)
    elif isinstance(date_time_obj, datetime.datetime):
        if date_time_obj.tzinfo is None or date_time_obj.tzinfo.utcoffset(date_time_obj) is None:
            pdt_utc = pendulum.datetime(
                date_time_obj.year,
                date_time_obj.month,
                date_time_obj.day,
                date_time_obj.hour,
                date_time_obj.minute,
                date_time_obj.second,
                date_time_obj.microsecond,
                tz=pendulum.UTC,
            )
        else:
            pdt_utc = pendulum.instance(date_time_obj).in_timezone(pendulum.UTC)
    else:
        raise TypeError(
            "Input must be a pendulum.DateTime or datetime.datetime object. "
            f"Received type: {type(date_time_obj).__name__}"
        )

    return pdt_utc.format(_TARGET_ISO8601_DATETIME_FORMAT)
