"""
Jolpica-F1 API Adapter (Open-source, community-maintained Ergast-compatible REST client).
Ref: docs/DATA_SOURCES.md
"""

import logging
from typing import Any, Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

JOLPICA_BASE_URL = "https://api.jolpi.ca/ergast/f1"


class JolpicaAdapter:
    """Client for Jolpica F1 Ergast-compatible API."""

    def __init__(self, base_url: str = JOLPICA_BASE_URL, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as err:
            logger.warning(f"Jolpica API request failed for URL {url}: {err}")
            return None

    def fetch_race_results(self, year: int, round_num: int) -> List[Dict[str, Any]]:
        """Fetch official race classification results."""
        data = self._get(f"{year}/{round_num}/results.json")
        if not data:
            return []
        try:
            races = data["MRData"]["RaceTable"]["Races"]
            if races:
                return races[0].get("Results", [])
        except (KeyError, IndexError) as err:
            logger.warning(f"Failed to parse Jolpica race results: {err}")
        return []

    def fetch_pit_stops(self, year: int, round_num: int) -> List[Dict[str, Any]]:
        """Fetch pit stop timing records."""
        data = self._get(f"{year}/{round_num}/pitstops.json")
        if not data:
            return []
        try:
            races = data["MRData"]["RaceTable"]["Races"]
            if races:
                return races[0].get("PitStops", [])
        except (KeyError, IndexError) as err:
            logger.warning(f"Failed to parse Jolpica pit stops: {err}")
        return []

    def fetch_driver_standings(self, year: int, round_num: int) -> List[Dict[str, Any]]:
        """Fetch driver standings after specified round."""
        data = self._get(f"{year}/{round_num}/driverstandings.json")
        if not data:
            return []
        try:
            standings_lists = data["MRData"]["StandingsTable"]["StandingsLists"]
            if standings_lists:
                return standings_lists[0].get("DriverStandings", [])
        except (KeyError, IndexError) as err:
            logger.warning(f"Failed to parse Jolpica driver standings: {err}")
        return []
