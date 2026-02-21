"""Integration tests for /tokens/success-rate endpoint."""

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
    """Create mock API client with realistic success rate data."""
    mock = Mock()

    # Mock teams data - return Pydantic models
    mock.fetch_teams.return_value = [
        TeamResponse.model_validate({"team_id": "team1", "team_alias": "Alpha Team"}),
        TeamResponse.model_validate({"team_id": "team2", "team_alias": "Beta Team"}),
    ]

    # Mock activity data with request metrics - return Pydantic model
    activity_data = {
        "results": [
            {
                "date": "2024-01-15",
                "metrics": {
                    "api_requests": 300,
                    "successful_requests": 275,
                    "failed_requests": 25,
                },
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
                    }
                },
            },
            {
                "date": "2024-01-16",
                "metrics": {
                    "api_requests": 400,
                    "successful_requests": 370,
                    "failed_requests": 30,
                },
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
                                "api_requests": 250,
                                "successful_requests": 230,
                                "failed_requests": 20,
                            }
                        },
                    }
                },
            },
        ]
    }
    mock.fetch_team_daily_activity.return_value = (
        SpendAnalyticsPaginatedResponse.model_validate(activity_data)
    )

    # Mock model name map (not used by success rate but needed for service initialization)
    mock.get_model_name_map.return_value = {}

    return mock


