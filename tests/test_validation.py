"""
Stage 11 Validation Infrastructure Unit Tests.
Ref: docs/DEVELOPMENT_PLAN.md Stage 11
"""

import pytest
import numpy as np
from backend.app.db.schema import get_db_connection
from backend.app.validation.metrics import (
    calculate_rmse,
    calculate_mae,
    calculate_brier_score,
    calculate_ranked_probability_score,
)
from backend.app.validation.evaluator import RollingOriginEvaluator
from scripts.seed_db import seed_race


def test_metrics_rmse_mae():
    """Verify RMSE and MAE metric calculations."""
    y_true = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.0, 2.0, 5.0])

    # Error vector: [0, 0, 2] -> MAE = 2/3 = 0.666, RMSE = sqrt(4/3) = 1.1547
    mae = calculate_mae(y_true, y_pred)
    rmse = calculate_rmse(y_true, y_pred)

    assert round(mae, 3) == 0.667
    assert round(rmse, 3) == 1.155


def test_metrics_brier_score():
    """Verify Brier Score calculation."""
    y_true = np.array([1.0, 0.0])
    p_pred = np.array([0.9, 0.1])

    # (0.1^2 + 0.1^2) / 2 = 0.01
    brier = calculate_brier_score(y_true, p_pred)
    assert round(brier, 4) == 0.0100


def test_metrics_rps():
    """Verify Ranked Probability Score calculation."""
    predicted_dist = {"P1": 80, "P2": 20}
    rps = calculate_ranked_probability_score(y_true_pos=1, predicted_pos_dist=predicted_dist)
    assert rps >= 0.0


def test_evaluator_ablation():
    """Verify RollingOriginEvaluator runs with ablation flags."""
    conn = get_db_connection(":memory:")
    seed_race("2021-abu-dhabi", conn, force_offline=True)

    evaluator = RollingOriginEvaluator(conn, no_tyre_deg=True, no_traffic=True)
    res = evaluator.evaluate_race("2021-abu-dhabi", origin_laps=[53])

    assert res["race_id"] == "2021-abu-dhabi"
    assert res["ablations"]["no_tyre_deg"] is True
    assert res["metrics"]["rmse"] >= 0.0
    conn.close()
