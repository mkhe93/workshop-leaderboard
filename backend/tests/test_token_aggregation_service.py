"""Unit tests for TokenAggregationService."""

import pytest
from typing import List, Dict, Any
from src.services.token_aggregation_service import TokenAggregationService


class MockAPIClient:
    """Mock API client for testing TokenAggregationService."""

    def __init__(
        self,
        activity_data: Dict[str, Any],
        should_fail: bool = False,
    ):
        """Initialize mock with test data."""
        self._activity_data = activity_data
        self._should_fail = should_fail
        self.fetch_team_daily_activity_call_count = 0

    def fetch_teams(self) -> List[Dict[str, Any]]:
        """Mock fetch_teams method."""
        return []

    def fetch_team_daily_activity(
        self,
        team_ids: List[str],
        start_date: str,
        end_date: str,
        page_size: int = 20000,
    ) -> Dict[str, Any]:
        """Mock fetch_team_daily_activity method."""
        self.fetch_team_daily_activity_call_count += 1
        if self._should_fail:
            raise RuntimeError("External API error: Connection failed")
        return self._activity_data


class MockTeamService:
    """Mock team service for testing TokenAggregationService."""

    def __init__(self, team_ids: List[str], team_id_to_name: Dict[str, str]):
        """Initialize mock with test data."""
        self._team_ids = team_ids
        self._team_id_to_name = team_id_to_name

    def fetch_teams(self) -> List[Dict[str, Any]]:
        """Mock fetch_teams method."""
        return []

    def get_team_ids(self) -> List[str]:
        """Mock get_team_ids method."""
        return self._team_ids

    def get_team_name(self, team_id: str) -> str:
        """Mock get_team_name method."""
        return self._team_id_to_name.get(team_id, team_id)


