"""Integration tests for /tokens/cost-efficiency endpoint."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from datetime import datetime, timedelta, timezone

from src.api.server import create_backend
from src.utils.dependency_config import get_api_client
from src.client.models import TeamResponse, SpendAnalyticsPaginatedResponse


@pytest.fixture
def app():
    """Create FastAPI application for testing."""
    return create_backend()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_api_client():
    """Create mock API client with realistic cost efficiency data."""
    mock = Mock()

    # Mock teams data - return Pydantic models
    mock.fetch_teams.return_value = [
        TeamResponse.model_validate({"team_id": "team1", "team_alias": "Alpha Team"}),
        TeamResponse.model_validate({"team_id": "team2", "team_alias": "Beta Team"}),
    ]

    # Mock activity data with cost and token metrics - return Pydantic model
    activity_data = {
        "results": [
            {
                "date": "2024-01-15",
                "metrics": {
                    "total_tokens": 30000,
                    "spend": 1.10,
                },
                "breakdown": {
                    "entities": {
                        "team1": {
                            "metrics": {},
                            "api_key_breakdown": {
                                "key1": {"metrics": {}},
                            },
                        },
                        "team2": {
                            "metrics": {},
                            "api_key_breakdown": {
                                "key2": {"metrics": {}},
                            },
                        },
                    },
                    "model_groups": {
                        "gpt-4": {
                            "metrics": {"total_tokens": 10000, "spend": 0.30},
                            "api_key_breakdown": {
                                "key1": {
                                    "metrics": {"total_tokens": 10000, "spend": 0.30}
                                }
                            },
                        },
                        "claude-3-opus": {
                            "metrics": {"total_tokens": 20000, "spend": 0.80},
                            "api_key_breakdown": {
                                "key2": {
                                    "metrics": {"total_tokens": 20000, "spend": 0.80}
                                }
                            },
                        },
                    },
                },
            }
        ]
    }
    mock.fetch_team_daily_activity.return_value = (
        SpendAnalyticsPaginatedResponse.model_validate(activity_data)
    )

    return mock


class TestCostEfficiencyEndpointIntegration:
    """Integration tests for /tokens/cost-efficiency endpoint."""

    def test_success_with_valid_date_range(self, client, app, mock_api_client):
        """Test /tokens/cost-efficiency endpoint with valid date range."""
        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/cost-efficiency?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "cells" in data
        assert isinstance(data["cells"], list)
        assert len(data["cells"]) == 2

        # Verify cell data
        cells_by_team_model = {
            (cell["team"], cell["model"]): cell for cell in data["cells"]
        }

        # Alpha Team with GPT-4: 10000 tokens, $0.30 cost
        # Cost per 1k = (0.30 / 10000) * 1000 = 0.03
        alpha_gpt4 = cells_by_team_model.get(("Alpha Team", "gpt-4"))
        assert alpha_gpt4 is not None
        assert alpha_gpt4["total_tokens"] == 10000
        assert alpha_gpt4["total_cost"] == 0.30
        assert alpha_gpt4["cost_per_1k_tokens"] == 0.03

        # Beta Team with Claude 3 Opus: 20000 tokens, $0.80 cost
        # Cost per 1k = (0.80 / 20000) * 1000 = 0.04
        beta_claude = cells_by_team_model.get(("Beta Team", "claude-3-opus"))
        assert beta_claude is not None
        assert beta_claude["total_tokens"] == 20000
        assert beta_claude["total_cost"] == 0.80
        assert beta_claude["cost_per_1k_tokens"] == 0.04

        # Clean up
        app.dependency_overrides.clear()

    def test_invalid_date_format_returns_400(self, client):
        """Test /tokens/cost-efficiency endpoint with invalid date format returns HTTP 400."""
        # Test various invalid formats
        invalid_formats = [
            "2024/01/01",  # Wrong separator
            "01-01-2024",  # Wrong order
            "not-a-date",  # Completely invalid
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
        ]

        for invalid_date in invalid_formats:
            response = client.get(f"/tokens/cost-efficiency?start_date={invalid_date}")
            assert response.status_code == 400, f"Failed for date: {invalid_date}"
            assert "detail" in response.json()
            assert "Date must be in YYYY-MM-DD format" in response.json()["detail"]

    def test_future_date_returns_400(self, client):
        """Test /tokens/cost-efficiency endpoint with future dates returns HTTP 400."""
        # Calculate future date
        future_date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )

        # Test future start_date
        response = client.get(f"/tokens/cost-efficiency?start_date={future_date}")
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "cannot be in the future" in response.json()["detail"]

        # Test future end_date
        response = client.get(f"/tokens/cost-efficiency?end_date={future_date}")
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "cannot be in the future" in response.json()["detail"]

    def test_external_api_failure_returns_502(self, client, app, mock_api_client):
        """Test /tokens/cost-efficiency endpoint when external API fails returns HTTP 502."""
        # Configure mock to raise RuntimeError
        mock_api_client.fetch_team_daily_activity.side_effect = RuntimeError(
            "External API error: Connection timeout"
        )

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/cost-efficiency?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 502
        assert "detail" in response.json()

        # Clean up
        app.dependency_overrides.clear()

    def test_unexpected_error_returns_500(self, client, app, mock_api_client):
        """Test /tokens/cost-efficiency endpoint when unexpected error occurs returns HTTP 500."""
        # Configure mock to raise unexpected exception
        mock_api_client.fetch_team_daily_activity.side_effect = ValueError(
            "Unexpected internal error"
        )

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/cost-efficiency?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 500
        assert "detail" in response.json()
        assert "Unexpected error" in response.json()["detail"]

        # Clean up
        app.dependency_overrides.clear()

    def test_zero_tokens_edge_case(self, client, app, mock_api_client):
        """Test /tokens/cost-efficiency endpoint with zero tokens (edge case)."""
        # Configure mock to return zero tokens
        mock_api_client.fetch_team_daily_activity.return_value = (
            SpendAnalyticsPaginatedResponse.model_validate(
                {
                    "results": [
                        {
                            "date": "2024-01-15",
                            "metrics": {
                                "total_tokens": 0,
                                "spend": 0.0,
                            },  # Required field
                            "breakdown": {
                                "entities": {
                                    "team1": {
                                        "metrics": {},
                                        "api_key_breakdown": {
                                            "key1": {"metrics": {}},
                                        },
                                    }
                                },
                                "model_groups": {
                                    "gpt-4": {
                                        "metrics": {},
                                        "api_key_breakdown": {
                                            "key1": {
                                                "metrics": {
                                                    "total_tokens": 0,
                                                    "spend": 0.0,
                                                }
                                            }
                                        },
                                    }
                                },
                            },
                        }
                    ]
                }
            )
        )

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/cost-efficiency?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify cells with zero tokens have cost_per_1k_tokens = 0.0
        assert "cells" in data
        for cell in data["cells"]:
            if cell["total_tokens"] == 0:
                assert cell["cost_per_1k_tokens"] == 0.0
                assert cell["total_cost"] == 0.0

        # Clean up
        app.dependency_overrides.clear()

    def test_default_date_range_behavior(self, client, app, mock_api_client):
        """Test /tokens/cost-efficiency endpoint with omitted date parameters uses default date range."""
        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Capture the current time before making the request
        before_request = datetime.now(timezone.utc)

        # Make request without date parameters
        response = client.get("/tokens/cost-efficiency")

        # Capture time after request
        after_request = datetime.now(timezone.utc)

        # Assert response is successful
        assert response.status_code == 200
        data = response.json()
        assert "cells" in data

        # Verify the API client was called
        assert mock_api_client.fetch_team_daily_activity.called

        # Get the call arguments
        call_args = mock_api_client.fetch_team_daily_activity.call_args
        args, kwargs = call_args

        # Arguments are: team_ids, start_date, end_date
        start_date_arg = args[1]
        end_date_arg = args[2]

        # Parse the dates from the API call
        start_dt = datetime.strptime(start_date_arg, "%Y.%m.%d").replace(
            tzinfo=timezone.utc
        )
        end_dt = datetime.fromisoformat(end_date_arg.replace("Z", "+00:00"))

        # Verify end_date is approximately now (within the request window)
        assert before_request <= end_dt <= after_request + timedelta(seconds=1), (
            f"Expected end_date to be between {before_request} and {after_request}, got {end_dt}"
        )

        # Verify start_date is approximately 24 hours before end_date
        expected_start_date = (end_dt - timedelta(days=1)).date()
        actual_start_date = start_dt.date()
        assert actual_start_date == expected_start_date, (
            f"Expected start_date to be {expected_start_date}, got {actual_start_date}"
        )

        # Clean up
        app.dependency_overrides.clear()

    def test_end_date_before_start_date_returns_400(self, client):
        """Test /tokens/cost-efficiency endpoint with end_date before start_date returns HTTP 400."""
        response = client.get(
            "/tokens/cost-efficiency?start_date=2024-01-31&end_date=2024-01-01"
        )
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "must not be before" in response.json()["detail"]

    def test_response_schema_structure(self, client, app, mock_api_client):
        """Test /tokens/cost-efficiency endpoint response has correct schema structure."""
        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/cost-efficiency?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify top-level structure
        assert "cells" in data
        assert isinstance(data["cells"], list)

        # Verify cell structure
        for cell in data["cells"]:
            assert "team" in cell
            assert "model" in cell
            assert "cost_per_1k_tokens" in cell
            assert "total_cost" in cell
            assert "total_tokens" in cell

            assert isinstance(cell["team"], str)
            assert isinstance(cell["model"], str)
            assert isinstance(cell["cost_per_1k_tokens"], (int, float))
            assert isinstance(cell["total_cost"], (int, float))
            assert isinstance(cell["total_tokens"], int)

        # Clean up
        app.dependency_overrides.clear()

    def test_empty_data_scenario(self, client, app, mock_api_client):
        """Test /tokens/cost-efficiency endpoint with empty data from API."""
        # Configure mock to return empty results
        mock_api_client.fetch_team_daily_activity.return_value = (
            SpendAnalyticsPaginatedResponse.model_validate({"results": []})
        )

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/cost-efficiency?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert "cells" in data
        assert len(data["cells"]) == 0  # No cells when no data

        # Clean up
        app.dependency_overrides.clear()

    def test_rounding_to_four_decimal_places(self, client, app, mock_api_client):
        """Test /tokens/cost-efficiency endpoint rounds cost values to 4 decimal places."""
        # Configure mock with values that require rounding
        mock_api_client.fetch_team_daily_activity.return_value = (
            SpendAnalyticsPaginatedResponse.model_validate(
                {
                    "results": [
                        {
                            "date": "2024-01-15",
                            "metrics": {
                                "total_tokens": 7777,
                                "spend": 0.123456789,
                            },  # Required field
                            "breakdown": {
                                "entities": {
                                    "team1": {
                                        "metrics": {},
                                        "api_key_breakdown": {
                                            "key1": {"metrics": {}},
                                        },
                                    }
                                },
                                "model_groups": {
                                    "gpt-4": {
                                        "metrics": {},
                                        "api_key_breakdown": {
                                            "key1": {
                                                "metrics": {
                                                    "total_tokens": 7777,
                                                    "spend": 0.123456789,
                                                }
                                            }
                                        },
                                    }
                                },
                            },
                        }
                    ]
                }
            )
        )

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/cost-efficiency?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify rounding
        for cell in data["cells"]:
            # Check that cost values have at most 4 decimal places
            cost_per_1k_str = str(cell["cost_per_1k_tokens"])
            total_cost_str = str(cell["total_cost"])

            if "." in cost_per_1k_str:
                decimals = len(cost_per_1k_str.split(".")[1])
                assert decimals <= 4, (
                    f"cost_per_1k_tokens has {decimals} decimals, expected <= 4"
                )

            if "." in total_cost_str:
                decimals = len(total_cost_str.split(".")[1])
                assert decimals <= 4, (
                    f"total_cost has {decimals} decimals, expected <= 4"
                )

        # Clean up
        app.dependency_overrides.clear()
