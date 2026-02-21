"""Dependency injection configuration for FastAPI services."""

from functools import lru_cache
from fastapi import Depends

from src.client.api_client import LiteLLMAPI
from src.services.team_service import TeamService
from src.services.team_daily_activity_service import TeamDailyActivityService
from src.services.token_aggregation_service import TokenAggregationService
from src.services.time_series_service import TimeSeriesService
from src.services.model_usage_service import ModelUsageService
from src.services.success_rate_service import SuccessRateService
from src.services.cost_efficiency_service import CostEfficiencyService
from src.utils.common import get_api_key, get_base_url


@lru_cache()
def get_api_client() -> LiteLLMAPI:
    """
    Get singleton API client instance.

    Uses @lru_cache to ensure only one instance is created per application lifecycle.

    Returns:
        LiteLLMAPI: Configured API client for LiteLLM Gateway.
    """
    return LiteLLMAPI(base_url=get_base_url(), api_key=get_api_key())


def get_team_service(
    api_client: LiteLLMAPI = Depends(get_api_client),
) -> TeamService:
    """
    Get TeamService instance with injected dependencies.

    Args:
        api_client: Injected API client dependency.

    Returns:
        TeamService: Service for managing team data.
    """
    return TeamService(api_client)


def get_team_daily_activity_service(
    api_client: LiteLLMAPI = Depends(get_api_client),
    team_service: TeamService = Depends(get_team_service),
) -> TeamDailyActivityService:
    """
    Get TeamDailyActivityService instance with injected dependencies.

    Args:
        api_client: Injected API client dependency.
        team_service: Injected team service dependency.

    Returns:
        TeamDailyActivityService: Service for fetching team daily activity data.
    """
    return TeamDailyActivityService(api_client, team_service)


def get_token_aggregation_service(
    api_client: LiteLLMAPI = Depends(get_api_client),
    team_service: TeamService = Depends(get_team_service),
) -> TokenAggregationService:
    """
    Get TokenAggregationService instance with injected dependencies.

    Args:
        api_client: Injected API client dependency.
        team_service: Injected team service dependency.

    Returns:
        TokenAggregationService: Service for aggregating total tokens per team.
    """
    return TokenAggregationService(api_client, team_service)


def get_time_series_service(
    api_client: LiteLLMAPI = Depends(get_api_client),
    team_service: TeamService = Depends(get_team_service),
) -> TimeSeriesService:
    """
    Get TimeSeriesService instance with injected dependencies.

    Args:
        api_client: Injected API client dependency.
        team_service: Injected team service dependency.

    Returns:
        TimeSeriesService: Service for fetching daily time series data.
    """
    return TimeSeriesService(api_client, team_service)


def get_model_usage_service(
    activity_service: TeamDailyActivityService = Depends(
        get_team_daily_activity_service
    ),
) -> ModelUsageService:
    """
    Get ModelUsageService instance with injected dependencies.

    Args:
        activity_service: Injected team daily activity service dependency.

    Returns:
        ModelUsageService: Service for aggregating token usage by model.
    """
    return ModelUsageService(activity_service)


def get_success_rate_service(
    api_client: LiteLLMAPI = Depends(get_api_client),
    team_service: TeamService = Depends(get_team_service),
) -> SuccessRateService:
    """
    Get SuccessRateService instance with injected dependencies.

    Args:
        api_client: Injected API client dependency.
        team_service: Injected team service dependency.

    Returns:
        SuccessRateService: Service for calculating team success rates.
    """
    return SuccessRateService(api_client, team_service)


def get_cost_efficiency_service(
    api_client: LiteLLMAPI = Depends(get_api_client),
    team_service: TeamService = Depends(get_team_service),
) -> CostEfficiencyService:
    """
    Get CostEfficiencyService instance with injected dependencies.

    Args:
        api_client: Injected API client dependency.
        team_service: Injected team service dependency.

    Returns:
        CostEfficiencyService: Service for calculating cost efficiency metrics.
    """
    return CostEfficiencyService(api_client, team_service)