class TestTokenAggregationService:
    """Test suite for TokenAggregationService."""

    def test_fetch_total_tokens_with_empty_data(self):
        """Test token aggregation with empty data."""
        # Arrange
        mock_activity_data = {"results": []}
        mock_api_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_id_to_name={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = TokenAggregationService(
            mock_api_client,
            mock_team_service, 
        )

        # Act
        result = service.fetch_total_tokens_per_team("2024-01-01", "2024-01-02")

        # Assert
        assert len(result) == 2
        assert result["Alpha Team"]["total_tokens"] == 0
        assert result["Beta Team"]["total_tokens"] == 0
        assert result["Alpha Team"]["breakdown"]["api_keys"] == []
        assert result["Beta Team"]["breakdown"]["api_keys"] == []

    def test_fetch_total_tokens_with_single_team(self):
        """Test token aggregation with single team."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-01",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 1000},
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                },
                            }
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "metrics": {"total_tokens": 1000},
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                },
                            }
                        },
                        "api_keys": {
                            "key1": {"metadata": {"key_alias": "DevBoost Key"}}
                        },
                    },
                }
            ]
        }
        mock_api_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"], team_id_to_name={"team1": "Alpha Team"}
        )
        service = TokenAggregationService(
            mock_api_client,
            mock_team_service, 
        )

        # Act
        result = service.fetch_total_tokens_per_team("2024-01-01", "2024-01-02")

        # Assert
        assert len(result) == 1
        assert result["Alpha Team"]["total_tokens"] == 1000
        assert len(result["Alpha Team"]["breakdown"]["api_keys"]) == 1
        api_key_data = result["Alpha Team"]["breakdown"]["api_keys"][0]
        assert api_key_data["api_key"] == "key1"
        assert api_key_data["key_alias"] == "DevBoost Key"
        assert len(api_key_data["models"]) == 1
        assert api_key_data["models"][0]["model_name"] == "openai/gpt-4"
        assert api_key_data["models"][0]["total_tokens"] == 1000

    def test_fetch_total_tokens_with_multiple_teams(self):
        """Test token aggregation with multiple teams."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-01",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 1000},
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
                            "team2": {
                                "metrics": {"total_tokens": 2000},
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
                        "model_groups": {
                            "openai/gpt-4": {
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                }
                            },
                            "anthropic/claude-3": {
                                "api_key_breakdown": {
                                    "key2": {
                                        "metrics": {
                                            "total_tokens": 2000,
                                            "prompt_tokens": 1200,
                                            "completion_tokens": 800,
                                        }
                                    }
                                }
                            },
                        },
                        "api_keys": {
                            "key1": {"metadata": {"key_alias": "Alpha Key"}},
                            "key2": {"metadata": {"key_alias": "Beta Key"}},
                        },
                    },
                }
            ]
        }
        mock_api_client = MockAPIClient(
            mock_activity_data,
        )
        mock_team_service = MockTeamService(
            team_ids=["team1", "team2"],
            team_id_to_name={"team1": "Alpha Team", "team2": "Beta Team"},
        )
        service = TokenAggregationService(
            mock_api_client,
            mock_team_service, 
        )

        # Act
        result = service.fetch_total_tokens_per_team("2024-01-01", "2024-01-02")

        # Assert
        assert len(result) == 2
        assert result["Alpha Team"]["total_tokens"] == 1000
        assert result["Beta Team"]["total_tokens"] == 2000

        # Verify Alpha Team breakdown
        alpha_keys = result["Alpha Team"]["breakdown"]["api_keys"]
        assert len(alpha_keys) == 1
        assert alpha_keys[0]["api_key"] == "key1"
        assert alpha_keys[0]["key_alias"] == "Alpha Key"
        assert alpha_keys[0]["models"][0]["model_name"] == "openai/gpt-4"
        assert alpha_keys[0]["models"][0]["total_tokens"] == 1000

        # Verify Beta Team breakdown
        beta_keys = result["Beta Team"]["breakdown"]["api_keys"]
        assert len(beta_keys) == 1
        assert beta_keys[0]["api_key"] == "key2"
        assert beta_keys[0]["key_alias"] == "Beta Key"
        assert beta_keys[0]["models"][0]["model_name"] == "anthropic/claude-3"
        assert beta_keys[0]["models"][0]["total_tokens"] == 2000

    def test_breakdown_extraction_with_multiple_models(self):
        """Test breakdown extraction logic with multiple models per API key."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-01",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 3000},
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 3000,
                                            "prompt_tokens": 1800,
                                            "completion_tokens": 1200,
                                        }
                                    }
                                },
                            }
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                }
                            },
                            "openai/gpt-3.5-turbo": {
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 2000,
                                            "prompt_tokens": 1200,
                                            "completion_tokens": 800,
                                        }
                                    }
                                }
                            },
                        },
                        "api_keys": {
                            "key1": {"metadata": {"key_alias": "Multi-Model Key"}}
                        },
                    },
                }
            ]
        }
        mock_api_client = MockAPIClient(
            mock_activity_data,
        )
        mock_team_service = MockTeamService(
            team_ids=["team1"], team_id_to_name={"team1": "Alpha Team"}
        )
        service = TokenAggregationService(
            mock_api_client,
            mock_team_service, 
        )

        # Act
        result = service.fetch_total_tokens_per_team("2024-01-01", "2024-01-02")

        # Assert
        assert result["Alpha Team"]["total_tokens"] == 3000
        api_key_data = result["Alpha Team"]["breakdown"]["api_keys"][0]
        assert api_key_data["api_key"] == "key1"
        assert api_key_data["key_alias"] == "Multi-Model Key"
        assert len(api_key_data["models"]) == 2

        # Verify both models are present
        model_names = {m["model_name"] for m in api_key_data["models"]}
        assert model_names == {"openai/gpt-3.5-turbo", "openai/gpt-4"}

        # Verify token counts
        gpt4_model = next(
            m for m in api_key_data["models"] if m["model_name"] == "openai/gpt-4"
        )
        gpt35_model = next(
            m
            for m in api_key_data["models"]
            if m["model_name"] == "openai/gpt-3.5-turbo"
        )
        assert gpt4_model["total_tokens"] == 1000
        assert gpt35_model["total_tokens"] == 2000

    def test_breakdown_merging_across_multiple_dates(self):
        """Test breakdown merging logic across multiple date entries."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-01",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 1000},
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                },
                            }
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                }
                            }
                        },
                        "api_keys": {
                            "key1": {"metadata": {"key_alias": "DevBoost Key"}}
                        },
                    },
                },
                {
                    "date": "2024-01-02",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 1500},
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1500,
                                            "prompt_tokens": 900,
                                            "completion_tokens": 600,
                                        }
                                    }
                                },
                            }
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1500,
                                            "prompt_tokens": 900,
                                            "completion_tokens": 600,
                                        }
                                    }
                                }
                            }
                        },
                        "api_keys": {
                            "key1": {"metadata": {"key_alias": "DevBoost Key"}}
                        },
                    },
                },
            ]
        }
        mock_api_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"], team_id_to_name={"team1": "Alpha Team"}
        )
        service = TokenAggregationService(
            mock_api_client,
            mock_team_service, 
        )

        # Act
        result = service.fetch_total_tokens_per_team("2024-01-01", "2024-01-03")

        # Assert - tokens should be aggregated across both dates
        assert result["Alpha Team"]["total_tokens"] == 2500  # 1000 + 1500

        api_key_data = result["Alpha Team"]["breakdown"]["api_keys"][0]
        assert api_key_data["api_key"] == "key1"
        assert len(api_key_data["models"]) == 1

        model_data = api_key_data["models"][0]
        assert model_data["model_name"] == "openai/gpt-4"
        assert model_data["total_tokens"] == 2500  # 1000 + 1500
        assert model_data["prompt_tokens"] == 1500  # 600 + 900
        assert model_data["completion_tokens"] == 1000  # 400 + 600

    def test_breakdown_merging_with_different_models_across_dates(self):
        """Test breakdown merging when different models are used on different dates."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-01",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 1000},
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                },
                            }
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                }
                            }
                        },
                        "api_keys": {
                            "key1": {"metadata": {"key_alias": "DevBoost Key"}}
                        },
                    },
                },
                {
                    "date": "2024-01-02",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 2000},
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 2000,
                                            "prompt_tokens": 1200,
                                            "completion_tokens": 800,
                                        }
                                    }
                                },
                            }
                        },
                        "model_groups": {
                            "anthropic/claude-3": {
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 2000,
                                            "prompt_tokens": 1200,
                                            "completion_tokens": 800,
                                        }
                                    }
                                }
                            }
                        },
                        "api_keys": {
                            "key1": {"metadata": {"key_alias": "DevBoost Key"}}
                        },
                    },
                },
            ]
        }
        mock_api_client = MockAPIClient(
            mock_activity_data,
        )
        mock_team_service = MockTeamService(
            team_ids=["team1"], team_id_to_name={"team1": "Alpha Team"}
        )
        service = TokenAggregationService(
            mock_api_client,
            mock_team_service, 
        )

        # Act
        result = service.fetch_total_tokens_per_team("2024-01-01", "2024-01-03")

        # Assert
        assert result["Alpha Team"]["total_tokens"] == 3000  # 1000 + 2000

        api_key_data = result["Alpha Team"]["breakdown"]["api_keys"][0]
        assert len(api_key_data["models"]) == 2  # Both models should be present

        model_names = {m["model_name"] for m in api_key_data["models"]}
        assert model_names == {"openai/gpt-4", "anthropic/claude-3"}

        gpt4_model = next(
            m for m in api_key_data["models"] if m["model_name"] == "openai/gpt-4"
        )
        claude_model = next(
            m for m in api_key_data["models"] if m["model_name"] == "anthropic/claude-3"
        )
        assert gpt4_model["total_tokens"] == 1000
        assert claude_model["total_tokens"] == 2000

    def test_breakdown_merging_with_multiple_api_keys(self):
        """Test breakdown merging with multiple API keys across dates."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-01",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 1000},
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                },
                            }
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                }
                            }
                        },
                        "api_keys": {"key1": {"metadata": {"key_alias": "Key 1"}}},
                    },
                },
                {
                    "date": "2024-01-02",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 2000},
                                "api_key_breakdown": {
                                    "key2": {
                                        "metrics": {
                                            "total_tokens": 2000,
                                            "prompt_tokens": 1200,
                                            "completion_tokens": 800,
                                        }
                                    }
                                },
                            }
                        },
                        "models": {
                            "openai/gpt-4": {
                                "api_key_breakdown": {
                                    "key2": {
                                        "metrics": {
                                            "total_tokens": 2000,
                                            "prompt_tokens": 1200,
                                            "completion_tokens": 800,
                                        }
                                    }
                                }
                            }
                        },
                        "api_keys": {"key2": {"metadata": {"key_alias": "Key 2"}}},
                    },
                },
            ]
        }
        mock_api_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"], team_id_to_name={"team1": "Alpha Team"}
        )
        service = TokenAggregationService(
            mock_api_client,
            mock_team_service, 
        )

        # Act
        result = service.fetch_total_tokens_per_team("2024-01-01", "2024-01-03")

        # Assert
        assert result["Alpha Team"]["total_tokens"] == 3000

        api_keys = result["Alpha Team"]["breakdown"]["api_keys"]
        assert len(api_keys) == 2  # Both keys should be present

        key_ids = {k["api_key"] for k in api_keys}
        assert key_ids == {"key1", "key2"}

        key1_data = next(k for k in api_keys if k["api_key"] == "key1")
        key2_data = next(k for k in api_keys if k["api_key"] == "key2")

        assert key1_data["key_alias"] == "Key 1"
        assert key2_data["key_alias"] == "Key 2"
        assert key1_data["models"][0]["total_tokens"] == 1000
        assert key2_data["models"][0]["total_tokens"] == 2000

    def test_api_failure_raises_runtime_error(self):
        """Test that API failures raise RuntimeError with sanitized message."""
        # Arrange
        mock_api_client = MockAPIClient({}, should_fail=True)
        mock_team_service = MockTeamService(
            team_ids=["team1"], team_id_to_name={"team1": "Alpha Team"}
        )
        service = TokenAggregationService(
            mock_api_client,
            mock_team_service, 
        )

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            service.fetch_total_tokens_per_team("2024-01-01", "2024-01-02")

        assert "Error fetching team token usage" in str(exc_info.value)
        assert "Connection failed" in str(exc_info.value)

    def test_breakdown_extraction_without_key_alias(self):
        """Test breakdown extraction when key_alias is missing."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-01",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 1000},
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                },
                            }
                        },
                        "model_groups": {
                            "openai/gpt-4": {
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                }
                            }
                        },
                        "api_keys": {
                            "key1": {"metadata": {}}  # No key_alias
                        },
                    },
                }
            ]
        }
        mock_api_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"], team_id_to_name={"team1": "Alpha Team"}
        )
        service = TokenAggregationService(
            mock_api_client,
            mock_team_service, 
        )

        # Act
        result = service.fetch_total_tokens_per_team("2024-01-01", "2024-01-02")

        # Assert
        api_key_data = result["Alpha Team"]["breakdown"]["api_keys"][0]
        assert api_key_data["api_key"] == "key1"
        assert (
            "key_alias" not in api_key_data
        )  # Should not include key_alias if missing

    def test_breakdown_extraction_fallback_to_all_models(self):
        """Test breakdown extraction fallback when no model-specific data exists."""
        # Arrange
        mock_activity_data = {
            "results": [
                {
                    "date": "2024-01-01",
                    "breakdown": {
                        "entities": {
                            "team1": {
                                "metrics": {"total_tokens": 1000},
                                "api_key_breakdown": {
                                    "key1": {
                                        "metrics": {
                                            "total_tokens": 1000,
                                            "prompt_tokens": 600,
                                            "completion_tokens": 400,
                                        }
                                    }
                                },
                            }
                        },
                        "model_groups": {},  # No model breakdown
                        "api_keys": {
                            "key1": {"metadata": {"key_alias": "Fallback Key"}}
                        },
                    },
                }
            ]
        }
        mock_api_client = MockAPIClient(mock_activity_data)
        mock_team_service = MockTeamService(
            team_ids=["team1"], team_id_to_name={"team1": "Alpha Team"}
        )
        service = TokenAggregationService(
            mock_api_client,
            mock_team_service, 
        )

        # Act
        result = service.fetch_total_tokens_per_team("2024-01-01", "2024-01-02")

        # Assert
        api_key_data = result["Alpha Team"]["breakdown"]["api_keys"][0]
        assert api_key_data["api_key"] == "key1"
        assert len(api_key_data["models"]) == 1
        assert api_key_data["models"][0]["model_name"] == "All Models"
        assert api_key_data["models"][0]["total_tokens"] == 1000
        assert api_key_data["models"][0]["prompt_tokens"] == 600
        assert api_key_data["models"][0]["completion_tokens"] == 400
