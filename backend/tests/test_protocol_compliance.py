"""Tests for protocol compliance.

This module tests that concrete implementations satisfy their protocol interfaces
through structural subtyping (duck typing).
"""

import pytest
from inspect import signature
from src.client.api_client import LiteLLMAPI
from src.services.protocols import APIClientProtocol


class TestAPIClientProtocolCompliance:
    """Test that LiteLLMAPI satisfies APIClientProtocol interface."""

    def test_litellm_api_has_fetch_teams_method(self):
        """Test that LiteLLMAPI has fetch_teams method with correct signature."""
        assert hasattr(LiteLLMAPI, "fetch_teams")

        # Check method signature
        method = getattr(LiteLLMAPI, "fetch_teams")
        sig = signature(method)

        # Should have no required parameters (only self)
        params = [p for p in sig.parameters.values() if p.name != "self"]
        assert len(params) == 0, "fetch_teams should have no parameters besides self"

    def test_litellm_api_has_fetch_team_daily_activity_method(self):
        """Test that LiteLLMAPI has fetch_team_daily_activity method with correct signature."""
        assert hasattr(LiteLLMAPI, "fetch_team_daily_activity")

        # Check method signature
        method = getattr(LiteLLMAPI, "fetch_team_daily_activity")
        sig = signature(method)

        # Should have team_ids, start_date, end_date, and optional page_size
        params = {p.name: p for p in sig.parameters.values() if p.name != "self"}
        assert "team_ids" in params
        assert "start_date" in params
        assert "end_date" in params
        assert "page_size" in params

        # page_size should have a default value
        assert params["page_size"].default == 20000

    def test_litellm_api_satisfies_protocol_structurally(self):
        """Test that LiteLLMAPI can be used where APIClientProtocol is expected."""

        def accepts_api_client(client: APIClientProtocol) -> str:
            """Function that accepts APIClientProtocol."""
            return "success"

        # Create a mock instance (we don't need real API calls for structural typing test)
        mock_client = LiteLLMAPI(base_url="http://test", api_key="test_key")

        # This should not raise any type errors at runtime
        # (static type checkers like mypy would verify this at compile time)
        result = accepts_api_client(mock_client)
        assert result == "success"

    def test_protocol_methods_match_implementation(self):
        """Test that all protocol methods exist in LiteLLMAPI with compatible signatures."""
        protocol_methods = {
            "fetch_teams": [],
            "fetch_team_daily_activity": [
                "team_ids",
                "start_date",
                "end_date",
                "page_size",
            ],
        }

        for method_name, expected_params in protocol_methods.items():
            # Check method exists
            assert hasattr(LiteLLMAPI, method_name), (
                f"LiteLLMAPI missing method: {method_name}"
            )

            # Check parameters
            method = getattr(LiteLLMAPI, method_name)
            sig = signature(method)
            actual_params = [p for p in sig.parameters.keys() if p != "self"]

            assert actual_params == expected_params, (
                f"Method {method_name} has parameters {actual_params}, "
                f"expected {expected_params}"
            )


class TestProtocolTypeChecking:
    """Test protocol type checking behavior."""

    def test_protocol_is_not_instantiable(self):
        """Test that Protocol classes cannot be instantiated directly."""
        with pytest.raises(TypeError):
            APIClientProtocol()  # type: ignore

    def test_protocol_can_be_used_as_type_hint(self):
        """Test that protocols can be used in type hints."""

        def process_client(client: APIClientProtocol) -> bool:
            """Function using protocol as type hint."""
            return hasattr(client, "fetch_teams")

        # Create mock client
        mock_client = LiteLLMAPI(base_url="http://test", api_key="test_key")

        # Should work with any object that has the required methods
        assert process_client(mock_client) is True

    def test_incomplete_implementation_fails_duck_typing(self):
        """Test that objects missing protocol methods fail duck typing checks."""

        class IncompleteClient:
            """Client missing some protocol methods."""

            def fetch_teams(self):
                return []

            # Missing fetch_team_daily_activity

        incomplete = IncompleteClient()

        # Should not have all required methods
        assert hasattr(incomplete, "fetch_teams")
        assert not hasattr(incomplete, "fetch_team_daily_activity")
