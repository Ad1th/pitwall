"""
Counterfactual Regret Engine & Statistical Indistinguishability Evaluator.
Ref: docs/MODELING.md Section 5 & docs/ARCHITECTURE.md Section 2.5
"""

import logging
from typing import List, Optional
import numpy as np

from backend.app.schemas.state import RaceStateVector
from backend.app.schemas.simulation import (
    CandidateStrategy,
    SimulationResponse,
    StrategyEvaluationResult,
)
from backend.app.engine.simulator import MonteCarloSimulator

logger = logging.getLogger(__name__)


class CounterfactualEngine:
    """Evaluates counterfactual race strategies using CRN paired Monte Carlo simulations."""

    def __init__(self, simulator: Optional[MonteCarloSimulator] = None):
        self.simulator = simulator or MonteCarloSimulator()

    def evaluate_counterfactual(
        self,
        race_state: RaceStateVector,
        target_driver_id: str,
        actual_strategy: CandidateStrategy,
        counterfactual_strategies: List[CandidateStrategy],
        num_simulations: int = 5000,
        seed: int = 42,
    ) -> SimulationResponse:
        """
        Run paired CRN counterfactual evaluations.
        
        Computes Utility Regret U(a*) - U(a) >= 0, Expected Position Delta, and
        evaluates precise statistical indistinguishability (0 in CI_95(Delta U)).
        """
        # Build candidate list ensuring actual_strategy is evaluated
        all_candidates = [actual_strategy]
        for cs in counterfactual_strategies:
            if cs.strategy_id != actual_strategy.strategy_id:
                all_candidates.append(cs)

        # Run paired CRN simulation across all candidate strategies
        sim_response = self.simulator.run(
            race_state=race_state,
            candidate_strategies=all_candidates,
            target_driver_id=target_driver_id,
            num_simulations=num_simulations,
            seed=seed,
        )

        evaluations = sim_response.evaluations
        if not evaluations:
            return sim_response

        # 1. Identify optimal strategy a* = argmax U(a) under model objective
        optimal_eval = max(evaluations, key=lambda x: x.expected_utility)
        u_star = optimal_eval.expected_utility
        pos_star = optimal_eval.expected_finish_pos

        # 2. Enrich evaluations with Utility Regret, Expected Position Delta, and Indistinguishability
        for ev in evaluations:
            # Utility Regret U(a*) - U(a) >= 0
            regret = max(0.0, u_star - ev.expected_utility)
            ev.utility_regret = round(regret, 2)

            # Expected Position Delta E[Pos(a)] - E[Pos(a*)]
            pos_delta = ev.expected_finish_pos - pos_star
            ev.expected_position_delta = round(pos_delta, 2)

            # Pairwise 95% CI for Delta U = U(a*) - U(a)
            # Estimate pairwise standard error
            se_diff = (
                abs(optimal_eval.expected_finish_pos_ci95[1] - optimal_eval.expected_finish_pos_ci95[0])
                + abs(ev.expected_finish_pos_ci95[1] - ev.expected_finish_pos_ci95[0])
            ) / 3.92

            ci95_lower = regret - 1.96 * se_diff
            ci95_upper = regret + 1.96 * se_diff

            # Precise Indistinguishability Rule: 0 in CI95(Delta U)
            if ev.strategy_id == optimal_eval.strategy_id:
                ev.is_statistically_distinct = True
            else:
                is_distinct = not (ci95_lower <= 0.0 <= ci95_upper)
                ev.is_statistically_distinct = is_distinct

        return sim_response
