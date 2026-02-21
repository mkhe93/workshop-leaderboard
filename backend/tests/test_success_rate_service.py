"""Unit tests for SuccessRateService."""

import pytest
from typing import List, Dict, Any
from src.services.success_rate_service import SuccessRateService
from src.client.models import SpendAnalyticsPaginatedResponse


class MockAPIClient:
    """Mock API client for testing SuccessRateService."""

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
    """Mock team service for testing SuccessRateService."""

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


class TestSuccessRateService:
    """Test suite for SuccessRateService."""

    def test_success_rate_calculation_with_various_request_counts(self):
        """Test success rate calculation with various request counts."""
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
                                    "api_requests": 100,
                                    "successful_requests": 95,
                                    "failed_requests": 5,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "api_requests": 200,
                                    "successful_requests": 180,
                                    "failed_requests": 20,
                                }
                            },
                            "team3": {
                                "metrics": {
                                    "api_requests": 50,
                                    "successful_requests": 48,
                                    "failed_requests": 2,
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
                                    "api_requests": 150,
                                    "successful_requests": 140,
                                    "failed_requests": 10,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "api_requests": 100,
                                    "successful_requests": 85,
                                    "failed_requests": 15,
                                }
                            },
                            "team3": {
                                "metrics": {
                                    "api_requests": 75,
                                    "successful_requests": 73,
                                    "failed_requests": 2,
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
        service = SuccessRateService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_team_success_rate_summary("2024-01-15", "2024-01-16")

        # Assert
        assert len(result) == 3
        assert mock_client.fetch_call_count == 1

        # Find teams in result
        alpha_team = next(team for team in result if team["name"] == "Alpha Team")
        beta_team = next(team for team in result if team["name"] == "Beta Team")
        gamma_team = next(team for team in result if team["name"] == "Gamma Team")

        # Alpha Team: 235 successful out of 250 total = 94%
        assert alpha_team["total_requests"] == 250
        assert alpha_team["successful_requests"] == 235
        assert alpha_team["failed_requests"] == 15
        assert alpha_team["success_rate"] == 94.0

        # Beta Team: 265 successful out of 300 total = 88.33%
        assert beta_team["total_requests"] == 300
        assert beta_team["successful_requests"] == 265
        assert beta_team["failed_requests"] == 35
        assert beta_team["success_rate"] == 88.33

        # Gamma Team: 121 successful out of 125 total = 96.8%
        assert gamma_team["total_requests"] == 125
        assert gamma_team["successful_requests"] == 121
        assert gamma_team["failed_requests"] == 4
        assert gamma_team["success_rate"] == 96.8

    def test_zero_requests_edge_case(self):
        """Test zero requests edge case."""
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
                                    "api_requests": 0,
                                    "successful_requests": 0,
                                    "failed_requests": 0,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "api_requests": 100,
                                    "successful_requests": 95,
                                    "failed_requests": 5,
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
        service = SuccessRateService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_team_success_rate_summary("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 2

        # Find teams in result
        alpha_team = next(team for team in result if team["name"] == "Alpha Team")
        beta_team = next(team for team in result if team["name"] == "Beta Team")

        # Alpha Team: 0 requests should result in 0.0% success rate
        assert alpha_team["total_requests"] == 0
        assert alpha_team["successful_requests"] == 0
        assert alpha_team["failed_requests"] == 0
        assert alpha_team["success_rate"] == 0.0

        # Beta Team: Normal calculation
        assert beta_team["total_requests"] == 100
        assert beta_team["successful_requests"] == 95
        assert beta_team["failed_requests"] == 5
        assert beta_team["success_rate"] == 95.0

    def test_100_percent_success_rate(self):
        """Test 100% success rate."""
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
                                    "api_requests": 100,
                                    "successful_requests": 100,
                                    "failed_requests": 0,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "api_requests": 250,
                                    "successful_requests": 250,
                                    "failed_requests": 0,
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
                                    "api_requests": 150,
                                    "successful_requests": 150,
                                    "failed_requests": 0,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "api_requests": 300,
                                    "successful_requests": 300,
                                    "failed_requests": 0,
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
        service = SuccessRateService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_team_success_rate_summary("2024-01-15", "2024-01-16")

        # Assert
        assert len(result) == 2

        # Find teams in result
        alpha_team = next(team for team in result if team["name"] == "Alpha Team")
        beta_team = next(team for team in result if team["name"] == "Beta Team")

        # Alpha Team: 250 successful out of 250 total = 100%
        assert alpha_team["total_requests"] == 250
        assert alpha_team["successful_requests"] == 250
        assert alpha_team["failed_requests"] == 0
        assert alpha_team["success_rate"] == 100.0

        # Beta Team: 550 successful out of 550 total = 100%
        assert beta_team["total_requests"] == 550
        assert beta_team["successful_requests"] == 550
        assert beta_team["failed_requests"] == 0
        assert beta_team["success_rate"] == 100.0

    def test_0_percent_success_rate(self):
        """Test 0% success rate."""
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
                                    "api_requests": 100,
                                    "successful_requests": 0,
                                    "failed_requests": 100,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "api_requests": 50,
                                    "successful_requests": 0,
                                    "failed_requests": 50,
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
                                    "api_requests": 75,
                                    "successful_requests": 0,
                                    "failed_requests": 75,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "api_requests": 25,
                                    "successful_requests": 0,
                                    "failed_requests": 25,
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
        service = SuccessRateService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_team_success_rate_summary("2024-01-15", "2024-01-16")

        # Assert
        assert len(result) == 2

        # Find teams in result
        alpha_team = next(team for team in result if team["name"] == "Alpha Team")
        beta_team = next(team for team in result if team["name"] == "Beta Team")

        # Alpha Team: 0 successful out of 175 total = 0%
        assert alpha_team["total_requests"] == 175
        assert alpha_team["successful_requests"] == 0
        assert alpha_team["failed_requests"] == 175
        assert alpha_team["success_rate"] == 0.0

        # Beta Team: 0 successful out of 75 total = 0%
        assert beta_team["total_requests"] == 75
        assert beta_team["successful_requests"] == 0
        assert beta_team["failed_requests"] == 75
        assert beta_team["success_rate"] == 0.0

    def test_success_rate_with_empty_data(self):
        """Test with empty API response."""
        # Arrange
        mock_activity_data = {"results": []}
        mock_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_names={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = SuccessRateService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_team_success_rate_summary("2024-01-15", "2024-01-16")

        # Assert
        assert len(result) == 2
        assert mock_client.fetch_call_count == 1

        # All teams should have zero values
        for team in result:
            assert team["total_requests"] == 0
            assert team["successful_requests"] == 0
            assert team["failed_requests"] == 0
            assert team["success_rate"] == 0.0

    def test_success_rate_with_missing_team_data(self):
        """Test when some teams have no data."""
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
                                    "api_requests": 100,
                                    "successful_requests": 95,
                                    "failed_requests": 5,
                                }
                            }
                            # team2 has no data
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
        service = SuccessRateService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_team_success_rate_summary("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 2

        # Find teams in result
        alpha_team = next(team for team in result if team["name"] == "Alpha Team")
        beta_team = next(team for team in result if team["name"] == "Beta Team")

        # Alpha Team has data
        assert alpha_team["total_requests"] == 100
        assert alpha_team["successful_requests"] == 95
        assert alpha_team["failed_requests"] == 5
        assert alpha_team["success_rate"] == 95.0

        # Beta Team has no data (defaults to 0)
        assert beta_team["total_requests"] == 0
        assert beta_team["successful_requests"] == 0
        assert beta_team["failed_requests"] == 0
        assert beta_team["success_rate"] == 0.0

    def test_success_rate_with_missing_metrics(self):
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
                                    # All metrics missing
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "api_requests": 100,
                                    # successful_requests and failed_requests missing
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
        service = SuccessRateService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_team_success_rate_summary("2024-01-15", "2024-01-15")

        # Assert
        assert len(result) == 2

        # Find teams in result
        alpha_team = next(team for team in result if team["name"] == "Alpha Team")
        beta_team = next(team for team in result if team["name"] == "Beta Team")

        # Alpha Team: All metrics default to 0
        assert alpha_team["total_requests"] == 0
        assert alpha_team["successful_requests"] == 0
        assert alpha_team["failed_requests"] == 0
        assert alpha_team["success_rate"] == 0.0

        # Beta Team: Missing metrics default to 0
        assert beta_team["total_requests"] == 100
        assert beta_team["successful_requests"] == 0
        assert beta_team["failed_requests"] == 0
        assert beta_team["success_rate"] == 0.0

    def test_success_rate_api_error_handling(self):
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
        service = SuccessRateService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            service.fetch_team_success_rate_summary("2024-01-15", "2024-01-16")

        assert "Error fetching team token usage: Connection timeout" in str(
            exc_info.value
        )

    def test_success_rate_aggregation_across_multiple_days(self):
        """Test that success rates are correctly aggregated across multiple days."""
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
                                    "api_requests": 100,
                                    "successful_requests": 90,
                                    "failed_requests": 10,
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
                                    "api_requests": 200,
                                    "successful_requests": 190,
                                    "failed_requests": 10,
                                }
                            }
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
                                    "api_requests": 300,
                                    "successful_requests": 270,
                                    "failed_requests": 30,
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
        service = SuccessRateService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_team_success_rate_summary("2024-01-15", "2024-01-17")

        # Assert
        assert len(result) == 1
        alpha_team = result[0]

        # Total: 600 requests, 550 successful, 50 failed = 91.67%
        assert alpha_team["name"] == "Alpha Team"
        assert alpha_team["total_requests"] == 600
        assert alpha_team["successful_requests"] == 550
        assert alpha_team["failed_requests"] == 50
        assert alpha_team["success_rate"] == 91.67

    def test_success_rate_rounding(self):
        """Test that success rates are rounded to 2 decimal places."""
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
                                    "api_requests": 3,
                                    "successful_requests": 2,
                                    "failed_requests": 1,
                                }
                            },
                            "team2": {
                                "metrics": {
                                    "api_requests": 7,
                                    "successful_requests": 5,
                                    "failed_requests": 2,
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
        service = SuccessRateService(mock_client, mock_team_service)  # type: ignore[arg-type]

        # Act
        result = service.fetch_team_success_rate_summary("2024-01-15", "2024-01-15")

        # Assert
        alpha_team = next(team for team in result if team["name"] == "Alpha Team")
        beta_team = next(team for team in result if team["name"] == "Beta Team")

        # Alpha Team: 2/3 = 66.666...% should round to 66.67%
        assert alpha_team["success_rate"] == 66.67

        # Beta Team: 5/7 = 71.428...% should round to 71.43%
        assert beta_team["success_rate"] == 71.43
