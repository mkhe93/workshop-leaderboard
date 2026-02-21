"""Team service for managing team data and mappings."""

from typing import List, Dict, Any
from src.services.protocols import APIClientProtocol
from src.client.models import TeamResponse


class TeamService:
    """Service for managing team data and mappings."""

    def __init__(self, api_client: APIClientProtocol):
        """
        Initialize the TeamService.

        Parameters:
            api_client: An API client instance implementing APIClientProtocol.
        """
        self.api_client = api_client
        self._teams: List[TeamResponse] = []
        self._team_ids: List[str] = []
        self._team_id_to_name: Dict[str, str] = {}
        self._initialized = False

    def fetch_teams(self) -> List[Dict[str, Any]]:
        """
        Fetch teams from API and cache mappings.

        Returns:
            List of team dictionaries from the API (for backward compatibility).
        """
        if self._initialized:
            return [team.model_dump() for team in self._teams]

        self._teams = self.api_client.fetch_teams()
        self._team_ids = [team.team_id for team in self._teams]
        self._team_id_to_name = {
            team.team_id: team.team_alias or team.team_id for team in self._teams
        }
        self._initialized = True
        return [team.model_dump() for team in self._teams]

    def get_team_ids(self) -> List[str]:
        """
        Get list of team IDs, fetching if necessary.

        Returns:
            List of team ID strings.
        """
        if not self._initialized:
            self.fetch_teams()
        return self._team_ids

    def get_team_name(self, team_id: str) -> str:
        """
        Get team name by ID, fetching if necessary.

        Parameters:
            team_id: The team ID to look up.

        Returns:
            Team name (alias) or the team_id if not found.
        """
        if not self._initialized:
            self.fetch_teams()
        return self._team_id_to_name.get(team_id, team_id)
