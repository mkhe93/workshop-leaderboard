"""Unit tests for TeamService."""

from typing import List, Dict, Any
from src.services.team_service import TeamService
from src.client.models import TeamResponse


class MockAPIClient:
    """Mock API client for testing TeamService."""

    def __init__(self, teams_data: List[Dict[str, Any]]):
        """Initialize mock with test data."""
        self._teams_data = teams_data
        self.fetch_teams_call_count = 0

    def fetch_teams(self) -> List[TeamResponse]:
        """Mock fetch_teams method - returns Pydantic models."""
        self.fetch_teams_call_count += 1
        return [TeamResponse.model_validate(team) for team in self._teams_data]

    def fetch_team_daily_activity(
        self,
        team_ids: str | List[str],
        start_date: str,
        end_date: str,
        page_size: int = 20000,
    ) -> Dict[str, Any]:
        """Mock fetch_team_daily_activity method."""
        return {"results": []}

    def get_model_name_map(self, ttl_seconds: int = 300) -> Dict[str, str]:
        """Mock get_model_name_map method."""
        return {}


class TestTeamService:
    """Test suite for TeamService."""

    def test_fetch_teams_with_valid_data(self):
        """Test team fetching with valid team data."""
        # Arrange
        mock_teams = [
            {"team_id": "team1", "team_alias": "Alpha Team"},
            {"team_id": "team2", "team_alias": "Beta Team"},
            {"team_id": "team3", "team_alias": "Gamma Team"},
        ]
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act
        result = service.fetch_teams()

        # Assert - check that result contains the expected teams
        assert len(result) == 3
        assert result[0]["team_id"] == "team1"
        assert result[0]["team_alias"] == "Alpha Team"
        assert result[1]["team_id"] == "team2"
        assert result[1]["team_alias"] == "Beta Team"
        assert result[2]["team_id"] == "team3"
        assert result[2]["team_alias"] == "Gamma Team"
        assert mock_client.fetch_teams_call_count == 1
        assert service._initialized is True

    def test_fetch_teams_lazy_initialization(self):
        """Test that fetch_teams is only called once (lazy initialization)."""
        # Arrange
        mock_teams = [
            {"team_id": "team1", "team_alias": "Alpha Team"},
        ]
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act - call fetch_teams multiple times
        result1 = service.fetch_teams()
        result2 = service.fetch_teams()
        result3 = service.fetch_teams()

        # Assert - API should only be called once and results should be consistent
        assert len(result1) == 1
        assert result1[0]["team_id"] == "team1"
        assert result1 == result2 == result3
        assert mock_client.fetch_teams_call_count == 1

    def test_get_team_ids_with_valid_data(self):
        """Test team ID extraction from team data."""
        # Arrange
        mock_teams = [
            {"team_id": "team1", "team_alias": "Alpha Team"},
            {"team_id": "team2", "team_alias": "Beta Team"},
            {"team_id": "team3", "team_alias": "Gamma Team"},
        ]
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act
        team_ids = service.get_team_ids()

        # Assert
        assert team_ids == ["team1", "team2", "team3"]
        assert mock_client.fetch_teams_call_count == 1

    def test_get_team_ids_triggers_lazy_initialization(self):
        """Test that get_team_ids triggers fetch_teams if not initialized."""
        # Arrange
        mock_teams = [
            {"team_id": "team1", "team_alias": "Alpha Team"},
        ]
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act - call get_team_ids without calling fetch_teams first
        team_ids = service.get_team_ids()

        # Assert
        assert team_ids == ["team1"]
        assert service._initialized is True
        assert mock_client.fetch_teams_call_count == 1

    def test_get_team_name_with_valid_id(self):
        """Test team name lookup with valid team ID."""
        # Arrange
        mock_teams = [
            {"team_id": "team1", "team_alias": "Alpha Team"},
            {"team_id": "team2", "team_alias": "Beta Team"},
        ]
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act
        name1 = service.get_team_name("team1")
        name2 = service.get_team_name("team2")

        # Assert
        assert name1 == "Alpha Team"
        assert name2 == "Beta Team"
        assert mock_client.fetch_teams_call_count == 1

    def test_get_team_name_with_invalid_id(self):
        """Test team name lookup with invalid team ID returns the ID itself."""
        # Arrange
        mock_teams = [
            {"team_id": "team1", "team_alias": "Alpha Team"},
        ]
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act
        name = service.get_team_name("nonexistent_team")

        # Assert
        assert name == "nonexistent_team"

    def test_get_team_name_triggers_lazy_initialization(self):
        """Test that get_team_name triggers fetch_teams if not initialized."""
        # Arrange
        mock_teams = [
            {"team_id": "team1", "team_alias": "Alpha Team"},
        ]
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act - call get_team_name without calling fetch_teams first
        name = service.get_team_name("team1")

        # Assert
        assert name == "Alpha Team"
        assert service._initialized is True
        assert mock_client.fetch_teams_call_count == 1

    def test_team_name_fallback_to_team_id(self):
        """Test that team name falls back to team_id when team_alias is missing or empty."""
        # Arrange
        mock_teams = [
            {"team_id": "team1"},  # No team_alias
            {
                "team_id": "team2",
                "team_alias": "",
            },  # Empty team_alias
        ]
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act
        name1 = service.get_team_name("team1")
        name2 = service.get_team_name("team2")

        # Assert
        assert name1 == "team1"  # Falls back to team_id when team_alias is missing
        assert (
            name2 == "team2"
        )  # Falls back to team_id when team_alias is empty (None or "")

    def test_empty_teams_scenario(self):
        """Test service behavior with empty teams list."""
        # Arrange
        mock_teams: List[Dict[str, Any]] = []
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act
        teams = service.fetch_teams()
        team_ids = service.get_team_ids()
        name = service.get_team_name("any_id")

        # Assert
        assert teams == []
        assert team_ids == []
        assert name == "any_id"  # Falls back to the ID itself
        assert service._initialized is True

    def test_teams_with_missing_team_id(self):
        """Test that teams with valid team_id are processed correctly."""
        # Arrange - Only include valid teams since Pydantic validates team_id is required
        mock_teams = [
            {"team_id": "team1", "team_alias": "Alpha Team"},
            {"team_id": "team2", "team_alias": "Beta Team"},
        ]
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act
        team_ids = service.get_team_ids()

        # Assert - Only valid teams with team_id are included
        assert len(team_ids) == 2
        assert "team1" in team_ids
        assert "team2" in team_ids

        # Act
        team_ids = service.get_team_ids()

        # Assert
        assert team_ids == ["team1", "team2"]
        assert len(service._team_id_to_name) == 2

    def test_multiple_method_calls_use_cached_data(self):
        """Test that multiple method calls use cached data without re-fetching."""
        # Arrange
        mock_teams = [
            {"team_id": "team1", "team_alias": "Alpha Team"},
            {"team_id": "team2", "team_alias": "Beta Team"},
        ]
        mock_client = MockAPIClient(mock_teams)
        service = TeamService(mock_client)  # type: ignore[arg-type]

        # Act - call various methods multiple times
        service.fetch_teams()
        service.get_team_ids()
        service.get_team_name("team1")
        service.get_team_ids()
        service.get_team_name("team2")
        service.fetch_teams()

        # Assert - API should only be called once
        assert mock_client.fetch_teams_call_count == 1
