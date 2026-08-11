"""
Stage 3 Predictive & Statistical ML Models Unit Tests.
Ref: docs/DEVELOPMENT_PLAN.md Stage 3
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.models.tyre_deg import TyreDegradationModel
from backend.app.models.pace import BasePaceModel
from backend.app.models.overtaking import OvertakingModel


def test_tyre_deg_monotone():
    """Verify degradation penalty increases monotonically with tyre age."""
    model = TyreDegradationModel()
    deg_5 = model.predict_degradation("MEDIUM", 5)
    deg_15 = model.predict_degradation("MEDIUM", 15)
    deg_25 = model.predict_degradation("MEDIUM", 25)

    assert deg_5 >= 0.0
    assert deg_15 > deg_5
    assert deg_25 > deg_15


def test_tyre_deg_compounds():
    """Verify compound wear hierarchy: SOFT > MEDIUM > HARD at same age."""
    model = TyreDegradationModel()
    soft_deg = model.predict_degradation("SOFT", 15)
    med_deg = model.predict_degradation("MEDIUM", 15)
    hard_deg = model.predict_degradation("HARD", 15)

    assert soft_deg > med_deg
    assert med_deg > hard_deg


def test_pace_fuel_decay():
    """Verify base lap pace improves (fuel weight decreases) as race progresses."""
    model = BasePaceModel(fuel_burn_rate=0.035)
    pace_lap_1 = model.predict_base_pace("yas_marina", "mercedes", "HAM", lap_number=1, total_laps=58)
    pace_lap_30 = model.predict_base_pace("yas_marina", "mercedes", "HAM", lap_number=30, total_laps=58)
    pace_lap_58 = model.predict_base_pace("yas_marina", "mercedes", "HAM", lap_number=58, total_laps=58)

    # Higher lap number -> less fuel remaining -> faster lap time (smaller seconds)
    assert pace_lap_1 > pace_lap_30
    assert pace_lap_30 > pace_lap_58


def test_overtaking_dirty_air():
    """Verify dirty air delay is applied within 1.0s interval and zero outside."""
    model = OvertakingModel(base_dirty_air_delay=0.40)
    delay_close = model.get_dirty_air_penalty(interval_ahead_sec=0.5)
    delay_far = model.get_dirty_air_penalty(interval_ahead_sec=1.5)

    assert delay_close == 0.40
    assert delay_far == 0.0


def test_overtaking_probabilities():
    """Verify overtake probability increases with pace delta and remains bounded in [0, 1]."""
    model = OvertakingModel()

    # Faster attacker vs slower attacker
    prob_slow = model.calculate_overtake_probability(pace_delta_sec=0.2, tyre_age_delta=5)
    prob_fast = model.calculate_overtake_probability(pace_delta_sec=1.5, tyre_age_delta=15)

    assert 0.0 <= prob_slow <= 1.0
    assert 0.0 <= prob_fast <= 1.0
    assert prob_fast > prob_slow


def test_overtaking_stochastic_swap():
    """Verify deterministic RNG resolution."""
    model = OvertakingModel()
    rng1 = np.random.default_rng(42)
    rng2 = np.random.default_rng(42)

    res1 = model.resolve_position_swap(pace_delta_sec=1.0, tyre_age_delta=10, rng=rng1)
    res2 = model.resolve_position_swap(pace_delta_sec=1.0, tyre_age_delta=10, rng=rng2)

    assert res1 == res2
