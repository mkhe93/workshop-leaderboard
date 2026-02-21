"""Token aggregation service for calculating total tokens per team with breakdown data."""

from typing import Dict, Any
from src.services.protocols import (
    APIClientProtocol,
    TeamServiceProtocol,
)


class TokenAggregationService:
    """Service for aggregating total tokens per team with detailed breakdown."""

    def __init__(
        self,
        api_client: APIClientProtocol,
        team_service: TeamServiceProtocol,
    ):
        """
        Initialize TokenAggregationService with injected dependencies.

        Args:
            api_client: Client for external API communication
            team_service: Service for team data
        """
        self.api_client = api_client
        self.team_service = team_service

    def fetch_total_tokens_per_team(
        self, start_date: str, end_date: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate total tokens per team using API data.
        Extended to return both total tokens and breakdown data.

        Parameters:
            start_date (str): Start date in ISO format.
            end_date (str): End date in ISO format.

        Returns:
            Dict with structure:
            {
                "team_name": {
                    "total_tokens": int,
                    "breakdown": {
                        "api_keys": [
                            {
                                "api_key": str,
                                "models": [
                                    {
                                        "model_name": str,
                                        "total_tokens": int,
                                        "prompt_tokens": int,
                                        "completion_tokens": int
                                    }
                                ]
                            }
                        ]
                    }
                }
            }

        Raises:
            RuntimeError: If fetching team token usage fails.
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
            raise RuntimeError(
                f"Error fetching team token usage: {str(e).split(': ', 1)[1]}"
            )

        # Initialize result structure
        team_data: Dict[str, Dict[str, Any]] = {
            self.team_service.get_team_name(team_id): {
                "total_tokens": 0,
                "breakdown": {"api_keys": []},
            }
            for team_id in team_ids
        }

        # Aggregate data from API response
        for entry in data.get("results", []):
            top_level_breakdown = entry.get("breakdown", {})
            entities = top_level_breakdown.get("entities", {})

            for team_id, entity in entities.items():
                total_tokens = entity.get("metrics", {}).get("total_tokens", 0)
                team_name = self.team_service.get_team_name(team_id)

                if team_name in team_data:
                    team_data[team_name]["total_tokens"] += total_tokens

                    # Extract and merge breakdown data
                    breakdown = self._extract_breakdown(entity, top_level_breakdown)
                    self._merge_breakdown(team_data[team_name]["breakdown"], breakdown)

        return team_data

    def _extract_breakdown(
        self,
        entity: Dict[str, Any],
        top_level_breakdown: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract model and API key breakdown from entity data and top-level breakdown.

        The LiteLLM Gateway structure has models at the top-level breakdown, with each model
        containing api_key_breakdown showing which keys used that model.

        Top-level breakdown structure:
        {
            "models": {
                "model-name": {
                    "metrics": {...},
                    "api_key_breakdown": {
                        "api-key-hash": {
                            "metrics": {
                                "total_tokens": int,
                                "prompt_tokens": int,
                                "completion_tokens": int
                            },
                            "metadata": {
                                "key_alias": "DevBoost (Internal)"
                            }
                        }
                    }
                }
            },
            "api_keys": {
                "api-key-hash": {
                    "metadata": {
                        "key_alias": "DevBoost (Internal)"
                    }
                }
            }
        }

        Returns:
            Dict with structure:
            {
                "api_keys": [
                    {
                        "api_key": str,
                        "key_alias": str (optional),
                        "models": [
                            {
                                "model_name": str,
                                "total_tokens": int,
                                "prompt_tokens": int,
                                "completion_tokens": int
                            }
                        ]
                    }
                ]
            }
        """
        breakdown = {"api_keys": []}

        # Get the team's API keys from entity-level breakdown
        entity_api_keys = set(entity.get("api_key_breakdown", {}).keys())

        # Get key aliases from top-level api_keys breakdown
        top_level_api_keys = top_level_breakdown.get("api_keys", {})

        # Build a map of api_key -> list of models
        api_key_models: Dict[str, list] = {key: [] for key in entity_api_keys}

        # Iterate through top-level models
        top_level_models = top_level_breakdown.get("model_groups", {})
        for model_name, model_data in top_level_models.items():
            model_api_key_breakdown = model_data.get("api_key_breakdown", {})

            # Check which of this team's API keys used this model
            for api_key in entity_api_keys:
                if api_key in model_api_key_breakdown:
                    key_metrics = model_api_key_breakdown[api_key].get("metrics", {})
                    api_key_models[api_key].append(
                        {
                            "model_name": model_name,
                            "total_tokens": key_metrics.get("total_tokens", 0),
                            "prompt_tokens": key_metrics.get("prompt_tokens", 0),
                            "completion_tokens": key_metrics.get(
                                "completion_tokens", 0
                            ),
                        }
                    )

        # Build the final structure with key aliases
        for api_key, models in api_key_models.items():
            # Get key_alias from top-level api_keys breakdown
            key_alias = (
                top_level_api_keys.get(api_key, {}).get("metadata", {}).get("key_alias")
            )

            if models:  # Only include keys that have model data
                key_entry = {"api_key": api_key, "models": models}
                if key_alias:
                    key_entry["key_alias"] = key_alias
                breakdown["api_keys"].append(key_entry)
            else:
                # Fallback: if no model data, show aggregated metrics
                entity_key_data = entity.get("api_key_breakdown", {}).get(api_key, {})
                metrics = entity_key_data.get("metrics", {})
                key_entry = {
                    "api_key": api_key,
                    "models": [
                        {
                            "model_name": "All Models",
                            "total_tokens": metrics.get("total_tokens", 0),
                            "prompt_tokens": metrics.get("prompt_tokens", 0),
                            "completion_tokens": metrics.get("completion_tokens", 0),
                        }
                    ],
                }
                if key_alias:
                    key_entry["key_alias"] = key_alias
                breakdown["api_keys"].append(key_entry)

        return breakdown

    def _merge_breakdown(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Merge breakdown data from multiple date entries.
        Aggregates token counts for matching api_key + model combinations.

        Parameters:
            target: The target breakdown dict to merge into (modified in place)
            source: The source breakdown dict to merge from
        """
        # Create lookup for existing api_keys
        existing_keys = {item["api_key"]: item for item in target["api_keys"]}

        for source_key_data in source["api_keys"]:
            api_key = source_key_data["api_key"]

            if api_key in existing_keys:
                # Merge models for this key
                existing_models = {
                    m["model_name"]: m for m in existing_keys[api_key]["models"]
                }

                for source_model in source_key_data["models"]:
                    model_name = source_model["model_name"]

                    if model_name in existing_models:
                        # Aggregate tokens
                        existing_models[model_name]["total_tokens"] += source_model[
                            "total_tokens"
                        ]
                        existing_models[model_name]["prompt_tokens"] += source_model[
                            "prompt_tokens"
                        ]
                        existing_models[model_name]["completion_tokens"] += (
                            source_model["completion_tokens"]
                        )
                    else:
                        # Add new model
                        existing_keys[api_key]["models"].append(source_model)
            else:
                # Add new api_key entry
                target["api_keys"].append(source_key_data)
