"""Unit tests for CostEfficiencyService."""

import pytest
from typing import List, Dict, Any
from src.services.cost_efficiency_service import CostEfficiencyService
from src.client.models import SpendAnalyticsPaginatedResponse


class MockAPIClient:
    """Mock API client for testing CostEfficiencyService."""

    def __init__(self, activity_data: Dict[str, Any]):
        """Initialize mock with test data."""
        self._activity_data = activity_data
        self.fetch_call_count = 0

    def fetch_teams(self) -> List[Dict[str, Any]]:
        """Mock fetch_teams method."""
        return []

    def fetch_team_daily_activity(
        self,
        team_ids: List[str],
        start_date: str,
        end_date: str,
        page_size: int = 20000,
    ) -> SpendAnalyticsPaginatedResponse:
        """Mock fetch_team_daily_activity method."""
        self.fetch_call_count += 1
        return SpendAnalyticsPaginatedResponse.model_validate(self._activity_data)


class MockTeamService:
    """Mock team service for testing CostEfficiencyService."""

    def __init__(self, team_ids: List[str], team_names: Dict[str, str]):
        """Initialize mock with team data."""
        self._team_ids = team_ids
        self._team_names = team_names

    def fetch_teams(self) -> List[Dict[str, Any]]:
        """Mock fetch_teams method."""
        return []

    def get_team_ids(self) -> List[str]:
        """Mock get_team_ids method."""
        return self._team_ids

    def get_team_name(self, team_id: str) -> str:
        """Mock get_team_name method."""
        return self._team_names.get(team_id, team_id)


