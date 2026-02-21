"""Integration test for ModelUsageService end-to-end behavior."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from datetime import date

from src.api.server import create_backend
from src.utils.dependency_config import (
    get_team_daily_activity_service,
)
from src.client.models import (
    SpendMetrics,
    BreakdownMetrics,
    MetricWithMetadata,
    DailySpendData,
    SpendAnalyticsPaginatedResponse,
)


@pytest.fixture
def app():
    """Create FastAPI application for testing."""
    return create_backend()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_activity_service():
    """Create mock team daily activity service."""
    mock = Mock()

    mock.fetch_daily_activity.return_value = SpendAnalyticsPaginatedResponse(
        results=[
            DailySpendData(
                date=date(2024, 1, 15),
                metrics=SpendMetrics(total_tokens=268000),
                breakdown=BreakdownMetrics(
                    models={
                        "openai/gpt-4.1": MetricWithMetadata(
                            metrics=SpendMetrics(total_tokens=125000)
                        ),
                        "anthropic/claude-4.6-opus": MetricWithMetadata(
                            metrics=SpendMetrics(total_tokens=98000)
                        ),
                        "openai/gpt-5.2-codex": MetricWithMetadata(
                            metrics=SpendMetrics(total_tokens=45000)
                        ),
                    }
                ),
            )
        ]
    ).model_dump(mode="json")

    return mock


class TestModelUsageEndpointIntegration:
    """Integration test for /tokens/models endpoint."""

    def test_happy_path_returns_aggregated_model_usage(
        self, client, app, mock_activity_service
    ):
        """
        Test /tokens/models endpoint returns aggregated model usage sorted by tokens.

        This test verifies the complete end-to-end flow:
        1. Frontend calls GET /tokens/models with date range
        2. Backend aggregates token usage per model across all teams
        3. Response contains models sorted by token count (descending)
        """
        ### GIVEN
        app.dependency_overrides[get_team_daily_activity_service] = lambda: (
            mock_activity_service
        )

        ### WHEN
        response = client.get(
            "/tokens/models?start_date=2024-01-01&end_date=2024-01-31"
        )

        ### THEN
        assert response.status_code == 200
        data = response.json()

        assert "models" in data
        assert len(data["models"]) == 3

        models = data["models"]
        assert models[0]["model"] == "GPT-4.1"
        assert models[0]["tokens"] == 125000
        assert models[1]["model"] == "Claude 4.6 Opus"
        assert models[1]["tokens"] == 98000
        assert models[2]["model"] == "GPT-5.2 Codex"
        assert models[2]["tokens"] == 45000

        # Clean up
        app.dependency_overrides.clear()
