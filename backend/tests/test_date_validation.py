"""Tests for date parameter validation."""

import pytest
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError
from src.api.models import DateRangeParams


def test_valid_date_format():
    """Test that valid YYYY-MM-DD dates are accepted."""
    params = DateRangeParams(start_date="2024-01-15", end_date="2024-01-20")
    assert params.start_date == "2024-01-15"
    assert params.end_date == "2024-01-20"


def test_invalid_date_format():
    """Test that invalid date formats are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DateRangeParams(start_date="2024/01/15", end_date="2024-01-20")
    assert "Date must be in YYYY-MM-DD format" in str(exc_info.value)


def test_future_start_date_rejected():
    """Test that future start dates are rejected."""
    future_date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    with pytest.raises(ValidationError) as exc_info:
        DateRangeParams(start_date=future_date, end_date="2024-01-20")
    assert "start_date cannot be in the future" in str(exc_info.value)


def test_future_end_date_rejected():
    """Test that future end dates are rejected."""
    future_date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    with pytest.raises(ValidationError) as exc_info:
        DateRangeParams(start_date="2024-01-15", end_date=future_date)
    assert "end_date cannot be in the future" in str(exc_info.value)


def test_end_date_before_start_date_rejected():
    """Test that end_date before start_date is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DateRangeParams(start_date="2024-01-20", end_date="2024-01-15")
    assert "end_date must not be before start_date" in str(exc_info.value)


def test_none_dates_accepted():
    """Test that None values are accepted for optional dates."""
    params = DateRangeParams(start_date=None, end_date=None)
    assert params.start_date is None
    assert params.end_date is None


def test_today_date_accepted():
    """Test that today's date is accepted."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    params = DateRangeParams(start_date=today, end_date=today)
    assert params.start_date == today
    assert params.end_date == today


def test_property_invalid_date_formats_rejected(start_date, end_date):
    """
    Property 1: Date format validation

    For any request with date parameters, if the date format is not YYYY-MM-DD,
    then the backend should return an HTTP 400 error with a descriptive message.

    Validates: Requirements 2.3
    """
    # Skip if both dates are None (valid case)
    if start_date is None and end_date is None:
        return

    # At least one date is invalid format
    with pytest.raises(ValidationError) as exc_info:
        DateRangeParams(start_date=start_date, end_date=end_date)

    # Verify error message mentions format requirement
    assert "Date must be in YYYY-MM-DD format" in str(exc_info.value)


def _is_valid_date_format(date_str: str) -> bool:
    """Helper to check if a string matches YYYY-MM-DD format."""
    if not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def test_property_date_range_validation(start_date, end_date):
    """
    Property 2: Date range validation

    For any request where start_date is after end_date, the backend should
    return an HTTP 400 error with a descriptive message.

    Validates: Requirements 2.4
    """
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    if start_date > end_date:
        # Invalid range: start after end
        with pytest.raises(ValidationError) as exc_info:
            DateRangeParams(start_date=start_str, end_date=end_str)

        # Verify error message mentions the range requirement
        assert "end_date must not be before start_date" in str(exc_info.value)
    else:
        # Valid range: start <= end
        params = DateRangeParams(start_date=start_str, end_date=end_str)
        assert params.start_date == start_str
        assert params.end_date == end_str


def test_property_future_date_rejection(days_in_future, which_date):
    """
    Property 3: Future date rejection

    For any date parameter that represents a future date, the backend should
    return an HTTP 400 error.

    Validates: Requirements 1.2, 1.4
    """
    today = datetime.now(timezone.utc).date()
    future_date = (
        datetime.now(timezone.utc) + timedelta(days=days_in_future)
    ).strftime("%Y-%m-%d")
    valid_past_date = (today - timedelta(days=10)).strftime("%Y-%m-%d")

    if which_date == "start":
        # Future start_date should be rejected
        with pytest.raises(ValidationError) as exc_info:
            DateRangeParams(start_date=future_date, end_date=valid_past_date)
        assert "start_date cannot be in the future" in str(exc_info.value)

    elif which_date == "end":
        # Future end_date should be rejected
        with pytest.raises(ValidationError) as exc_info:
            DateRangeParams(start_date=valid_past_date, end_date=future_date)
        assert "end_date cannot be in the future" in str(exc_info.value)

    else:  # both
        # Both dates in future should be rejected
        with pytest.raises(ValidationError) as exc_info:
            DateRangeParams(start_date=future_date, end_date=future_date)
        # Either start or end validation will catch it
        error_msg = str(exc_info.value)
        assert (
            "start_date cannot be in the future" in error_msg
            or "end_date cannot be in the future" in error_msg
        )
