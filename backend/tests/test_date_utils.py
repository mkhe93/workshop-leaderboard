"""Unit tests for date utility functions."""

import pytest
from datetime import datetime, timedelta, timezone
from src.utils.date_utils import (
    parse_date_range,
    format_date_for_api,
    format_date_for_api_end,
)


class TestParseDateRange:
    """Tests for parse_date_range function."""

    def test_valid_date_parsing_both_dates(self):
        """Test parsing valid start and end dates."""
        start_dt, end_dt = parse_date_range("2024-01-15", "2024-01-20")

        assert start_dt.year == 2024
        assert start_dt.month == 1
        assert start_dt.day == 15
        assert start_dt.hour == 0
        assert start_dt.minute == 0
        assert start_dt.second == 0
        assert start_dt.tzinfo == timezone.utc

        assert end_dt.year == 2024
        assert end_dt.month == 1
        assert end_dt.day == 20
        assert end_dt.hour == 23
        assert end_dt.minute == 59
        assert end_dt.second == 59
        assert end_dt.tzinfo == timezone.utc

    def test_valid_date_parsing_various_formats(self):
        """Test parsing dates with different valid YYYY-MM-DD formats."""
        # Test with single digit month and day
        start_dt, end_dt = parse_date_range("2024-01-01", "2024-12-31")
        assert start_dt.month == 1
        assert start_dt.day == 1
        assert end_dt.month == 12
        assert end_dt.day == 31

        # Test with leap year date
        start_dt, end_dt = parse_date_range("2024-02-29", "2024-03-01")
        assert start_dt.month == 2
        assert start_dt.day == 29
        assert end_dt.month == 3
        assert end_dt.day == 1

    def test_default_date_range_both_none(self):
        """Test default date range when both dates are None (last 24 hours)."""
        start_dt, end_dt = parse_date_range(None, None)

        # end_dt should be approximately now
        now = datetime.now(timezone.utc)
        time_diff = abs((end_dt - now).total_seconds())
        assert time_diff < 2  # Within 2 seconds of now

        # start_dt should be 24 hours before end_dt
        expected_start = end_dt - timedelta(days=1)
        assert start_dt == expected_start

        # Both should have UTC timezone
        assert start_dt.tzinfo == timezone.utc
        assert end_dt.tzinfo == timezone.utc

    def test_default_start_date_only(self):
        """Test default start date when only end_date is provided."""
        end_date = "2024-01-20"
        start_dt, end_dt = parse_date_range(None, end_date)

        # end_dt should be the provided date at 23:59:59
        assert end_dt.year == 2024
        assert end_dt.month == 1
        assert end_dt.day == 20
        assert end_dt.hour == 23
        assert end_dt.minute == 59
        assert end_dt.second == 59

        # start_dt should be 24 hours before end_dt
        expected_start = end_dt - timedelta(days=1)
        assert start_dt == expected_start
        assert start_dt.day == 19

    def test_default_end_date_only(self):
        """Test default end date when only start_date is provided."""
        start_date = "2024-01-15"
        start_dt, end_dt = parse_date_range(start_date, None)

        # start_dt should be the provided date at 00:00:00
        assert start_dt.year == 2024
        assert start_dt.month == 1
        assert start_dt.day == 15
        assert start_dt.hour == 0
        assert start_dt.minute == 0
        assert start_dt.second == 0

        # end_dt should be approximately now
        now = datetime.now(timezone.utc)
        time_diff = abs((end_dt - now).total_seconds())
        assert time_diff < 2  # Within 2 seconds of now

    def test_invalid_start_date_format(self):
        """Test that invalid start_date format raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_date_range("2024/01/15", "2024-01-20")

        assert "Invalid start_date format" in str(exc_info.value)
        assert "Expected YYYY-MM-DD" in str(exc_info.value)

    def test_invalid_end_date_format(self):
        """Test that invalid end_date format raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_date_range("2024-01-15", "2024/01/20")

        assert "Invalid end_date format" in str(exc_info.value)
        assert "Expected YYYY-MM-DD" in str(exc_info.value)

    def test_invalid_date_format_wrong_separator(self):
        """Test various invalid date formats with wrong separators."""
        invalid_formats = [
            "2024.01.15",  # Dots instead of dashes
            "2024_01_15",  # Underscores
            "20240115",  # No separators
        ]

        for invalid_date in invalid_formats:
            with pytest.raises(ValueError):
                parse_date_range(invalid_date, "2024-01-20")

    def test_accepts_dates_without_leading_zeros(self):
        """Test that dates without leading zeros are accepted (Python strptime behavior)."""
        # Python's strptime is lenient and accepts these formats
        start_dt, end_dt = parse_date_range("2024-1-5", "2024-12-25")

        assert start_dt.month == 1
        assert start_dt.day == 5
        assert end_dt.month == 12
        assert end_dt.day == 25

    def test_invalid_date_values(self):
        """Test that invalid date values raise ValueError."""
        invalid_dates = [
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
            "2024-02-30",  # Invalid day for February
            "2023-02-29",  # Not a leap year
            "2024-00-15",  # Month zero
            "2024-01-00",  # Day zero
        ]

        for invalid_date in invalid_dates:
            with pytest.raises(ValueError):
                parse_date_range(invalid_date, "2024-01-20")

    def test_non_date_strings(self):
        """Test that non-date strings raise ValueError."""
        invalid_inputs = [
            "not-a-date",
            "2024-Jan-15",
            "15-01-2024",  # Wrong order
            "",
            "abc-def-ghi",
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError):
                parse_date_range(invalid_input, "2024-01-20")


