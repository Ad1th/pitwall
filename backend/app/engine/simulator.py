"""
Vectorized Monte Carlo Race Simulator Kernel using Common Random Numbers (CRN).
Ref: docs/PRD.md Section 3.4 & docs/ARCHITECTURE.md Section 2.3
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np

from backend.app.schemas.state import RaceStateVector, DriverState
from backend.app.schemas.simulation import (
    CandidateStrategy,
    SimulationResponse,
    StrategyEvaluationResult,
)
from backend.app.models.tyre_deg import TyreDegradationModel
from backend.app.models.pace import BasePaceModel
from backend.app.models.overtaking import OvertakingModel

logger = logging.getLogger(__name__)

# F1 FIA points distribution for P1..P10
F1_POINTS_MAP = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}


class MonteCarloSimulator:
    """High-Performance Vectorized Monte Carlo Race Simulator Kernel."""

    def __init__(
        self,
        tyre_model: Optional[TyreDegradationModel] = None,
        pace_model: Optional[BasePaceModel] = None,
        overtaking_model: Optional[OvertakingModel] = None,
        risk_penalty_lambda: float = 0.05,
    ):
        self.tyre_model = tyre_model or TyreDegradationModel()
        self.pace_model = pace_model or BasePaceModel()
        self.overtaking_model = overtaking_model or OvertakingModel()
        self.risk_penalty_lambda = risk_penalty_lambda

    def _get_points(self, pos: int) -> int:
        return F1_POINTS_MAP.get(pos, 0)

    def run(
        self,
        race_state: RaceStateVector,
        candidate_strategies: List[CandidateStrategy],
        target_driver_id: str,
        num_simulations: int = 5000,
        seed: int = 42,
    ) -> SimulationResponse:
        """
        Run paired Monte Carlo simulations using Common Random Numbers (CRN).
        
        Evaluates candidate pit strategies under identical exogenous random seed sequences.
        """
        start_time = time.time()
        rng = np.random.default_rng(seed)

        drivers = race_state.drivers
        num_drivers = len(drivers)
        if num_drivers == 0:
            raise ValueError("RaceState contains zero drivers.")

        current_lap = race_state.lap_number
        total_laps = race_state.total_laps
        laps_to_sim = max(1, total_laps - current_lap + 1)

        # 1. Generate Common Random Numbers (CRN)
        # Exogenous pace noise: shape (num_simulations, laps_to_sim, num_drivers)
        crn_pace_noise = rng.normal(loc=0.0, scale=0.25, size=(num_simulations, laps_to_sim, num_drivers))
        # Exogenous pit stop duration noise: shape (num_simulations, num_drivers)
        crn_pit_noise = rng.lognormal(mean=0.0, sigma=0.1, size=(num_simulations, num_drivers))
        # Exogenous overtaking draw noise: shape (num_simulations, laps_to_sim, num_drivers)
        crn_overtake_draws = rng.uniform(0.0, 1.0, size=(num_simulations, laps_to_sim, num_drivers))

        driver_idx_map = {d.driver_id.upper(): idx for idx, d in enumerate(drivers)}
        target_driver_id_clean = target_driver_id.upper()
        target_idx = driver_idx_map.get(target_driver_id_clean, 0)

        evaluations: List[StrategyEvaluationResult] = []

        # 2. Simulate each candidate strategy under the EXACT SAME CRN
        for strategy in candidate_strategies:
            eval_res = self._simulate_single_strategy(
                race_state=race_state,
                strategy=strategy,
                target_driver_idx=target_idx,
                num_simulations=num_simulations,
                laps_to_sim=laps_to_sim,
                crn_pace_noise=crn_pace_noise,
                crn_pit_noise=crn_pit_noise,
                crn_overtake_draws=crn_overtake_draws,
            )
            evaluations.append(eval_res)

        elapsed_ms = (time.time() - start_time) * 1000.0

        return SimulationResponse(
            simulation_id=f"sim-{race_state.race_id}-{target_driver_id_clean}-l{current_lap}",
            race_id=race_state.race_id,
            target_driver_id=target_driver_id_clean,
            decision_lap=current_lap,
            mode=race_state.mode.value,
            execution_time_ms=elapsed_ms,
            evaluations=evaluations,
        )

    def _simulate_single_strategy(
        self,
        race_state: RaceStateVector,
        strategy: CandidateStrategy,
        target_driver_idx: int,
        num_simulations: int,
        laps_to_sim: int,
        crn_pace_noise: np.ndarray,
        crn_pit_noise: np.ndarray,
        crn_overtake_draws: np.ndarray,
    ) -> StrategyEvaluationResult:
        """Simulate a single candidate strategy across N iterations using CRN matrix operations."""
        num_drivers = len(race_state.drivers)
        current_lap = race_state.lap_number
        total_laps = race_state.total_laps

        # Initial state vectors across N simulations
        # positions: shape (num_simulations, num_drivers)
        positions = np.tile([d.position for d in race_state.drivers], (num_simulations, 1))
        tyre_ages = np.tile([d.tyre_age for d in race_state.drivers], (num_simulations, 1))
        compounds = [d.compound for d in race_state.drivers]
        
        # Target driver strategy adjustments
        target_compounds = list(compounds)
        planned_pit_laps = set(strategy.pit_laps)

        # Vector of accumulated cumulative race times for each driver in each sim
        cumulative_times = np.zeros((num_simulations, num_drivers))

        for lap_step in range(laps_to_sim):
            sim_lap = current_lap + lap_step

            # Check if target driver pits on sim_lap
            is_target_pit = sim_lap in planned_pit_laps

            for d_idx, d in enumerate(race_state.drivers):
                d_compound = target_compounds[d_idx]
                if d_idx == target_driver_idx and is_target_pit:
                    d_compound = strategy.target_compound or "HARD"
                    target_compounds[d_idx] = d_compound
                    tyre_ages[:, d_idx] = 0  # reset tyre age
                    pit_loss = 22.0 * crn_pit_noise[:, d_idx]
                    cumulative_times[:, d_idx] += pit_loss
                else:
                    tyre_ages[:, d_idx] += 1

                # Predict base pace + tyre degradation
                base_pace = self.pace_model.predict_base_pace(
                    circuit_id=race_state.race_id,
                    constructor_id=d.constructor_id,
                    driver_id=d.driver_id,
                    lap_number=sim_lap,
                    total_laps=total_laps,
                )

                # Degradation penalty (sample average tyre age for vectorized efficiency)
                avg_age = int(np.mean(tyre_ages[:, d_idx]))
                deg_penalty = self.tyre_model.predict_degradation(
                    compound=d_compound,
                    tyre_age=avg_age,
                    track_temp_c=race_state.weather.track_temp_c,
                )

                lap_pace = base_pace + deg_penalty + crn_pace_noise[:, lap_step, d_idx]
                cumulative_times[:, d_idx] += lap_pace

            # Rank drivers by cumulative time per simulation run
            sorted_indices = np.argsort(cumulative_times, axis=1)
            for sim_i in range(num_simulations):
                positions[sim_i, sorted_indices[sim_i]] = np.arange(1, num_drivers + 1)

        # Extract target driver finish positions across N simulations
        target_finish_positions = positions[:, target_driver_idx]

        # Calculate statistical metrics
        mean_finish = float(np.mean(target_finish_positions))
        std_finish = float(np.std(target_finish_positions))
        
        # 95% Confidence Interval for expected finish position mean (standard error of mean)
        sem = std_finish / np.sqrt(num_simulations) if num_simulations > 1 else 0.0
        ci95_lower = max(1.0, mean_finish - 1.96 * sem)
        ci95_upper = min(float(num_drivers), mean_finish + 1.96 * sem)

        # Outcome Prediction Quantiles (5th and 95th percentiles of outcome dispersion)
        q05 = float(np.percentile(target_finish_positions, 5))
        q95 = float(np.percentile(target_finish_positions, 95))

        # Outcome Probabilities
        win_prob = float(np.mean(target_finish_positions == 1))
        podium_prob = float(np.mean(target_finish_positions <= 3))
        points_prob = float(np.mean(target_finish_positions <= 10))
        dnf_prob = 0.0

        # Calculate Expected Points & Utility U(a) = E[Points] - lambda * Var(Position)
        points_array = np.array([self._get_points(p) for p in target_finish_positions])
        expected_points = float(np.mean(points_array))
        var_position = float(np.var(target_finish_positions))
        expected_utility = float(expected_points - (self.risk_penalty_lambda * var_position))

        # Position Distribution histogram mapping
        unique_pos, counts = np.unique(target_finish_positions, return_counts=True)
        pos_dist = {f"P{int(p)}": int(c) for p, c in zip(unique_pos, counts)}

        return StrategyEvaluationResult(
            strategy_id=strategy.strategy_id,
            expected_utility=round(expected_utility, 2),
            expected_finish_pos=round(mean_finish, 2),
            expected_finish_pos_ci95=[round(ci95_lower, 2), round(ci95_upper, 2)],
            outcome_prediction_quantiles=[round(q05, 1), round(q95, 1)],
            win_probability=round(win_prob, 4),
            podium_probability=round(podium_prob, 4),
            points_probability=round(points_prob, 4),
            dnf_probability=round(dnf_prob, 4),
            position_distribution=pos_dist,
            utility_regret=0.0,
            expected_position_delta=0.0,
        )
