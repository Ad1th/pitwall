"""
Statistical Metrics for Predictive Validation.
Ref: docs/VALIDATION.md Section 2
"""

import numpy as np


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate Root Mean Squared Error (RMSE)."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    if len(y_t) == 0:
        return 0.0
    return float(np.sqrt(np.mean((y_t - y_p) ** 2)))


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate Mean Absolute Error (MAE)."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    if len(y_t) == 0:
        return 0.0
    return float(np.mean(np.abs(y_t - y_p)))


def calculate_brier_score(y_true_binary: np.ndarray, p_pred: np.ndarray) -> float:
    """
    Calculate Brier Score for probability calibration.
    BS = (1/N) * sum((p_i - o_i)^2)
    """
    y_t = np.asarray(y_true_binary, dtype=float)
    p_p = np.asarray(p_pred, dtype=float)
    if len(y_t) == 0:
        return 0.0
    return float(np.mean((p_p - y_t) ** 2))


def calculate_ranked_probability_score(y_true_pos: int, predicted_pos_dist: dict, max_pos: int = 20) -> float:
    """
    Calculate Ranked Probability Score (RPS) for ordinal finishing position distribution.
    RPS = (1 / (K - 1)) * sum_k=1^(K-1) (CDF_pred(k) - CDF_true(k))^2
    """
    total_obs = sum(predicted_pos_dist.values())
    if total_obs == 0:
        return 0.0

    # Build empirical PDF and CDF vectors
    pdf_pred = np.zeros(max_pos)
    for p_key, count in predicted_pos_dist.items():
        pos_num = int(str(p_key).replace("P", ""))
        if 1 <= pos_num <= max_pos:
            pdf_pred[pos_num - 1] = count / total_obs

    cdf_pred = np.cumsum(pdf_pred)

    # True CDF indicator
    cdf_true = np.zeros(max_pos)
    if 1 <= y_true_pos <= max_pos:
        cdf_true[y_true_pos - 1 :] = 1.0

    rps = np.mean((cdf_pred[:-1] - cdf_true[:-1]) ** 2)
    return float(rps)
