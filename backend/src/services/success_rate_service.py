"""Service for calculating team success rates."""

from typing import List, Dict, Any
from src.services.protocols import APIClientProtocol, TeamServiceProtocol


class SuccessRateService:
    """Service for calculating team success rates."""

    def __init__(
        self, api_client: APIClientProtocol, team_service: TeamServiceProtocol
    ):
        """
        Initialize SuccessRateService with dependencies.

        Args:
            api_client: Client for external API communication
            team_service: Service for team data and mappings
        """
        self.api_client = api_client
        self.team_service = team_service

    def fetch_team_success_rate_summary(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch aggregated success rate summary per team over the entire date range.

        Parameters:
            start_date (str): Start date in ISO format.
            end_date (str): End date in ISO format.

        Returns:
            List of team summaries:
            [
                {
                    "name": "Team A",
                    "total_requests": 500,
                    "successful_requests": 475,
                    "failed_requests": 25,
                    "success_rate": 95.0
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
            # Convert Pydantic model to dict with JSON-serializable values
            data = response.model_dump(mode="json")
        except RuntimeError as e:
            raise RuntimeError(
                f"Error fetching team token usage: {str(e).split(': ', 1)[1]}"
            )

        # Aggregate metrics across all days per team
        team_metrics: Dict[str, Dict[str, int]] = {
            self.team_service.get_team_name(team_id): {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
            }
            for team_id in team_ids
        }

        for entry in data.get("results", []):
            breakdown = entry.get("breakdown", {})
            entities = breakdown.get("entities", {})

            for team_id in team_ids:
                team_name = self.team_service.get_team_name(team_id)
                entity = entities.get(team_id, {})
                metrics = entity.get("metrics", {})

                team_metrics[team_name]["total_requests"] += metrics.get(
                    "api_requests", 0
                )
                team_metrics[team_name]["successful_requests"] += metrics.get(
                    "successful_requests", 0
                )
                team_metrics[team_name]["failed_requests"] += metrics.get(
                    "failed_requests", 0
                )

        # Calculate success rate and format response
        summary = []
        for team_name, metrics in team_metrics.items():
            total = metrics["total_requests"]
            successful = metrics["successful_requests"]

            success_rate = (successful / total * 100) if total > 0 else 0.0

            summary.append(
                {
                    "name": team_name,
                    "total_requests": total,
                    "successful_requests": successful,
                    "failed_requests": metrics["failed_requests"],
                    "success_rate": round(success_rate, 2),
                }
            )

        return summary
