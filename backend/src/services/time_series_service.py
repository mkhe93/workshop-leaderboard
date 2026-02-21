from typing import List, Dict, Any
from src.services.protocols import APIClientProtocol, TeamServiceProtocol


class TimeSeriesService:
    """Service for fetching daily time series token data."""

    def __init__(
        self, api_client: APIClientProtocol, team_service: TeamServiceProtocol
    ):
        """
        Initialize the TimeSeriesService.

        Parameters:
            api_client: API client for fetching team activity data
            team_service: Service for managing team data and mappings
        """
        self.api_client = api_client
        self.team_service = team_service

    def fetch_daily_timeseries_per_team(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch daily time-series token data per team.
        Returns one data point per day with token counts and request metrics for each team.

        Parameters:
            start_date (str): Start date in ISO format.
            end_date (str): End date in ISO format.

        Returns:
            List of daily data points:
            [
                {
                    "date": "2024-01-15",
                    "teams": [
                        {
                            "name": "Team A",
                            "tokens": 1500,
                            "total_requests": 100,
                            "successful_requests": 95,
                            "failed_requests": 5
                        },
                        ...
                    ]
                },
                ...
            ]

        Raises:
            RuntimeError: If fetching team token usage fails.
        """
        team_ids = self.team_service.get_team_ids()

        try:
            response = self.api_client.fetch_team_daily_activity(
                team_ids, start_date, end_date
            )
            # Convert Pydantic model to dict with JSON-serializable values (dates as strings)
            data = response.model_dump(mode="json")
        except RuntimeError as e:
            raise RuntimeError(
                f"Error fetching team token usage: {str(e).split(': ', 1)[1]}"
            )

        # Process daily results
        daily_data = []
        for entry in data.get("results", []):
            date = entry.get("date")
            breakdown = entry.get("breakdown") or {}
            entities = breakdown.get("entities", {})

            teams_for_day = []
            for team_id in team_ids:
                team_name = self.team_service.get_team_name(team_id)
                entity = entities.get(team_id, {})
                metrics = entity.get("metrics", {})

                total_tokens = metrics.get("total_tokens", 0)
                # LiteLLM API uses 'api_requests', not 'total_api_requests'
                total_requests = metrics.get("api_requests", 0)
                successful_requests = metrics.get("successful_requests", 0)
                failed_requests = metrics.get("failed_requests", 0)

                teams_for_day.append(
                    {
                        "name": team_name,
                        "tokens": total_tokens,
                        "total_requests": total_requests,
                        "successful_requests": successful_requests,
                        "failed_requests": failed_requests,
                    }
                )

            daily_data.append({"date": date, "teams": teams_for_day})

        return daily_data
