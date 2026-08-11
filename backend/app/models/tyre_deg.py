"""
Statistical Tyre Degradation Model.
Predicts lap pace wear rate delta_T_deg(compound, tyre_age, track_temp).
Ref: docs/MODELING.md Section 3
"""

import logging
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Default calibrated compound degradation priors (seconds per lap age)
DEFAULT_COMPOUND_SLOPES = {
    "SOFT": 0.085,
    "MEDIUM": 0.055,
    "HARD": 0.035,
    "INTERMEDIATE": 0.065,
    "WET": 0.075,
    "UNKNOWN": 0.050,
}


class TyreDegradationModel:
    """Predicts continuous lap pace loss due to tyre wear."""

    def __init__(self, compound_slopes: Optional[Dict[str, float]] = None):
        self.compound_slopes = compound_slopes or DEFAULT_COMPOUND_SLOPES.copy()
        self.temp_coefficient = 0.002  # seconds/lap per °C deviation from 30°C

    def predict_degradation(
        self, compound: str, tyre_age: int, track_temp_c: float = 30.0
    ) -> float:
        """
        Predict pace degradation penalty in seconds/lap.
        Enforces monotone non-decreasing constraint on tyre_age.
        """
        cmp_key = str(compound).upper().strip()
        base_slope = self.compound_slopes.get(cmp_key, self.compound_slopes.get("UNKNOWN", 0.0))

        # Thermal adjustment
        temp_delta = max(0.0, track_temp_c - 30.0)
        effective_slope = base_slope + (temp_delta * self.temp_coefficient)

        # Non-linear cliff penalty for high tyre age (age > 20 laps)
        age = max(0, tyre_age)
        linear_wear = age * effective_slope
        cliff_wear = 0.003 * max(0, age - 20) ** 1.8 if age > 20 else 0.0

        deg_sec = linear_wear + cliff_wear
        return max(0.0, deg_sec)

    def fit(self, lap_data_df: pd.DataFrame) -> Dict[str, Any]:
        """Fit empirical degradation slopes per compound from historical lap data."""
        if lap_data_df.empty:
            return {"fitted": False, "reason": "Empty dataset"}

        clean_laps = lap_data_df[
            (lap_data_df["is_accurate"] == True)
            & (lap_data_df["is_pit_lap"] == False)
            & (lap_data_df["track_status"] == "1")
            & (lap_data_df["lap_time_sec"].notnull())
        ].copy()

        if len(clean_laps) < 10:
            return {"fitted": False, "reason": "Insufficient clean laps"}

        metrics = {}
        for cmp_name in clean_laps["compound"].unique():
            cmp_df = clean_laps[clean_laps["compound"] == cmp_name]
            if len(cmp_df) >= 5:
                # Fit linear regression: lap_time ~ tyre_age_laps
                x = cmp_df["tyre_age_laps"].values
                y = cmp_df["lap_time_sec"].values
                if len(set(x)) > 1:
                    slope, _ = np.polyfit(x, y, 1)
                    # Enforce non-negative slope prior constraint
                    fitted_slope = max(0.01, float(slope))
                    self.compound_slopes[cmp_name] = fitted_slope
                    metrics[cmp_name] = {"slope": fitted_slope, "samples": len(cmp_df)}

        return {"fitted": True, "metrics": metrics}
