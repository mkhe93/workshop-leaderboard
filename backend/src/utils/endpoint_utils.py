"""Utilities for abstracting common endpoint patterns."""

from typing import TypeVar, Protocol, Optional
from fastapi import HTTPException

from src.api.models import DateRangeParams
from src.utils.date_utils import (
    parse_date_range,
    format_date_for_api,
    format_date_for_api_end,
)

T = TypeVar("T")


class ServiceMethod(Protocol[T]):
    """Protocol for service methods that accept start_date and end_date."""

    def __call__(self, start_date: str, end_date: str) -> T: ...


def execute_date_range_endpoint(
    start_date: Optional[str],
    end_date: Optional[str],
    service_method: ServiceMethod[T],
) -> T:
    """
    Abstract common pattern for endpoints that accept date ranges and call a service method.

    Args:
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
        service_method: Service method to call with (start_date, end_date) parameters

    Returns:
        Result from service_method

    Raises:
        HTTPException: 400 for validation errors, 502 for service errors, 500 for unexpected errors
    """
    # Validate date parameters
    try:
        params = DateRangeParams(start_date=start_date, end_date=end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Parse date range using centralized utility
    try:
        start_dt, end_dt = parse_date_range(params.start_date, params.end_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Execute service method with formatted dates
    try:
        return service_method(
            start_date=format_date_for_api(start_dt),
            end_date=format_date_for_api_end(end_dt),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