class TestCostEfficiencyService:
    """Test suite for CostEfficiencyService."""

    def test_cost_per_1k_tokens_calculation(self):
        """Test cost per 1k tokens calculation."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                    "key2": {"metrics": {}},
                                },
                            },
                            "team2": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key3": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 100000,
                                            "spend": 3.0,
                                        }
                                    },
                                    "key2": {
                                        "metrics": {
                                            "total_tokens": 50000,
                                            "spend": 1.5,
                                        }
                                    },
                                },
                            },
                            "anthropic/claude-3": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key3": {
                                        "metrics": {
                                            "total_tokens": 200000,
                                            "spend": 10.0,
                                        }
                                    },
                                },
                            },
                        },
                    },
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_names={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act
        result = service.fetch_cost_efficiency("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 2
        assert mock_client.fetch_call_count == 1

        # Find cells in result
        alpha_gpt4 = next(
            cell
            for cell in result
            if cell["team"] == "Alpha Team" and cell["model"] == "openai/gpt-4"
        )
        beta_claude = next(
            cell
            for cell in result
            if cell["team"] == "Beta Team" and cell["model"] == "anthropic/claude-3"
        )

        # Alpha Team + GPT-4: 150000 tokens, $4.50 cost = $0.03 per 1k tokens
        assert alpha_gpt4["total_tokens"] == 150000
        assert alpha_gpt4["total_cost"] == 4.5
        assert alpha_gpt4["cost_per_1k_tokens"] == 0.03

        # Beta Team + Claude 3: 200000 tokens, $10.00 cost = $0.05 per 1k tokens
        assert beta_claude["total_tokens"] == 200000
        assert beta_claude["total_cost"] == 10.0
        assert beta_claude["cost_per_1k_tokens"] == 0.05

    def test_zero_tokens_edge_case(self):
        """Test zero tokens edge case."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 0,
                                            "spend": 0.0,
                                        }
                                    },
                                },
                            },
                        },
                    },
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"],
            team_names={"team1": "Alpha Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act
        result = service.fetch_cost_efficiency("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 1
        cell = result[0]

        # Zero tokens should result in 0.0 cost per 1k tokens
        assert cell["team"] == "Alpha Team"
        assert cell["model"] == "openai/gpt-4"
        assert cell["total_tokens"] == 0
        assert cell["total_cost"] == 0.0
        assert cell["cost_per_1k_tokens"] == 0.0

    def test_rounding_to_4_decimal_places(self):
        """Test rounding to 4 decimal places."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 333333,
                                            "spend": 9.999999,
                                        }
                                    },
                                },
                            },
                        },
                    },
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"],
            team_names={"team1": "Alpha Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act
        result = service.fetch_cost_efficiency("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 1
        cell = result[0]

        # Cost per 1k: (9.999999 / 333333) * 1000 = 0.029999997... should round to 0.03
        assert cell["cost_per_1k_tokens"] == 0.03
        # Total cost should also be rounded to 4 decimal places
        assert cell["total_cost"] == 10.0

    def test_cost_efficiency_with_empty_data(self):
        """Test with empty API response."""
        # Arrange
        mock_activity_data = {"results": []}
        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_names={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act
        result = service.fetch_cost_efficiency("2024-01-15", "2024-01-16")

        # Assert
        assert len(result) == 0
        assert mock_client.fetch_call_count == 1

    def test_cost_efficiency_with_multiple_teams_and_models(self):
        """Test cost efficiency with multiple teams and models."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                    "key2": {"metrics": {}},
                                },
                            },
                            "team2": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key3": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 100000,
                                            "spend": 3.0,
                                        }
                                    },
                                },
                            },
                            "openai/gpt-3.5-turbo": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key2": {
                                        "metrics": {
                                            "total_tokens": 500000,
                                            "spend": 1.0,
                                        }
                                    },
                                },
                            },
                            "anthropic/claude-3": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key3": {
                                        "metrics": {
                                            "total_tokens": 200000,
                                            "spend": 10.0,
                                        }
                                    },
                                },
                            },
                        },
                    },
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_names={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act
        result = service.fetch_cost_efficiency("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 3

        # Find cells
        alpha_gpt4 = next(
            cell
            for cell in result
            if cell["team"] == "Alpha Team" and cell["model"] == "openai/gpt-4"
        )
        alpha_gpt35 = next(
            cell
            for cell in result
            if cell["team"] == "Alpha Team" and cell["model"] == "openai/gpt-3.5-turbo"
        )
        beta_claude = next(
            cell
            for cell in result
            if cell["team"] == "Beta Team" and cell["model"] == "anthropic/claude-3"
        )

        # Verify calculations
        assert alpha_gpt4["cost_per_1k_tokens"] == 0.03
        assert alpha_gpt35["cost_per_1k_tokens"] == 0.002
        assert beta_claude["cost_per_1k_tokens"] == 0.05

    def test_cost_efficiency_aggregation_across_multiple_days(self):
        """Test that costs are correctly aggregated across multiple days."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 100000,
                                            "spend": 3.0,
                                        }
                                    },
                                },
                            },
                        },
                    },
                },
                {
                    "date": "2024-01-16",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 200000,
                                            "spend": 6.0,
                                        }
                                    },
                                },
                            },
                        },
                    },
                },
                {
                    "date": "2024-01-17",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 300000,
                                            "spend": 9.0,
                                        }
                                    },
                                },
                            },
                        },
                    },
                },
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"],
            team_names={"team1": "Alpha Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act
        result = service.fetch_cost_efficiency("2024-01-15", "2024-01-17")

        # Assert
        assert len(result) == 1
        cell = result[0]

        # Total: 600000 tokens, $18.00 cost = $0.03 per 1k tokens
        assert cell["team"] == "Alpha Team"
        assert cell["model"] == "openai/gpt-4"
        assert cell["total_tokens"] == 600000
        assert cell["total_cost"] == 18.0
        assert cell["cost_per_1k_tokens"] == 0.03

    def test_cost_efficiency_with_model_name(self):
        """Test that model names are correctly mapped."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "openai/gpt-4-0613": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 100000,
                                            "spend": 3.0,
                                        }
                                    },
                                },
                            },
                        },
                    },
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"],
            team_names={"team1": "Alpha Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act
        result = service.fetch_cost_efficiency("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 1
        cell = result[0]
        assert cell["model"] == "openai/gpt-4-0613"

    def test_cost_efficiency_with_unmapped_model_name(self):
        """Test that unmapped model names are used as-is."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "custom/my-model": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 100000,
                                            "spend": 5.0,
                                        }
                                    },
                                },
                            },
                        },
                    },
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"],
            team_names={"team1": "Alpha Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act
        result = service.fetch_cost_efficiency("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 1
        cell = result[0]
        assert cell["model"] == "custom/my-model"

    def test_cost_efficiency_api_error_handling(self):
        """Test error handling when API client raises RuntimeError."""

        # Arrange
        class ErrorMockAPIClient:
            def fetch_teams(self) -> List[Dict[str, Any]]:
                return []

            def fetch_team_daily_activity(
                self,
                team_ids: List[str],
                start_date: str,
                end_date: str,
                page_size: int = 20000,
            ) -> Dict[str, Any]:
                raise RuntimeError("External API error: Connection timeout")

            def get_model_name_map(self, ttl_seconds: int = 300) -> Dict[str, str]:
                return {}

        mock_client = ErrorMockAPIClient()
        mock_team_service = MockTeamService(
            team_ids=["team1"],
            team_names={"team1": "Alpha Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            service.fetch_cost_efficiency("2024-01-15", "2024-01-16")

        assert "Error fetching team data: Connection timeout" in str(exc_info.value)

    def test_cost_efficiency_with_missing_api_keys(self):
        """Test when team has no API keys in the model breakdown."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                },
                            },
                            "team2": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key2": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 100000,
                                            "spend": 3.0,
                                        }
                                    },
                                    # key2 not in this model's breakdown
                                },
                            },
                        },
                    },
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_names={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act
        result = service.fetch_cost_efficiency("2024-01-15", "2024-01-15")

        # Assert
        # Only team1 should have data since team2's key is not in the model breakdown
        assert len(result) == 1
        cell = result[0]
        assert cell["team"] == "Alpha Team"
        assert cell["model"] == "openai/gpt-4"

    def test_cost_efficiency_with_missing_metrics(self):
        """Test when metrics are partially missing."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {"metrics": {}},
                                },
                            },
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "metrics": {},  # Required field for Pydantic validation
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            # total_tokens and spend missing
                                        }
                                    },
                                },
                            },
                        },
                    },
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"],
            team_names={"team1": "Alpha Team"},
        )
        service = CostEfficiencyService(
            mock_client,
            mock_team_service,
        )

        # Act
        result = service.fetch_cost_efficiency("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 1
        cell = result[0]

        # Missing metrics should default to 0
        assert cell["total_tokens"] == 0
        assert cell["total_cost"] == 0.0
        assert cell["cost_per_1k_tokens"] == 0.0
