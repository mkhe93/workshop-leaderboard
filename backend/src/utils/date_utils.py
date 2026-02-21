"""Date parsing and formatting utilities for API endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Tuple


def parse_date_range(
    start_date: str | None, end_date: str | None
) -> Tuple[datetime, datetime]:
    """
    Parse and validate date range parameters.

    Args:
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format

    Returns:
        Tuple of (start_datetime, end_datetime) with proper timezone and time components

    Raises:
        ValueError: If date format is invalid
    """
    # Default to last 24 hours if not provided
    if end_date is None:
        end_dt = datetime.now(timezone.utc)
    else:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            )
        except ValueError as e:
            raise ValueError(f"Invalid end_date format. Expected YYYY-MM-DD: {e}")

    if start_date is None:
        start_dt = end_dt - timedelta(days=1)
    else:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(
                hour=0, minute=0, second=0, tzinfo=timezone.utc
            )
        except ValueError as e:
            raise ValueError(f"Invalid start_date format. Expected YYYY-MM-DD: {e}")

    return start_dt, end_dt


def format_date_for_api(dt: datetime) -> str:
    """
    Format datetime for LiteLLM API start date.

    Args:
        dt: Datetime object to format

    Returns:
        Date string in YYYY.MM.DD format
    """
    return dt.strftime("%Y.%m.%d")


def format_date_for_api_end(dt: datetime) -> str:
    """
    Format datetime for LiteLLM API end date.

    Args:
        dt: Datetime object to format

    Returns:
        Date string in ISO format
    """
    return dt.isoformat()
