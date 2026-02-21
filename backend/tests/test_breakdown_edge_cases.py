"""Edge case tests for team model breakdown functionality."""

import pytest
from typing import Any
from unittest.mock import Mock
from src.services.token_aggregation_service import TokenAggregationService


class TestBreakdownEdgeCases:
    """Test edge cases for breakdown data handling."""

    @pytest.fixture
    def service(self):
        """Create a TokenAggregationService instance with mocked dependencies."""
        mock_api_client = Mock()
        mock_team_service = Mock()
        return TokenAggregationService(
            api_client=mock_api_client,
            team_service=mock_team_service,
        )

    def test_empty_breakdown_structure(self, service):
        """
        Test that empty breakdown structure is handled gracefully.
        Edge case for Requirement 2.5: When no breakdown data exists for a team,
        the backend shall return an empty breakdown structure.
        """
        # Entity with no api_key_breakdown field
        entity_no_breakdown = {
            "metrics": {
                "total_tokens": 1000,
                "prompt_tokens": 600,
                "completion_tokens": 400,
            }
        }

        # Empty top-level breakdown
        top_level_breakdown = {}

        result = service._extract_breakdown(entity_no_breakdown, top_level_breakdown)

        # Should return empty structure, not None or error
        assert result is not None
        assert "api_keys" in result
        assert isinstance(result["api_keys"], list)
        assert len(result["api_keys"]) == 0

    def test_empty_top_level_breakdown(self, service):
        """
        Test that empty top-level breakdown is handled.
        Edge case for Requirement 2.5.
        """
        # Entity with empty structure
        entity_empty = {"metrics": {"total_tokens": 1000}}

        # Empty top-level breakdown
        top_level_breakdown = {"models": {}}

        result = service._extract_breakdown(entity_empty, top_level_breakdown)

        assert result is not None
        assert result["api_keys"] == []

    def test_zero_token_counts_display(self, service):
        """
        Test that zero token counts are preserved in breakdown.
        Edge case for Requirement 4.4: When token counts are zero,
        the frontend shall display "0" rather than hiding the entry.
        """
        # Entity data with api_key_breakdown
        entity = {
            "metrics": {"total_tokens": 0},
            "api_key_breakdown": {
                "hash123": {
                    "metrics": {
                        "total_tokens": 0,
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                    }
                }
            },
        }

        # Top-level breakdown with zero tokens
        top_level_breakdown = {
            "model_groups": {
                "gpt-4": {
                    "metrics": {"total_tokens": 0},
                    "api_key_breakdown": {
                        "hash123": {
                            "metrics": {
                                "total_tokens": 0,
                                "prompt_tokens": 0,
                                "completion_tokens": 0,
                            },
                            "metadata": {},
                        }
                    },
                }
            },
            "api_keys": {"hash123": {"metadata": {}}},
        }

        result = service._extract_breakdown(entity, top_level_breakdown)

        # Zero tokens should be preserved
        assert len(result["api_keys"]) == 1
        assert len(result["api_keys"][0]["models"]) == 1
        assert result["api_keys"][0]["models"][0]["total_tokens"] == 0
        assert result["api_keys"][0]["models"][0]["model_name"] == "gpt-4"

    def test_merge_breakdown_with_empty_target(self, service):
        """
        Test merging breakdown into empty target structure.
        Edge case for Requirement 6.4: Token aggregation across dates.
        """
        target = {"api_keys": []}
        source = {
            "api_keys": [
                {
                    "api_key": "sk-test789",
                    "models": [
                        {
                            "model_name": "gpt-4",
                            "total_tokens": 1000,
                            "prompt_tokens": 600,
                            "completion_tokens": 400,
                        }
                    ],
                }
            ]
        }

        service._merge_breakdown(target, source)

        # Source should be added to empty target
        assert len(target["api_keys"]) == 1
        assert target["api_keys"][0]["api_key"] == "sk-test789"
        assert target["api_keys"][0]["models"][0]["total_tokens"] == 1000

    def test_merge_breakdown_aggregates_same_model(self, service):
        """
        Test that merging aggregates tokens for same model+key combination.
        Edge case for Requirement 6.4: Token aggregation across dates.
        """
        target = {
            "api_keys": [
                {
                    "api_key": "sk-same",
                    "models": [
                        {
                            "model_name": "gpt-4",
                            "total_tokens": 1000,
                            "prompt_tokens": 600,
                            "completion_tokens": 400,
                        }
                    ],
                }
            ]
        }

        source = {
            "api_keys": [
                {
                    "api_key": "sk-same",
                    "models": [
                        {
                            "model_name": "gpt-4",
                            "total_tokens": 500,
                            "prompt_tokens": 300,
                            "completion_tokens": 200,
                        }
                    ],
                }
            ]
        }

        service._merge_breakdown(target, source)

        # Should aggregate tokens for same model+key
        assert len(target["api_keys"]) == 1
        assert len(target["api_keys"][0]["models"]) == 1
        model: Any = target["api_keys"][0]["models"][0]
        assert model["total_tokens"] == 1500  # type: ignore[invalid-argument-type]
        assert model["prompt_tokens"] == 900  # type: ignore[invalid-argument-type]
        assert model["completion_tokens"] == 600  # type: ignore[invalid-argument-type]

    def test_malformed_metrics_handling(self, service):
        """
        Test handling of malformed or missing metrics fields.
        Edge case for Requirement 2.5: Handle missing breakdown data gracefully.
        """
        # Entity data with api_key_breakdown
        entity = {"metrics": {}, "api_key_breakdown": {"hash456": {"metrics": {}}}}

        # Top-level breakdown with missing metrics
        top_level_breakdown = {
            "models": {
                "gpt-4": {
                    "metrics": {},  # Empty metrics
                    "api_key_breakdown": {
                        "hash456": {
                            "metrics": {},  # Empty model metrics
                            "metadata": {},
                        }
                    },
                }
            },
            "api_keys": {"hash456": {"metadata": {}}},
        }

        result = service._extract_breakdown(entity, top_level_breakdown)

        # Should handle gracefully with default 0 values
        assert len(result["api_keys"]) == 1
        assert len(result["api_keys"][0]["models"]) == 1
        assert result["api_keys"][0]["models"][0]["total_tokens"] == 0
        assert result["api_keys"][0]["models"][0]["prompt_tokens"] == 0
        assert result["api_keys"][0]["models"][0]["completion_tokens"] == 0
