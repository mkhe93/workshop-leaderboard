"""Unit tests for TimeSeriesService."""

import pytest
from typing import List, Dict, Any
from src.services.time_series_service import TimeSeriesService
from src.client.models import SpendAnalyticsPaginatedResponse


class MockAPIClient:
    """Mock API client for testing TimeSeriesService."""

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

    def get_model_name_map(self, ttl_seconds: int = 300) -> Dict[str, str]:
        """Mock get_model_name_map method."""
        return {}


class MockTeamService:
    """Mock team service for testing TimeSeriesService."""

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


class TestTimeSeriesService:
    """Test suite for TimeSeriesService."""

    def test_fetch_daily_timeseries_with_valid_data(self):
        """Test time series data with mocked API responses."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {
                                    "total_tokens": 1500,
                                    "api_requests": 100,
                                    "successful_requests": 95,
                                    "failed_requests": 5,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "total_tokens": 2000,
                                    "api_requests": 150,
                                    "successful_requests": 145,
                                    "failed_requests": 5,
                                }
                            },
                        }
                    },
                },
                {
                    "date": "2024-01-16",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {
                                    "total_tokens": 1800,
                                    "api_requests": 120,
                                    "successful_requests": 115,
                                    "failed_requests": 5,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "total_tokens": 2200,
                                    "api_requests": 160,
                                    "successful_requests": 155,
                                    "failed_requests": 5,
                                }
                            },
                        }
                    },
                },
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_names={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = TimeSeriesService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_daily_timeseries_per_team("2024-01-15", "2024-01-16")

        # Assert
        assert len(result) == 2
        assert mock_client.fetch_call_count == 1

        # Check first day
        assert result[0]["date"] == "2024-01-15"
        assert len(result[0]["teams"]) == 2
        assert result[0]["teams"][0] == {
            "name": "Alpha Team",
            "tokens": 1500,
            "total_requests": 100,
            "successful_requests": 95,
            "failed_requests": 5,
        }
        assert result[0]["teams"][1] == {
            "name": "Beta Team",
            "tokens": 2000,
            "total_requests": 150,
            "successful_requests": 145,
            "failed_requests": 5,
        }

        # Check second day
        assert result[1]["date"] == "2024-01-16"
        assert len(result[1]["teams"]) == 2
        assert result[1]["teams"][0] == {
            "name": "Alpha Team",
            "tokens": 1800,
            "total_requests": 120,
            "successful_requests": 115,
            "failed_requests": 5,
        }
        assert result[1]["teams"][1] == {
            "name": "Beta Team",
            "tokens": 2200,
            "total_requests": 160,
            "successful_requests": 155,
            "failed_requests": 5,
        }

    def test_fetch_daily_timeseries_with_empty_data(self):
        """Test empty data scenario."""
        # Arrange
        mock_activity_data = {"results": []}
        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_names={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = TimeSeriesService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_daily_timeseries_per_team("2024-01-15", "2024-01-16")

        # Assert
        assert result == []
        assert mock_client.fetch_call_count == 1

    def test_fetch_daily_timeseries_with_missing_team_data(self):
        """Test when some teams have no data for a given day."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {
                                    "total_tokens": 1500,
                                    "api_requests": 100,
                                    "successful_requests": 95,
                                    "failed_requests": 5,
                                }
                            }
                            # team2 has no data for this day
                        }
                    },
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_names={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = TimeSeriesService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_daily_timeseries_per_team("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 1
        assert result[0]["date"] == "2024-01-15"
        assert len(result[0]["teams"]) == 2

        # team1 has data
        assert result[0]["teams"][0] == {
            "name": "Alpha Team",
            "tokens": 1500,
            "total_requests": 100,
            "successful_requests": 95,
            "failed_requests": 5,
        }

        # team2 has zero values (missing data)
        assert result[0]["teams"][1] == {
            "name": "Beta Team",
            "tokens": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
        }

    def test_fetch_daily_timeseries_with_multiple_teams_and_dates(self):
        """Test multiple teams and multiple dates."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {
                                    "total_tokens": 1000,
                                    "api_requests": 50,
                                    "successful_requests": 48,
                                    "failed_requests": 2,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "total_tokens": 2000,
                                    "api_requests": 100,
                                    "successful_requests": 95,
                                    "failed_requests": 5,
                                }
                            },
                            "team3": {
                                "metrics": {
                                    "total_tokens": 3000,
                                    "api_requests": 150,
                                    "successful_requests": 140,
                                    "failed_requests": 10,
                                }
                            },
                        }
                    },
                },
                {
                    "date": "2024-01-16",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {
                                    "total_tokens": 1200,
                                    "api_requests": 60,
                                    "successful_requests": 58,
                                    "failed_requests": 2,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "total_tokens": 2500,
                                    "api_requests": 120,
                                    "successful_requests": 115,
                                    "failed_requests": 5,
                                }
                            },
                            "team3": {
                                "metrics": {
                                    "total_tokens": 3500,
                                    "api_requests": 180,
                                    "successful_requests": 170,
                                    "failed_requests": 10,
                                }
                            },
                        }
                    },
                },
                {
                    "date": "2024-01-17",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {
                                    "total_tokens": 1100,
                                    "api_requests": 55,
                                    "successful_requests": 53,
                                    "failed_requests": 2,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "total_tokens": 2300,
                                    "api_requests": 110,
                                    "successful_requests": 105,
                                    "failed_requests": 5,
                                }
                            },
                            "team3": {
                                "metrics": {
                                    "total_tokens": 3200,
                                    "api_requests": 160,
                                    "successful_requests": 150,
                                    "failed_requests": 10,
                                }
                            },
                        }
                    },
                },
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2", "team3"],
            team_names={
                "team1": "Alpha Team",
                "team2": "Beta Team",
                "team3": "Gamma Team",
            },
        )
        service = TimeSeriesService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_daily_timeseries_per_team("2024-01-15", "2024-01-17")

        # Assert
        assert len(result) == 3
        assert mock_client.fetch_call_count == 1

        # Verify all dates are present
        assert result[0]["date"] == "2024-01-15"
        assert result[1]["date"] == "2024-01-16"
        assert result[2]["date"] == "2024-01-17"

        # Verify all teams are present in each day
        for day_data in result:
            assert len(day_data["teams"]) == 3
            team_names = [team["name"] for team in day_data["teams"]]
            assert "Alpha Team" in team_names
            assert "Beta Team" in team_names
            assert "Gamma Team" in team_names

    def test_fetch_daily_timeseries_with_missing_metrics(self):
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
                                "metrics": {
                                    "total_tokens": 1500,
                                    # Missing api_requests, successful_requests, failed_requests
                                }
                            },
                            "team2": {
                                "metrics": {
                                    # All metrics missing
                                }
                            },
                        }
                    },
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_names={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = TimeSeriesService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_daily_timeseries_per_team("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 1
        assert result[0]["teams"][0] == {
            "name": "Alpha Team",
            "tokens": 1500,
            "total_requests": 0,  # Default to 0
            "successful_requests": 0,  # Default to 0
            "failed_requests": 0,  # Default to 0
        }
        assert result[0]["teams"][1] == {
            "name": "Beta Team",
            "tokens": 0,  # Default to 0
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
        }

    def test_fetch_daily_timeseries_with_missing_breakdown(self):
        """Test when breakdown structure is missing."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    # Missing breakdown
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"],
            team_names={"team1": "Alpha Team"},
        )
        service = TimeSeriesService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_daily_timeseries_per_team("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 1
        assert result[0]["date"] == "2024-01-15"
        assert result[0]["teams"][0] == {
            "name": "Alpha Team",
            "tokens": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
        }

    def test_fetch_daily_timeseries_with_no_teams(self):
        """Test when there are no teams."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {"entities": {}},
                }
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=[],  # No teams
            team_names={},
        )
        service = TimeSeriesService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_daily_timeseries_per_team("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 1
        assert result[0]["date"] == "2024-01-15"
        assert result[0]["teams"] == []

    def test_fetch_daily_timeseries_api_error_handling(self):
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
            ) -> SpendAnalyticsPaginatedResponse:
                raise RuntimeError("External API error: Connection timeout")

            def get_model_name_map(self, ttl_seconds: int = 300) -> Dict[str, str]:
                return {}

        mock_client = ErrorMockAPIClient()
        mock_team_service = MockTeamService(
            team_ids=["team1"],
            team_names={"team1": "Alpha Team"},
        )
        service = TimeSeriesService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            service.fetch_daily_timeseries_per_team("2024-01-15", "2024-01-16")

        assert "Error fetching team token usage: Connection timeout" in str(
            exc_info.value
        )

    def test_fetch_daily_timeseries_preserves_date_order(self):
        """Test that date order from API is preserved."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-17",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {
                                    "total_tokens": 300,
                                    "api_requests": 30,
                                    "successful_requests": 28,
                                    "failed_requests": 2,
                                }
                            }
                        }
                    },
                },
                {
                    "date": "2024-01-15",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {
                                    "total_tokens": 100,
                                    "api_requests": 10,
                                    "successful_requests": 9,
                                    "failed_requests": 1,
                                }
                            }
                        }
                    },
                },
                {
                    "date": "2024-01-16",
                    "metrics": {},  # Required field for Pydantic validation
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {
                                    "total_tokens": 200,
                                    "api_requests": 20,
                                    "successful_requests": 19,
                                    "failed_requests": 1,
                                }
                            }
                        }
                    },
                },
            ]
        }

        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"],
            team_names={"team1": "Alpha Team"},
        )
        service = TimeSeriesService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_daily_timeseries_per_team("2024-01-15", "2024-01-17")

        # Assert - dates should be in the order returned by API
        assert len(result) == 3
        assert result[0]["date"] == "2024-01-17"
        assert result[1]["date"] == "2024-01-15"
        assert result[2]["date"] == "2024-01-16"
