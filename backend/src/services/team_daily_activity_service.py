"""Service for fetching team daily activity data."""

from typing import Dict, Any
from src.services.protocols import APIClientProtocol, TeamServiceProtocol


class TeamDailyActivityService:
    """Service for fetching team daily activity data from the API."""

    def __init__(
        self,
        api_client: APIClientProtocol,
        team_service: TeamServiceProtocol,
    ):
        """
        Initialize TeamDailyActivityService with dependencies.

        Args:
            api_client: Client for external API communication
            team_service: Service for team management
        """
        self.api_client = api_client
        self.team_service = team_service

    def fetch_daily_activity(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch daily activity data for all teams.

        Args:
            start_date: Start date in API format (YYYY-MM-DD)
            end_date: End date in API format (YYYY-MM-DD)

        Returns:
            Dictionary containing results array with daily activity data.
            Structure: {"results": [{"date": "...", "breakdown": {...}}, ...]}

        Raises:
            RuntimeError: If fetching team activity fails
        """
        team_ids = self.team_service.get_team_ids()
        response = self.api_client.fetch_team_daily_activity(
            team_ids, start_date, end_date
        )
        # Convert Pydantic model to dict with JSON-serializable values
        return response.model_dump(mode="json")