class TestFormatDateForApi:
    """Tests for format_date_for_api function."""

    def test_format_date_for_api_basic(self):
        """Test basic date formatting for API start date."""
        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        formatted = format_date_for_api(dt)

        assert formatted == "2024.01.15"

    def test_format_date_for_api_single_digit_month_day(self):
        """Test formatting with single digit month and day."""
        dt = datetime(2024, 3, 5, 0, 0, 0, tzinfo=timezone.utc)
        formatted = format_date_for_api(dt)

        assert formatted == "2024.03.05"

    def test_format_date_for_api_december(self):
        """Test formatting with December (month 12)."""
        dt = datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        formatted = format_date_for_api(dt)

        assert formatted == "2024.12.31"

    def test_format_date_for_api_ignores_time(self):
        """Test that time components are ignored in formatting."""
        dt1 = datetime(2024, 1, 15, 0, 0, 0, tzinfo=timezone.utc)
        dt2 = datetime(2024, 1, 15, 23, 59, 59, tzinfo=timezone.utc)

        assert format_date_for_api(dt1) == format_date_for_api(dt2)
        assert format_date_for_api(dt1) == "2024.01.15"


class TestFormatDateForApiEnd:
    """Tests for format_date_for_api_end function."""

    def test_format_date_for_api_end_basic(self):
        """Test basic ISO format for API end date."""
        dt = datetime(2024, 1, 20, 23, 59, 59, tzinfo=timezone.utc)
        formatted = format_date_for_api_end(dt)

        assert formatted == "2024-01-20T23:59:59+00:00"

    def test_format_date_for_api_end_includes_time(self):
        """Test that ISO format includes time components."""
        dt = datetime(2024, 1, 20, 15, 30, 45, tzinfo=timezone.utc)
        formatted = format_date_for_api_end(dt)

        assert "T15:30:45" in formatted
        assert formatted.startswith("2024-01-20")

    def test_format_date_for_api_end_includes_timezone(self):
        """Test that ISO format includes timezone information."""
        dt = datetime(2024, 1, 20, 23, 59, 59, tzinfo=timezone.utc)
        formatted = format_date_for_api_end(dt)

        assert "+00:00" in formatted or "Z" in formatted.replace("+00:00", "Z")

    def test_format_date_for_api_end_midnight(self):
        """Test ISO format for midnight."""
        dt = datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc)
        formatted = format_date_for_api_end(dt)

        assert formatted == "2024-01-20T00:00:00+00:00"


class TestDateUtilsIntegration:
    """Integration tests for date utility functions working together."""

    def test_parse_and_format_roundtrip(self):
        """Test parsing dates and formatting them for API."""
        start_dt, end_dt = parse_date_range("2024-01-15", "2024-01-20")

        start_formatted = format_date_for_api(start_dt)
        end_formatted = format_date_for_api_end(end_dt)

        assert start_formatted == "2024.01.15"
        assert end_formatted == "2024-01-20T23:59:59+00:00"

    def test_default_range_formatting(self):
        """Test formatting default date range (last 24 hours)."""
        start_dt, end_dt = parse_date_range(None, None)

        start_formatted = format_date_for_api(start_dt)
        end_formatted = format_date_for_api_end(end_dt)

        # Should produce valid formatted strings
        assert len(start_formatted) == 10  # YYYY.MM.DD
        assert "." in start_formatted
        assert "T" in end_formatted  # ISO format includes T
        assert ":" in end_formatted  # ISO format includes time
