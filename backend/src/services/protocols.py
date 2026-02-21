"""Protocol definitions for service abstractions.

This module defines abstract interfaces using Python's Protocol for structural
subtyping. Services depend on these protocols rather than concrete implementations,
following the Dependency Inversion Principle.
"""

from typing import Protocol, Dict, List, Any

# Import types from client models for protocol definitions
try:
    from src.client.models import (
        TeamResponse,
        SpendAnalyticsPaginatedResponse,
    )
except ImportError:
    # Fallback for type checking when imports fail
    TeamResponse = Any  # type: ignore
    SpendAnalyticsPaginatedResponse = Any  # type: ignore


class APIClientProtocol(Protocol):
    """Abstract interface for external API clients.

    This protocol defines the contract that any API client must satisfy.
    LiteLLMAPI implicitly satisfies this protocol through structural subtyping.
    """

    def fetch_teams(self) -> List[TeamResponse]:
        """Fetch list of teams from external API.

        Returns:
            List of validated TeamResponse objects

        Raises:
            ValueError: If API key is invalid
            RuntimeError: If request fails or response is unexpected
        """
        ...

    def fetch_team_daily_activity(
        self,
        team_ids: str | List[str],
        start_date: str,
        end_date: str,
        page_size: int = 20000,
    ) -> SpendAnalyticsPaginatedResponse:
        """Fetch daily activity data for teams.

        Args:
            team_ids: Single team ID (str) or list of team IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            page_size: Number of records per page (default: 20000)

        Returns:
            Validated SpendAnalyticsPaginatedResponse with daily activity data

        Raises:
            ValueError: If API key is invalid or multiple pages found
            RuntimeError: If request fails
        """
        ...


class TeamServiceProtocol(Protocol):
    """Abstract interface for team management services.

    This protocol defines operations for fetching and mapping team data.
    """

    def fetch_teams(self) -> List[Dict[str, Any]]:
        """Fetch and cache team data from API.

        Returns:
            List of team dictionaries

        Raises:
            ValueError: If API key is invalid
            RuntimeError: If request fails
        """
        ...

    def get_team_ids(self) -> List[str]:
        """Get list of team IDs.

        Fetches teams if not already cached.

        Returns:
            List of team ID strings
        """
        ...

    def get_team_name(self, team_id: str) -> str:
        """Get team name by ID.

        Fetches teams if not already cached.

        Args:
            team_id: The team ID to look up

        Returns:
            Team name (alias if available, otherwise team_id)
        """
        ...


class ModelMappingServiceProtocol(Protocol):
    """Abstract interface for model name mapping services.

    This protocol defines operations for normalizing model names from
    internal gateway names to user-friendly display names.
    """

    def get_display_name(self, internal_name: str) -> str:
        """Get display name for internal model name.

        Args:
            internal_name: Internal model name from API

        Returns:
            User-friendly display name (falls back to internal_name if no mapping)
        """
        ...

    def refresh_mapping(self) -> None:
        """Refresh model name mapping from API.

        Forces a refresh of the cached model name mapping.

        Raises:
            ValueError: If API key is invalid
            RuntimeError: If request fails
        """
        ...


class TeamDailyActivityServiceProtocol(Protocol):
    """Abstract interface for team daily activity services.

    This protocol defines operations for fetching team activity data.
    """

    def fetch_daily_activity(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Fetch daily activity data for all teams.

        Args:
            start_date: Start date in API format (YYYY.MM.DD)
            end_date: End date in ISO format

        Returns:
            Dictionary containing results array with daily activity data

        Raises:
            RuntimeError: If fetching team activity fails
        """
        ...
