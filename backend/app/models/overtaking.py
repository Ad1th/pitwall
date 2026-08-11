"""
Probabilistic Overtaking & Traffic Friction Model.
Models dirty air pace penalties and logistic position swap probabilities.
Ref: docs/MODELING.md Section 4
"""

import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class OvertakingModel:
    """Two-Stage Overtaking Friction Kernel for 20-car traffic interactions."""

    def __init__(
        self,
        base_dirty_air_delay: float = 0.40,
        beta_0: float = -2.5,
        beta_pace: float = 1.8,
        beta_tyre: float = 0.05,
        beta_drs: float = 0.8,
        beta_difficulty: float = 1.2,
    ):
        self.base_dirty_air_delay = base_dirty_air_delay
        self.beta_0 = beta_0
        self.beta_pace = beta_pace
        self.beta_tyre = beta_tyre
        self.beta_drs = beta_drs
        self.beta_difficulty = beta_difficulty

    def get_dirty_air_penalty(
        self, interval_ahead_sec: float, circuit_aero_sensitivity: float = 1.0
    ) -> float:
        """
        Calculate lap pace delay (seconds) incurred when running in dirty air.
        Triggered when interval_ahead_sec <= 1.0s.
        """
        if interval_ahead_sec <= 1.0:
            return self.base_dirty_air_delay * circuit_aero_sensitivity
        return 0.0

    def calculate_overtake_probability(
        self,
        pace_delta_sec: float,
        tyre_age_delta: int,
        drs_available: bool = True,
        circuit_overtake_difficulty: float = 1.0,
    ) -> float:
        """
        Calculate logistic probability P(Overtake) of passing car ahead.
        
        pace_delta_sec: (Pace_defender - Pace_attacker) in seconds (positive means attacker is faster)
        tyre_age_delta: (TyreAge_defender - TyreAge_attacker) in laps
        """
        drs_val = 1.0 if drs_available else 0.0
        logit = (
            self.beta_0
            + (self.beta_pace * pace_delta_sec)
            + (self.beta_tyre * tyre_age_delta)
            + (self.beta_drs * drs_val)
            - (self.beta_difficulty * circuit_overtake_difficulty)
        )
        prob = 1.0 / (1.0 + np.exp(-logit))
        return float(np.clip(prob, 0.001, 0.999))

    def resolve_position_swap(
        self,
        pace_delta_sec: float,
        tyre_age_delta: int,
        drs_available: bool = True,
        circuit_overtake_difficulty: float = 1.0,
        rng: Optional[np.random.Generator] = None,
    ) -> bool:
        """Evaluate stochastic overtake trial; returns True if overtake succeeds."""
        p_overtake = self.calculate_overtake_probability(
            pace_delta_sec=pace_delta_sec,
            tyre_age_delta=tyre_age_delta,
            drs_available=drs_available,
            circuit_overtake_difficulty=circuit_overtake_difficulty,
        )
        if rng is None:
            rng = np.random.default_rng()
        draw = rng.uniform(0.0, 1.0)
        return bool(draw < p_overtake)
