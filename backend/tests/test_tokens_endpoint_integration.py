"""Integration tests for /tokens endpoint."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from datetime import datetime, timedelta, timezone

from src.api.server import create_backend
from src.utils.dependency_config import get_api_client
from src.client.models import TeamResponse


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
    """Create mock API client with realistic data."""
    mock = Mock()

    # Mock teams data - return Pydantic models
    mock.fetch_teams.return_value = [
        TeamResponse.model_validate({"team_id": "team1", "team_alias": "Alpha Team"}),
        TeamResponse.model_validate({"team_id": "team2", "team_alias": "Beta Team"}),
    ]

    # Mock activity data with breakdown structure - return dict (not Pydantic model)
    # The service expects to call model_dump() on the response, so we need to mock that
    activity_data = {
        "results": [
            {
                "date": "2024-01-15",
                "metrics": {
                    "total_tokens": 3000,
                    "prompt_tokens": 1800,
                    "completion_tokens": 1200,
                },
                "breakdown": {
                    "entities": {
                        "team1": {
                            "metrics": {
                                "total_tokens": 1000,
                                "prompt_tokens": 600,
                                "completion_tokens": 400,
                            },
                            "api_key_breakdown": {
                                "key1": {"metrics": {}},
                            },
                        },
                        "team2": {
                            "metrics": {
                                "total_tokens": 2000,
                                "prompt_tokens": 1200,
                                "completion_tokens": 800,
                            },
                            "api_key_breakdown": {
                                "key2": {"metrics": {}},
                            },
                        },
                    },
                    "models": {
                        "openai/gpt-4": {
                            "metrics": {
                                "total_tokens": 1000,
                                "prompt_tokens": 600,
                                "completion_tokens": 400,
                            },
                            "api_key_breakdown": {
                                "key1": {
                                    "metrics": {
                                        "total_tokens": 1000,
                                        "prompt_tokens": 600,
                                        "completion_tokens": 400,
                                    }
                                }
                            },
                        },
                        "anthropic/claude-3": {
                            "metrics": {
                                "total_tokens": 2000,
                                "prompt_tokens": 1200,
                                "completion_tokens": 800,
                            },
                            "api_key_breakdown": {
                                "key2": {
                                    "metrics": {
                                        "total_tokens": 2000,
                                        "prompt_tokens": 1200,
                                        "completion_tokens": 800,
                                    }
                                }
                            },
                        },
                    },
                    "api_keys": {
                        "key1": {"metadata": {"key_alias": "DevBoost Key 1"}},
                        "key2": {"metadata": {"key_alias": "DevBoost Key 2"}},
                    },
                },
            }
        ]
    }

    # Create a mock response object that has model_dump method
    mock_response = Mock()
    mock_response.model_dump.return_value = activity_data
    mock.fetch_team_daily_activity.return_value = mock_response

    return mock


class TestTokensEndpointIntegration:
    """Integration tests for /tokens endpoint."""

    def test_success_with_valid_date_range(self, client, app, mock_api_client):
        """Test /tokens endpoint with valid date range."""
        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get("/tokens?start_date=2024-01-01&end_date=2024-01-31")

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

        # Verify tokens
        alpha_team = next(t for t in data["teams"] if t["name"] == "Alpha Team")
        beta_team = next(t for t in data["teams"] if t["name"] == "Beta Team")
        assert alpha_team["tokens"] == 1000
        assert beta_team["tokens"] == 2000

        # Verify breakdown structure exists
        assert "breakdown" in alpha_team
        assert "api_keys" in alpha_team["breakdown"]

        # Clean up
        app.dependency_overrides.clear()

    def test_invalid_date_format_returns_400(self, client):
        """Test /tokens endpoint with invalid date format returns HTTP 400."""
        # Test various invalid formats
        invalid_formats = [
            "2024/01/01",  # Wrong separator
            "01-01-2024",  # Wrong order
            "not-a-date",  # Completely invalid
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
        ]

        for invalid_date in invalid_formats:
            response = client.get(f"/tokens?start_date={invalid_date}")
            assert response.status_code == 400, f"Failed for date: {invalid_date}"
            assert "detail" in response.json()
            assert "Date must be in YYYY-MM-DD format" in response.json()["detail"]

    def test_future_date_returns_400(self, client):
        """Test /tokens endpoint with future dates returns HTTP 400."""
        # Calculate future date
        future_date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )

        # Test future start_date
        response = client.get(f"/tokens?start_date={future_date}")
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "cannot be in the future" in response.json()["detail"]

        # Test future end_date
        response = client.get(f"/tokens?end_date={future_date}")
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "cannot be in the future" in response.json()["detail"]

    def test_external_api_failure_returns_502(self, client, app, mock_api_client):
        """Test /tokens endpoint when external API fails returns HTTP 502."""
        # Configure mock to raise RuntimeError
        mock_api_client.fetch_team_daily_activity.side_effect = RuntimeError(
            "External API error: Connection timeout"
        )

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get("/tokens?start_date=2024-01-01&end_date=2024-01-31")

        # Assert response
        assert response.status_code == 502
        assert "detail" in response.json()
        assert "Error fetching team token usage" in response.json()["detail"]

        # Clean up
        app.dependency_overrides.clear()

    def test_default_date_range_behavior(self, client, app, mock_api_client):
        """
        Test /tokens endpoint with omitted date parameters uses default date range.

        Property 1: Default date range behavior
        When both start_date and end_date are omitted, the system should default
        to the last 24 hours (current time minus 24 hours to current time).

        Validates: Requirements 4.6
        """
        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Capture the current time before making the request
        before_request = datetime.now(timezone.utc)

        # Make request without date parameters
        response = client.get("/tokens")

        # Capture time after request
        after_request = datetime.now(timezone.utc)

        # Assert response is successful
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data

        # Verify the API client was called
        assert mock_api_client.fetch_team_daily_activity.called

        # Get the call arguments - they are positional
        call_args = mock_api_client.fetch_team_daily_activity.call_args
        args, kwargs = call_args

        # Arguments are: team_ids, start_date, end_date
        start_date_arg = args[1]
        end_date_arg = args[2]

        # Parse the dates from the API call
        # start_date format: YYYY.MM.DD (only date, no time)
        # end_date format: ISO format (includes time)
        start_dt = datetime.strptime(start_date_arg, "%Y.%m.%d").replace(
            tzinfo=timezone.utc
        )
        end_dt = datetime.fromisoformat(end_date_arg.replace("Z", "+00:00"))

        # Verify end_date is approximately now (within the request window)
        assert before_request <= end_dt <= after_request + timedelta(seconds=1), (
            f"Expected end_date to be between {before_request} and {after_request}, got {end_dt}"
        )

        # Verify start_date is approximately 24 hours before end_date
        # Since start_date only has date precision (no time), we check it's the right day
        expected_start_date = (end_dt - timedelta(days=1)).date()
        actual_start_date = start_dt.date()
        assert actual_start_date == expected_start_date, (
            f"Expected start_date to be {expected_start_date}, got {actual_start_date}"
        )

        # Clean up
        app.dependency_overrides.clear()

    def test_end_date_before_start_date_returns_400(self, client):
        """Test /tokens endpoint with end_date before start_date returns HTTP 400."""
        response = client.get("/tokens?start_date=2024-01-31&end_date=2024-01-01")
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "must not be before" in response.json()["detail"]

    def test_response_schema_structure(self, client, app, mock_api_client):
        """Test /tokens endpoint response has correct schema structure."""
        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get("/tokens?start_date=2024-01-01&end_date=2024-01-31")

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify top-level structure
        assert "teams" in data
        assert isinstance(data["teams"], list)

        # Verify team structure
        for team in data["teams"]:
            assert "name" in team
            assert "tokens" in team
            assert isinstance(team["name"], str)
            assert isinstance(team["tokens"], int)

            # Verify breakdown structure if present
            if "breakdown" in team:
                assert "api_keys" in team["breakdown"]
                assert isinstance(team["breakdown"]["api_keys"], list)

                for api_key in team["breakdown"]["api_keys"]:
                    assert "api_key" in api_key
                    assert "models" in api_key
                    assert isinstance(api_key["models"], list)

                    for model in api_key["models"]:
                        assert "model_name" in model
                        assert "total_tokens" in model
                        assert "prompt_tokens" in model
                        assert "completion_tokens" in model

        # Clean up
        app.dependency_overrides.clear()

    def test_empty_data_scenario(self, client, app, mock_api_client):
        """Test /tokens endpoint with empty data from API."""
        # Configure mock to return empty results
        mock_response = Mock()
        mock_response.model_dump.return_value = {"results": []}
        mock_api_client.fetch_team_daily_activity.return_value = mock_response

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get("/tokens?start_date=2024-01-01&end_date=2024-01-31")

        # Assert response
        assert response.status_code == 200
        data = response.json()
        assert "teams" in data
        assert len(data["teams"]) == 2  # Teams exist but with zero tokens

        # Verify all teams have zero tokens
        for team in data["teams"]:
            assert team["tokens"] == 0

        # Clean up
        app.dependency_overrides.clear()

    def test_unexpected_error_returns_500(self, client, app, mock_api_client):
        """Test /tokens endpoint when unexpected error occurs returns HTTP 500."""
        # Configure mock to raise unexpected exception
        mock_api_client.fetch_team_daily_activity.side_effect = ValueError(
            "Unexpected internal error"
        )

        # Override dependency
        app.dependency_overrides[get_api_client] = lambda: mock_api_client

        # Make request
        response = client.get("/tokens?start_date=2024-01-01&end_date=2024-01-31")

        # Assert response
        assert response.status_code == 500
        assert "detail" in response.json()
        assert "Unexpected error" in response.json()["detail"]

        # Clean up
        app.dependency_overrides.clear()
