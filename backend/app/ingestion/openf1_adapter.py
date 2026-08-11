"""
OpenF1 API Adapter (Supplemental 2023+ telemetry data source).
Ref: docs/DATA_SOURCES.md
"""

import logging
from typing import Any, Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

OPENF1_BASE_URL = "https://api.openf1.org/v1"


class OpenF1Adapter:
    """Supplemental client for OpenF1 API (2023+ sessions only)."""

    def __init__(self, base_url: str = OPENF1_BASE_URL, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def fetch_session_telemetry(self, year: int, session_key: str) -> List[Dict[str, Any]]:
        """Fetch supplemental telemetry for 2023+ sessions."""
        if year < 2023:
            logger.info(f"OpenF1 adapter skipped for year {year} (supplemental for 2023+ only).")
            return []
        url = f"{self.base_url}/car_data?session_key={session_key}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as err:
            logger.warning(f"OpenF1 request failed for session {session_key}: {err}")
            return []
