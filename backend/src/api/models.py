from typing import List, Optional
from pydantic import BaseModel, field_validator
from datetime import datetime, timezone


class ModelUsage(BaseModel):
    """Token usage for a specific model."""

    model_name: str
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int


class ApiKeyBreakdown(BaseModel):
    """Breakdown of model usage for a specific API key."""

    api_key: str
    key_alias: Optional[str] = None  # Human-readable alias like "DevBoost (Internal)"
    models: List[ModelUsage]


class TeamBreakdown(BaseModel):
    """Complete breakdown structure for a team."""

    api_keys: List[ApiKeyBreakdown]


class TeamOut(BaseModel):
    name: str
    tokens: int
    breakdown: Optional[TeamBreakdown] = None


class TeamsOut(BaseModel):
    teams: List[TeamOut]


class DailyTeamTokens(BaseModel):
    """Token count and request metrics for a team on a specific day."""

    name: str
    tokens: int
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0


class DailyTimeSeriesPoint(BaseModel):
    """Time-series data point for a single day."""

    date: str
    teams: List[DailyTeamTokens]


class TimeSeriesOut(BaseModel):
    """Response containing daily time-series data."""

    timeseries: List[DailyTimeSeriesPoint]


class DateRangeParams(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate that date strings are in YYYY-MM-DD format."""
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    @field_validator("start_date")
    @classmethod
    def validate_start_date_not_future(cls, v: Optional[str]) -> Optional[str]:
        """Validate that start_date is not in the future."""
        if v is None:
            return v
        date = datetime.strptime(v, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        if date > now:
            raise ValueError("start_date cannot be in the future")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date_not_future(cls, v: Optional[str]) -> Optional[str]:
        """Validate that end_date is not in the future."""
        if v is None:
            return v
        date = datetime.strptime(v, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        if date > now:
            raise ValueError("end_date cannot be in the future")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: Optional[str], info) -> Optional[str]:
        """Validate that end_date is not before start_date."""
        if v is None or info.data.get("start_date") is None:
            return v
        start = datetime.strptime(info.data["start_date"], "%Y-%m-%d")
        end = datetime.strptime(v, "%Y-%m-%d")
        if end < start:
            raise ValueError("end_date must not be before start_date")
        return v


class ModelUsageOut(BaseModel):
    """Token usage for a specific model (aggregated across all teams)."""

    model: str = "Dummy Model"
    tokens: int = 10000


class ModelsOut(BaseModel):
    """Response containing model usage data."""

    models: List[ModelUsageOut] = [ModelUsageOut()]


class TeamSuccessRate(BaseModel):
    """Success rate summary for a team over a time period."""

    name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float  # Percentage (0-100)


class SuccessRateSummaryOut(BaseModel):
    """Response containing success rate summaries per team."""

    teams: List[TeamSuccessRate]


class CostEfficiencyCell(BaseModel):
    """Cost efficiency for a specific team-model combination."""

    team: str
    model: str
    cost_per_1k_tokens: float
    total_cost: float
    total_tokens: int


class CostEfficiencyOut(BaseModel):
    """Response containing cost efficiency heatmap data."""

    cells: List[CostEfficiencyCell]


class HourlyBucket(BaseModel):
    """Token count for a specific hour of day."""

    hour: int  # 0-23
    tokens: int


class HourlyBreakdownOut(BaseModel):
    """Response containing hourly token breakdown."""

    hours: List[HourlyBucket]

