"""Service for aggregating token usage by model."""

from typing import Dict
from src.services.protocols import (
    TeamDailyActivityServiceProtocol,
    ModelMappingServiceProtocol,
)


class ModelUsageService:
    """Service for aggregating token usage by model."""

    def __init__(
        self,
        daily_activity_service: TeamDailyActivityServiceProtocol,
        model_mapping_service: ModelMappingServiceProtocol,
    ):
        """
        Initialize ModelUsageService with dependencies.

        Args:
            daily_activity_service: Service for fetching team daily activity
            model_mapping_service: Service for model name mapping
        """
        self.daily_activity_service = daily_activity_service
        self.model_mapping_service = model_mapping_service

    def fetch_model_usage(self, start_date: str, end_date: str) -> Dict[str, int]:
        """
        Aggregate total tokens per model across all teams.

        Args:
            start_date: Start date in API format (YYYY.MM.DD)
            end_date: End date in ISO format

        Returns:
            Dict mapping model display names to total token counts,
            sorted by tokens descending, with zero-token models filtered out.
            Example: {"GPT-4": 125000, "Claude 3 Opus": 98000}

        Raises:
            RuntimeError: If fetching team token usage fails
        """
        data = self.daily_activity_service.fetch_daily_activity(start_date, end_date)

        model_totals: Dict[str, int] = {}

        for entry in data.get("results", []):
            top_level_breakdown = entry.get("breakdown", {})
            models_breakdown = top_level_breakdown.get("models", {})

            for model_name, model_data in models_breakdown.items():
                display_name = self.model_mapping_service.get_display_name(model_name)
                metrics = model_data.get("metrics", {})
                total_tokens = metrics.get("total_tokens", 0)

                model_totals[display_name] = (
                    model_totals.get(display_name, 0) + total_tokens
                )

        # Filter out zero-token models and sort by tokens descending
        filtered = {name: tokens for name, tokens in model_totals.items() if tokens > 0}
        return dict(sorted(filtered.items(), key=lambda x: x[1], reverse=True))
