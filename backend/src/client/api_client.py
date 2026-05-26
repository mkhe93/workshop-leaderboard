import sys
import traceback
from typing import Dict, List, Optional

import requests

from .models import (
    ModelInfoResponse,
    SpendAnalyticsPaginatedResponse,
    TeamResponse,
)


class LiteLLMAPI:
    """
    Client for interacting with the LiteLLM API.

    Attributes:
        api_key (str): The API key used for authentication.
        base_url (str): The base URL for the LiteLLM API.
        headers (dict): HTTP headers including the authorization token.

    Methods:
        fetch_teams(): Fetches the list of teams from the API.
        fetch_team_daily_activity(team_ids, start_date, end_date, page_size): Fetches daily activity for one or more teams.
    """

    def __init__(self, base_url, api_key):
        """
        Initialize the LiteLLMAPI client.

        Parameters:
            base_url (str): The base URL for the LiteLLM API.
            api_key (str): The API key for authentication.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

        self._model_name_map_cache: Optional[Dict[str, str]] = None
        self._model_name_map_cache_time: Optional[float] = None

    def fetch_teams(self) -> List[TeamResponse]:
        """
        Fetch the list of teams from the LiteLLM API.

        Returns:
            List[TeamResponse]: A list of validated team objects.

        Raises:
            ValueError: If the API key is invalid.
            RuntimeError: If the response is not as expected or a request error occurs.
        """
        url = f"{self.base_url}/team/list"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 401:
                raise ValueError("Invalid API key.")
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list):
                raise RuntimeError("Unexpected response from /team/list.")

            # Parse and validate response data
            return [TeamResponse.model_validate(team) for team in data]
        except requests.RequestException as e:
            raise RuntimeError(f"Error fetching teams: {e}")

    def fetch_team_daily_activity(
        self,
        team_ids: str | List[str],
        start_date: str,
        end_date: str,
        page_size: int = 20000,
    ) -> SpendAnalyticsPaginatedResponse:
        """
        Fetch daily activity data for one or more teams from the LiteLLM API.

        Parameters:
            team_ids: A single team ID (str) or a list of team IDs (list of str).
            start_date: The start date for the activity data (YYYY-MM-DD).
            end_date: The end date for the activity data (YYYY-MM-DD).
            page_size: The number of records per page (default: 20000).

        Returns:
            SpendAnalyticsPaginatedResponse: Validated paginated activity data.

        Raises:
            ValueError: If the API key is invalid or if multiple pages of results are found.
            RuntimeError: If a request error occurs.
        """
        # Handle both single team_id string and list of team_ids
        if isinstance(team_ids, list):
            team_ids_param = ",".join(team_ids)
        else:
            team_ids_param = team_ids

        url = (
            f"{self.base_url}/team/daily/activity"
            f"?team_ids={team_ids_param}"
            f"&start_date={start_date}"
            f"&end_date={end_date}"
            f"&page_size={page_size}"
        )
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 401:
                raise ValueError("Invalid API key.")
            resp.raise_for_status()
            data = resp.json()

            try:
                if data["metadata"]["total_pages"] > 1:
                    raise ValueError(
                        "Multiple pages of results found, pagination not supported."
                    )
            except ValueError:
                traceback.print_exc()
                sys.exit(1)

            # Parse and validate response data
            return SpendAnalyticsPaginatedResponse.model_validate(data)

        except requests.RequestException as e:
            team_id_msg = team_ids if isinstance(team_ids, str) else "multiple teams"
            raise RuntimeError(f"Error fetching activity for {team_id_msg}: {e}")

    def fetch_model_info(self) -> ModelInfoResponse:
        """Fetch model info from LiteLLM gateway.

        The gateway typically returns a dict with a `data` array. Each item can include
        `model_name` (gateway deployment id/name) and `litellm_params.model` (canonical).

        Returns:
            ModelInfoResponse: Validated model information response.

        Raises:
            ValueError: If the API key is invalid.
            RuntimeError: If the response is not as expected or a request error occurs.
        """
        # LiteLLM exposes both /model/info and /v1/model/info depending on deployment.
        url = f"{self.base_url}/model/info"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 401:
                raise ValueError("Invalid API key.")
            if resp.status_code == 404:
                url = f"{self.base_url}/v1/model/info"
                resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, dict):
                raise RuntimeError("Unexpected response from /model/info.")

            # Parse and validate response data
            return ModelInfoResponse.model_validate(data)
        except requests.RequestException as e:
            raise RuntimeError(f"Error fetching model info: {e}")
