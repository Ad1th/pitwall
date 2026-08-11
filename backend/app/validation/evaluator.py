"""
Rolling-Origin Model Evaluation and Ablation Engine.
Ref: docs/VALIDATION.md Section 3 & docs/DEVELOPMENT_PLAN.md Stage 11
"""

import logging
from typing import Dict, Any, List, Optional
import numpy as np
import duckdb

from backend.app.schemas.state import SimulationMode
from backend.app.schemas.simulation import CandidateStrategy
from backend.app.engine.state import RaceStateEngine
from backend.app.engine.simulator import MonteCarloSimulator
from backend.app.models.tyre_deg import TyreDegradationModel
from backend.app.models.pace import BasePaceModel
from backend.app.models.overtaking import OvertakingModel
from backend.app.validation.metrics import (
    calculate_rmse,
    calculate_mae,
    calculate_brier_score,
    calculate_ranked_probability_score,
)

logger = logging.getLogger(__name__)


class RollingOriginEvaluator:
    """Evaluates simulator performance and model ablations across historical benchmark races."""

    def __init__(
        self,
        conn: duckdb.DuckDBPyConnection,
        no_tyre_deg: bool = False,
        no_traffic: bool = False,
        no_weather_markov: bool = False,
    ):
        self.conn = conn
        self.no_tyre_deg = no_tyre_deg
        self.no_traffic = no_traffic
        self.no_weather_markov = no_weather_markov

        # Configure ablated model instances
        tyre_model = TyreDegradationModel(compound_slopes={"SOFT": 0.0, "MEDIUM": 0.0, "HARD": 0.0}) if no_tyre_deg else TyreDegradationModel()
        overtaking_model = OvertakingModel(base_dirty_air_delay=0.0) if no_traffic else OvertakingModel()

        self.simulator = MonteCarloSimulator(
            tyre_model=tyre_model,
            pace_model=BasePaceModel(),
            overtaking_model=overtaking_model,
        )

    def evaluate_race(self, race_id: str, origin_laps: Optional[List[int]] = None) -> Dict[str, Any]:
        """Run rolling-origin evaluation for a given race_id at specified origin laps."""
        state_engine = RaceStateEngine(self.conn)

        if not origin_laps:
            available_laps = [
                row[0]
                for row in self.conn.execute(
                    "SELECT DISTINCT lap_number FROM lap_data WHERE race_id = ? ORDER BY lap_number",
                    [race_id],
                ).fetchall()
            ]
            if available_laps:
                origin_laps = available_laps
            else:
                origin_laps = [1]

        evaluations_count = 0
        actual_finishes = []
        predicted_means = []
        brier_outcomes = []
        brier_probs = []
        rps_scores = []

        for lap in origin_laps:
            state = state_engine.reconstruct_state(race_id, lap_number=lap, mode=SimulationMode.DECISION_TIME)
            if not state or not state.drivers:
                continue

            target_driver = state.drivers[0].driver_id
            baseline_strat = CandidateStrategy(strategy_id="STAY_OUT", pit_laps=[])

            sim_res = self.simulator.run(
                race_state=state,
                candidate_strategies=[baseline_strat],
                target_driver_id=target_driver,
                num_simulations=500,
                seed=42,
            )

            if not sim_res.evaluations:
                continue

            eval_item = sim_res.evaluations[0]
            evaluations_count += 1

            # Actual finish position from database
            actual_finish = state.drivers[0].position
            predicted_mean = eval_item.expected_finish_pos

            actual_finishes.append(actual_finish)
            predicted_means.append(predicted_mean)

            # Brier Score components for P1 win
            brier_outcomes.append(1.0 if actual_finish == 1 else 0.0)
            brier_probs.append(eval_item.win_probability)

            # RPS
            rps = calculate_ranked_probability_score(actual_finish, eval_item.position_distribution)
            rps_scores.append(rps)

        rmse = calculate_rmse(np.array(actual_finishes), np.array(predicted_means))
        mae = calculate_mae(np.array(actual_finishes), np.array(predicted_means))
        brier = calculate_brier_score(np.array(brier_outcomes), np.array(brier_probs))
        mean_rps = float(np.mean(rps_scores)) if rps_scores else 0.0

        return {
            "race_id": race_id,
            "origin_laps_evaluated": len(origin_laps),
            "ablations": {
                "no_tyre_deg": self.no_tyre_deg,
                "no_traffic": self.no_traffic,
                "no_weather_markov": self.no_weather_markov,
            },
            "metrics": {
                "rmse": round(rmse, 3),
                "mae": round(mae, 3),
                "brier_score": round(brier, 4),
                "mean_rps": round(mean_rps, 4),
            },
        }
