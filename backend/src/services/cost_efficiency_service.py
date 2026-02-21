"""Cost efficiency service for calculating cost per 1k tokens by team and model."""

from typing import Dict, List, Any
from src.services.protocols import (
    APIClientProtocol,
    TeamServiceProtocol,
)


class CostEfficiencyService:
    """Service for calculating cost efficiency metrics."""

    def __init__(
        self,
        api_client: APIClientProtocol,
        team_service: TeamServiceProtocol,
    ):
        """
        Initialize CostEfficiencyService with dependencies.

        Args:
            api_client: Client for external API communication
            team_service: Service for team data and mappings
        """
        self.api_client = api_client
        self.team_service = team_service

    def fetch_cost_efficiency(
        self, start_date: str, end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch cost efficiency data (cost per 1k tokens) by team and model.

        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format

        Returns:
            List of cost efficiency cells with team, model, cost metrics

        Raises:
            RuntimeError: If fetching team data fails
        """
        team_ids = self.team_service.get_team_ids()

        try:
            response = self.api_client.fetch_team_daily_activity(
                team_ids, start_date, end_date
            )
            # Convert Pydantic model to dict with JSON-serializable values
            # Handle both Pydantic models and plain dicts (for testing)
            data = (
                response.model_dump(mode="json")
                if hasattr(response, "model_dump")
                else response
            )
        except RuntimeError as e:
            raise RuntimeError(f"Error fetching team data: {str(e).split(': ', 1)[1]}")

        # Aggregate cost and tokens by team and model
        team_model_data: Dict[str, Dict[str, Dict[str, float]]] = {}

        for entry in data.get("results", []):
            top_level_breakdown = entry.get("breakdown", {})
            entities = top_level_breakdown.get("entities", {})
            models_breakdown = top_level_breakdown.get("model_groups", {})

            for team_id in team_ids:
                team_name = self.team_service.get_team_name(team_id)
                entity = entities.get(team_id, {})

                if team_name not in team_model_data:
                    team_model_data[team_name] = {}

                # Iterate through models to find which ones this team used
                for model_name, model_data in models_breakdown.items():
                    api_key_breakdown = model_data.get("api_key_breakdown", {})

                    # Check if this team's API keys used this model
                    team_api_keys = entity.get("api_key_breakdown", {}).keys()
                    for api_key in team_api_keys:
                        if api_key in api_key_breakdown:
                            key_metrics = api_key_breakdown[api_key].get("metrics", {})
                            tokens = key_metrics.get("total_tokens", 0)
                            spend = key_metrics.get("spend", 0.0)

                            if model_name not in team_model_data[team_name]:
                                team_model_data[team_name][model_name] = {
                                    "total_tokens": 0,
                                    "total_cost": 0.0,
                                }

                            team_model_data[team_name][model_name]["total_tokens"] += (
                                tokens
                            )
                            team_model_data[team_name][model_name]["total_cost"] += (
                                spend
                            )

        # Build result list
        cells = []
        for team_name, models in team_model_data.items():
            for model_name, metrics in models.items():
                total_tokens = metrics["total_tokens"]
                total_cost = metrics["total_cost"]

                # Calculate cost per 1k tokens
                cost_per_1k = (
                    (total_cost / total_tokens * 1000) if total_tokens > 0 else 0.0
                )

                cells.append(
                    {
                        "team": team_name,
                        "model": model_name,
                        "cost_per_1k_tokens": round(cost_per_1k, 4),
                        "total_cost": round(total_cost, 4),
                        "total_tokens": total_tokens,
                    }
                )

        return cells
