from datetime import datetime, timezone


def is_before_now(iso_date: str):
    """
    Returns True if the given ISO 8601 date string is before the current UTC time.
    The input must include timezone info.
    Raises AssertionError if the parsed date is not timezone-aware.
    """
    date = _parse_date(iso_date)
    now = _get_now()

    return date < now


def is_after_now(iso_date: str):
    return not is_before_now(iso_date)


def _get_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_date(date_string: str) -> datetime:
    dt = datetime.fromisoformat(date_string)
    assert dt.tzinfo is not None, "ISO datetime must include timezone"
    return dt
