"""
Pydantic Data Schemas for Race State Vector Representation.
Ref: docs/PRD.md Section 3.1 & docs/ARCHITECTURE.md Section 2.2
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SimulationMode(str, Enum):
    DECISION_TIME = "decision_time"
    HINDSIGHT = "hindsight"


class TrackStatus(str, Enum):
    GREEN = "1"
    YELLOW = "2"
    SC = "4"
    RED = "5"
    VSC = "6"


class DriverState(BaseModel):
    driver_id: str
    position: int
    constructor_id: str
    compound: str
    tyre_age: int
    stint_number: int
    gap_to_leader_sec: float
    interval_ahead_sec: float
    last_lap_time_sec: Optional[float] = None
    is_pit_lap: bool = False


class WeatherState(BaseModel):
    track_temp_c: float
    air_temp_c: float
    humidity_pct: Optional[float] = None
    pressure_mbar: Optional[float] = None
    rainfall: bool = False


class RaceStateVector(BaseModel):
    race_id: str
    lap_number: int
    mode: SimulationMode
    track_status: str = "1"
    total_laps: int
    weather: WeatherState
    drivers: List[DriverState] = Field(default_factory=list)

    def get_driver(self, driver_id: str) -> Optional[DriverState]:
        """Find driver state by driver code or ID."""
        d_id = driver_id.upper()
        for d in self.drivers:
            if d.driver_id.upper() == d_id:
                return d
        return None
