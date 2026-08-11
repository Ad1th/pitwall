"""
FastF1 Primary Data Adapter for Lap Timing, Tyre Data, and Track Weather Telemetry.
Ref: docs/DATA_SOURCES.md
"""

import os
import logging
from typing import Any, Dict, List, Optional
import pandas as pd
from backend.app.ingestion.normalizer import clean_lap_record, timedelta_to_seconds, normalize_compound

logger = logging.getLogger(__name__)

CACHE_DIR = "data/cache/fastf1"


class FastF1Adapter:
    """Primary ingestion adapter wrapping FastF1 library."""

    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        self._setup_cache()

    def _setup_cache(self) -> None:
        """Enable local disk caching for FastF1."""
        os.makedirs(self.cache_dir, exist_ok=True)
        try:
            import fastf1
            fastf1.Cache.enable_cache(self.cache_dir)
        except Exception as err:
            logger.warning(f"Could not enable FastF1 cache: {err}")

    def load_race_session(self, year: int, round_num: int) -> Optional[Dict[str, Any]]:
        """Load and parse FastF1 race session."""
        try:
            import fastf1
            session = fastf1.get_session(year, round_num, "R")
            session.load(telemetry=False, weather=True)
            return self._parse_session(session, year, round_num)
        except Exception as err:
            logger.warning(f"FastF1 session load failed for {year} round {round_num}: {err}")
            return None

    def _parse_session(self, session: Any, year: int, round_num: int) -> Dict[str, Any]:
        """Extract structured entities from loaded FastF1 session."""
        race_id = f"{year}-round-{round_num}"
        event_name = getattr(session.event, "EventName", f"Grand Prix {year}")
        circuit_id = getattr(session.event, "Location", "circuit_default").lower().replace(" ", "_")
        
        # 1. Circuit Metadata
        circuit_info = {
            "circuit_id": circuit_id,
            "name": getattr(session.event, "Location", "Circuit"),
            "location": getattr(session.event, "Location", ""),
            "country": getattr(session.event, "Country", ""),
            "latitude": float(getattr(session.event, "Latitude", 0.0)) if hasattr(session.event, "Latitude") else 0.0,
            "longitude": float(getattr(session.event, "Longitude", 0.0)) if hasattr(session.event, "Longitude") else 0.0,
            "length_km": 5.0,  # Default circuit length fallback
            "turns": 16,
            "pit_lane_loss_sec": None,  # Estimated per circuit
            "base_degradation_mult": 1.0,
            "overtaking_difficulty_mult": 1.0,
        }

        # 2. Race Metadata
        total_laps = int(session.laps["LapNumber"].max()) if not session.laps.empty else 50
        race_info = {
            "race_id": race_id,
            "year": year,
            "round": round_num,
            "circuit_id": circuit_id,
            "name": event_name,
            "date": str(session.date.date()) if hasattr(session, "date") and session.date else f"{year}-01-01",
            "total_laps": total_laps,
            "official_winner_driver_id": None,
        }

        # 3. Drivers & Constructors
        drivers_list = []
        constructors_set = set()
        if hasattr(session, "results") and session.results is not None and not session.results.empty:
            for _, row in session.results.iterrows():
                code = str(row.get("Abbreviation", "UNK")).upper()
                d_id = code
                c_id = str(row.get("TeamName", "unknown")).lower().replace(" ", "_")
                constructors_set.add((c_id, str(row.get("TeamName", "Unknown"))))
                drivers_list.append({
                    "driver_id": d_id,
                    "code": code,
                    "permanent_number": int(row.get("DriverNumber")) if pd.notna(row.get("DriverNumber")) else None,
                    "first_name": str(row.get("FirstName", "")),
                    "last_name": str(row.get("LastName", "")),
                    "nationality": str(row.get("CountryCode", "")),
                })
                if int(row.get("Position", 99)) == 1:
                    race_info["official_winner_driver_id"] = d_id

        constructors_list = [
            {"constructor_id": c_id, "name": c_name, "nationality": ""}
            for c_id, c_name in constructors_set
        ]

        # 4. Lap Data Records
        laps_cleaned = []
        if not session.laps.empty:
            for _, lap_row in session.laps.iterrows():
                raw_dict = lap_row.to_dict()
                cleaned = clean_lap_record(raw_dict, race_id)
                laps_cleaned.append(cleaned)

        # 5. Weather Telemetry Records
        weather_cleaned = []
        if hasattr(session, "weather_data") and session.weather_data is not None and not session.weather_data.empty:
            for _, w_row in session.weather_data.iterrows():
                w_time = w_row.get("Time")
                t_stamp = str(w_time) if pd.notna(w_time) else f"{year}-01-01 00:00:00"
                weather_cleaned.append({
                    "race_id": race_id,
                    "timestamp": t_stamp,
                    "air_temp_c": float(w_row.get("AirTemp")) if pd.notna(w_row.get("AirTemp")) else None,
                    "track_temp_c": float(w_row.get("TrackTemp")) if pd.notna(w_row.get("TrackTemp")) else None,
                    "humidity_pct": float(w_row.get("Humidity")) if pd.notna(w_row.get("Humidity")) else None,
                    "pressure_mbar": float(w_row.get("Pressure")) if pd.notna(w_row.get("Pressure")) else None,
                    "rainfall_flag": bool(w_row.get("Rainfall", False)),
                })

        return {
            "circuit": circuit_info,
            "race": race_info,
            "drivers": drivers_list,
            "constructors": constructors_list,
            "lap_data": laps_cleaned,
            "weather_telemetry": weather_cleaned,
        }