class TestSuccessRateEndpointIntegration:
    """Integration tests for /tokens/success-rate endpoint."""

    def test_success_with_valid_date_range(self, client, app, mock_api_client):
        """Test /tokens/success-rate endpoint with valid date range."""
        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/success-rate?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "teams" in data
        assert isinstance(data["teams"], list)
        assert len(data["teams"]) == 2

        # Verify team data
        team_names = {team["name"] for team in data["teams"]}
        assert team_names == {"Alpha Team", "Beta Team"}

        # Verify success rate calculations
        alpha_team = next(t for t in data["teams"] if t["name"] == "Alpha Team")
        beta_team = next(t for t in data["teams"] if t["name"] == "Beta Team")

        # Alpha Team: 100 + 150 = 250 total, 95 + 140 = 235 successful
        assert alpha_team["total_requests"] == 250
        assert alpha_team["successful_requests"] == 235
        assert alpha_team["failed_requests"] == 15
        assert alpha_team["success_rate"] == 94.0  # 235/250 * 100 = 94.0

        # Beta Team: 200 + 250 = 450 total, 180 + 230 = 410 successful
        assert beta_team["total_requests"] == 450
        assert beta_team["successful_requests"] == 410
        assert beta_team["failed_requests"] == 40
        assert (
            beta_team["success_rate"] == 91.11
        )  # 410/450 * 100 = 91.11 (rounded to 2 decimals)

        # Clean up
        app.dependency_overrides.clear()

    def test_invalid_date_format_returns_400(self, client):
        """Test /tokens/success-rate endpoint with invalid date format returns HTTP 400."""
        # Test various invalid formats
        invalid_formats = [
            "2024/01/01",  # Wrong separator
            "01-01-2024",  # Wrong order
            "not-a-date",  # Completely invalid
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
        ]

        for invalid_date in invalid_formats:
            response = client.get(f"/tokens/success-rate?start_date={invalid_date}")
            assert response.status_code == 400, f"Failed for date: {invalid_date}"
            assert "detail" in response.json()
            assert "Date must be in YYYY-MM-DD format" in response.json()["detail"]

    def test_future_date_returns_400(self, client):
        """Test /tokens/success-rate endpoint with future dates returns HTTP 400."""
        # Calculate future date
        future_date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )

        # Test future start_date
        response = client.get(f"/tokens/success-rate?start_date={future_date}")
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "cannot be in the future" in response.json()["detail"]

        # Test future end_date
        response = client.get(f"/tokens/success-rate?end_date={future_date}")
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "cannot be in the future" in response.json()["detail"]

    def test_external_api_failure_returns_502(self, client, app, mock_api_client):
        """Test /tokens/success-rate endpoint when external API fails returns HTTP 502."""
        # Configure mock to raise RuntimeError
        mock_api_client.fetch_team_daily_activity.side_effect = RuntimeError(
            "External API error: Connection timeout"
        )

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/success-rate?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 502
        assert "detail" in response.json()

        # Clean up
        app.dependency_overrides.clear()

    def test_unexpected_error_returns_500(self, client, app, mock_api_client):
        """Test /tokens/success-rate endpoint when unexpected error occurs returns HTTP 500."""
        # Configure mock to raise unexpected exception
        mock_api_client.fetch_team_daily_activity.side_effect = ValueError(
            "Unexpected internal error"
        )

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/success-rate?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 500
        assert "detail" in response.json()
        assert "Unexpected error" in response.json()["detail"]

        # Clean up
        app.dependency_overrides.clear()

    def test_zero_requests_edge_case(self, client, app, mock_api_client):
        """Test /tokens/success-rate endpoint with zero requests (edge case)."""
        # Configure mock to return zero requests
        mock_api_client.fetch_team_daily_activity.return_value = (
            SpendAnalyticsPaginatedResponse.model_validate(
                {
                    "results": [
                        {
                            "date": "2024-01-15",
                            "metrics": {
                                "api_requests": 0,
                                "successful_requests": 0,
                                "failed_requests": 0,
                            },  # Required field
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
                                            "api_requests": 0,
                                            "successful_requests": 0,
                                            "failed_requests": 0,
                                        }
                                    },
                                }
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
            "/tokens/success-rate?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify all teams have zero requests and 0.0 success rate
        for team in data["teams"]:
            assert team["total_requests"] == 0
            assert team["successful_requests"] == 0
            assert team["failed_requests"] == 0
            assert team["success_rate"] == 0.0

        # Clean up
        app.dependency_overrides.clear()

    def test_default_date_range_behavior(self, client, app, mock_api_client):
        """Test /tokens/success-rate endpoint with omitted date parameters uses default date range."""
        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Capture the current time before making the request
        before_request = datetime.now(timezone.utc)

        # Make request without date parameters
        response = client.get("/tokens/success-rate")

        # Capture time after request
        after_request = datetime.now(timezone.utc)

        # Assert response is successful
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data

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
        """Test /tokens/success-rate endpoint with end_date before start_date returns HTTP 400."""
        response = client.get(
            "/tokens/success-rate?start_date=2024-01-31&end_date=2024-01-01"
        )
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "must not be before" in response.json()["detail"]

    def test_response_schema_structure(self, client, app, mock_api_client):
        """Test /tokens/success-rate endpoint response has correct schema structure."""
        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/success-rate?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify top-level structure
        assert "teams" in data
        assert isinstance(data["teams"], list)

        # Verify team structure
        for team in data["teams"]:
            assert "name" in team
            assert "total_requests" in team
            assert "successful_requests" in team
            assert "failed_requests" in team
            assert "success_rate" in team

            assert isinstance(team["name"], str)
            assert isinstance(team["total_requests"], int)
            assert isinstance(team["successful_requests"], int)
            assert isinstance(team["failed_requests"], int)
            assert isinstance(team["success_rate"], (int, float))

        # Clean up
        app.dependency_overrides.clear()

    def test_empty_data_scenario(self, client, app, mock_api_client):
        """Test /tokens/success-rate endpoint with empty data from API."""
        # Configure mock to return empty results
        mock_api_client.fetch_team_daily_activity.return_value = (
            SpendAnalyticsPaginatedResponse.model_validate({"results": []})
        )

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get(
            "/tokens/success-rate?start_date=2024-01-01&end_date=2024-01-31"
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert len(data["teams"]) == 2  # Teams exist but with zero requests

        # Verify all teams have zero requests
        for team in data["teams"]:
            assert team["total_requests"] == 0
            assert team["successful_requests"] == 0
            assert team["failed_requests"] == 0
            assert team["success_rate"] == 0.0

        # Clean up
        app.dependency_overrides.clear()
