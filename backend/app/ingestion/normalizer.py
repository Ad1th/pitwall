"""
Data Normalization & Cleaning Utilities for Formula 1 Lap Timing & Telemetry.
"""

from typing import Any, Dict, Optional
import datetime
import pandas as pd


COMPOUND_MAP = {
    "SOFT": "SOFT",
    "MEDIUM": "MEDIUM",
    "HARD": "HARD",
    "INTERMEDIATE": "INTERMEDIATE",
    "INTER": "INTERMEDIATE",
    "WET": "WET",
    "FULL WET": "WET",
}


def normalize_compound(compound_str: Optional[str]) -> str:
    """Standardize tyre compound string."""
    if not compound_str or pd.isna(compound_str):
        return "UNKNOWN"
    clean_str = str(compound_str).upper().strip()
    return COMPOUND_MAP.get(clean_str, clean_str)


def timedelta_to_seconds(td_val: Any) -> Optional[float]:
    """Convert timedelta or string timedelta representation to float seconds."""
    if td_val is None or pd.isna(td_val):
        return None
    if isinstance(td_val, (int, float)):
        return float(td_val)
    if isinstance(td_val, datetime.timedelta):
        return td_val.total_seconds()
    if isinstance(td_val, pd.Timedelta):
        return td_val.total_seconds()
    try:
        return pd.to_timedelta(td_val).total_seconds()
    except Exception:
        return None


def clean_lap_record(raw_lap: Dict[str, Any], race_id: str) -> Dict[str, Any]:
    """Clean and normalize a raw lap dict for insertion into lap_data table."""
    lap_time = timedelta_to_seconds(raw_lap.get("LapTime"))
    s1 = timedelta_to_seconds(raw_lap.get("Sector1Time"))
    s2 = timedelta_to_seconds(raw_lap.get("Sector2Time"))
    s3 = timedelta_to_seconds(raw_lap.get("Sector3Time"))

    pit_out = raw_lap.get("PitOutTime")
    pit_in = raw_lap.get("PitInTime")
    is_pit_lap = bool(
        (pit_out is not None and not pd.isna(pit_out))
        or (pit_in is not None and not pd.isna(pit_in))
    )

    track_status = str(raw_lap.get("TrackStatus", "1"))
    if not track_status or track_status == "nan":
        track_status = "1"

    is_accurate = raw_lap.get("IsAccurate", True)
    if pd.isna(is_accurate):
        is_accurate = True

    return {
        "race_id": race_id,
        "driver_id": str(raw_lap.get("Driver", "UNK")).upper(),
        "constructor_id": str(raw_lap.get("Team", "unknown")).lower().replace(" ", "_"),
        "lap_number": int(raw_lap.get("LapNumber", 0)),
        "position": int(raw_lap.get("Position")) if pd.notna(raw_lap.get("Position")) else None,
        "lap_time_sec": lap_time,
        "sector1_sec": s1,
        "sector2_sec": s2,
        "sector3_sec": s3,
        "speed_st": float(raw_lap.get("SpeedST")) if pd.notna(raw_lap.get("SpeedST")) else None,
        "compound": normalize_compound(raw_lap.get("Compound")),
        "tyre_age_laps": int(raw_lap.get("TyreLife")) if pd.notna(raw_lap.get("TyreLife")) else 0,
        "stint_number": int(raw_lap.get("Stint")) if pd.notna(raw_lap.get("Stint")) else 1,
        "is_pit_lap": is_pit_lap,
        "is_accurate": bool(is_accurate),
        "track_status": track_status,
        "gap_to_leader_sec": float(raw_lap.get("GapToLeader")) if pd.notna(raw_lap.get("GapToLeader")) else None,
        "interval_to_ahead_sec": float(raw_lap.get("IntervalToAhead")) if pd.notna(raw_lap.get("IntervalToAhead")) else None,
    }
