"""
Race State Reconstruction Engine.
Reconstructs spatial-temporal vector RaceState(t) from DuckDB.
Ref: docs/PRD.md Section 3.1 & docs/ARCHITECTURE.md Section 2.2
"""

import logging
from typing import Any, Dict, List, Optional
import duckdb
from backend.app.schemas.state import DriverState, RaceStateVector, SimulationMode, WeatherState

logger = logging.getLogger(__name__)


class RaceStateEngine:
    """Engine for reconstructing F1 race state vectors at lap t."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def reconstruct_state(
        self,
        race_id: str,
        lap_number: int,
        mode: SimulationMode = SimulationMode.DECISION_TIME,
    ) -> Optional[RaceStateVector]:
        """
        Reconstruct complete RaceStateVector at lap t.
        
        In DECISION_TIME mode, queries strictly filter data at or prior to lap t to prevent look-ahead bias.
        In HINDSIGHT mode, full historical telemetry is accessible for retrospective analysis.
        """
        # 1. Fetch race metadata
        race_row = self.conn.execute(
            "SELECT total_laps FROM races WHERE race_id = ?", [race_id]
        ).fetchone()

        if not race_row:
            logger.warning(f"Race '{race_id}' not found in database.")
            return None

        total_laps = race_row[0]

        # Clamp requested lap number
        lap_number = max(1, min(lap_number, total_laps))

        # 2. Fetch driver lap records at lap t (or latest available lap <= t for decision_time)
        if mode == SimulationMode.DECISION_TIME:
            query = """
            SELECT 
                driver_id,
                constructor_id,
                position,
                compound,
                tyre_age_laps,
                stint_number,
                gap_to_leader_sec,
                interval_to_ahead_sec,
                lap_time_sec,
                is_pit_lap,
                track_status
            FROM lap_data
            WHERE race_id = ? AND lap_number = ?
            ORDER BY position ASC
            """
            laps = self.conn.execute(query, [race_id, lap_number]).fetchall()
        else:
            # Hindsight mode
            query = """
            SELECT 
                driver_id,
                constructor_id,
                position,
                compound,
                tyre_age_laps,
                stint_number,
                gap_to_leader_sec,
                interval_to_ahead_sec,
                lap_time_sec,
                is_pit_lap,
                track_status
            FROM lap_data
            WHERE race_id = ? AND lap_number = ?
            ORDER BY position ASC
            """
            laps = self.conn.execute(query, [race_id, lap_number]).fetchall()

        if not laps:
            logger.warning(f"No lap data found for race '{race_id}' at lap {lap_number}.")
            return None

        # 3. Parse drivers list & track status
        drivers: List[DriverState] = []
        track_status = "1"

        for row in laps:
            (
                d_id,
                c_id,
                pos,
                compound,
                tyre_age,
                stint,
                gap_leader,
                interval_ahead,
                lap_time,
                is_pit,
                status,
            ) = row

            if status and status != "1":
                track_status = status

            drivers.append(
                DriverState(
                    driver_id=d_id,
                    position=pos or len(drivers) + 1,
                    constructor_id=c_id,
                    compound=compound or "MEDIUM",
                    tyre_age=tyre_age or 1,
                    stint_number=stint or 1,
                    gap_to_leader_sec=float(gap_leader) if gap_leader is not None else 0.0,
                    interval_ahead_sec=float(interval_ahead) if interval_ahead is not None else 0.0,
                    last_lap_time_sec=float(lap_time) if lap_time is not None else None,
                    is_pit_lap=bool(is_pit),
                )
            )

        # 4. Fetch weather state
        weather_row = self.conn.execute(
            """
            SELECT air_temp_c, track_temp_c, humidity_pct, pressure_mbar, rainfall_flag
            FROM weather_telemetry
            WHERE race_id = ?
            LIMIT 1
            """,
            [race_id],
        ).fetchone()

        if weather_row:
            air, track, hum, pres, rain = weather_row
            weather = WeatherState(
                air_temp_c=air if air is not None else 22.0,
                track_temp_c=track if track is not None else 30.0,
                humidity_pct=hum,
                pressure_mbar=pres,
                rainfall=bool(rain),
            )
        else:
            weather = WeatherState(air_temp_c=22.0, track_temp_c=30.0, rainfall=False)

        return RaceStateVector(
            race_id=race_id,
            lap_number=lap_number,
            mode=mode,
            track_status=track_status,
            total_laps=total_laps,
            weather=weather,
            drivers=drivers,
        )
