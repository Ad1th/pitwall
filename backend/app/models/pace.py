"""
Expected Base Pace & Fuel Decay Model.
Estimates clean-air base lap pace incorporating fuel mass burn decay.
Ref: docs/MODELING.md Section 3 & Section 2
"""

import logging
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Default calibrated priors
DEFAULT_FUEL_BURN_RATE = 0.035  # seconds lap time gain per completed lap (fuel burn)
DEFAULT_CIRCUIT_BENCHMARKS = {
    "yas_marina": 87.0,
    "monaco": 74.0,
    "silverstone": 89.0,
    "zandvoort": 73.0,
    "default": 85.0,
}


class BasePaceModel:
    """Estimates clean-air baseline lap pace for driver/car combination."""

    def __init__(
        self,
        fuel_burn_rate: float = DEFAULT_FUEL_BURN_RATE,
        circuit_benchmarks: Optional[Dict[str, float]] = None,
    ):
        self.fuel_burn_rate = fuel_burn_rate
        self.circuit_benchmarks = circuit_benchmarks or DEFAULT_CIRCUIT_BENCHMARKS.copy()
        self.constructor_deltas: Dict[str, float] = {}
        self.driver_deltas: Dict[str, float] = {}

    def predict_base_pace(
        self,
        circuit_id: str,
        constructor_id: str,
        driver_id: str,
        lap_number: int,
        total_laps: int,
    ) -> float:
        """
        Predict baseline clean-air lap pace (seconds) on fresh tyres.
        
        As lap_number increases (fuel burns down), fuel weight penalty decreases,
        improving lap pace by fuel_burn_rate * (total_laps - lap_number).
        """
        circuit_key = str(circuit_id).lower()
        base_benchmark = self.circuit_benchmarks.get(circuit_key, self.circuit_benchmarks["default"])

        c_delta = self.constructor_deltas.get(str(constructor_id).lower(), 0.0)
        d_delta = self.driver_deltas.get(str(driver_id).upper(), 0.0)

        # Remaining fuel mass penalty
        laps_remaining = max(0, total_laps - lap_number)
        fuel_penalty = laps_remaining * self.fuel_burn_rate

        expected_pace = base_benchmark + c_delta + d_delta + fuel_penalty
        return max(50.0, float(expected_pace))

    def fit(self, lap_data_df: pd.DataFrame) -> Dict[str, Any]:
        """Fit empirical constructor and driver pace deltas from clean lap data."""
        if lap_data_df.empty:
            return {"fitted": False}

        clean_laps = lap_data_df[
            (lap_data_df["is_accurate"] == True)
            & (lap_data_df["is_pit_lap"] == False)
            & (lap_data_df["track_status"] == "1")
            & (lap_data_df["lap_time_sec"].notnull())
        ]

        if clean_laps.empty:
            return {"fitted": False}

        race_median = clean_laps["lap_time_sec"].median()

        # Constructor deltas
        c_grp = clean_laps.groupby("constructor_id")["lap_time_sec"].median()
        for c_id, c_med in c_grp.items():
            self.constructor_deltas[str(c_id).lower()] = float(c_med - race_median)

        # Driver deltas
        d_grp = clean_laps.groupby("driver_id")["lap_time_sec"].median()
        for d_id, d_med in d_grp.items():
            self.driver_deltas[str(d_id).upper()] = float(d_med - race_median)

        return {
            "fitted": True,
            "race_median_pace": float(race_median),
            "num_constructors": len(self.constructor_deltas),
            "num_drivers": len(self.driver_deltas),
        }
