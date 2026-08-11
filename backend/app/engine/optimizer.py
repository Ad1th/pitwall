"""
Two-Stage Coarse-to-Fine Strategy Optimizer.
Ref: docs/MODELING.md Section 5 & docs/ARCHITECTURE.md Section 2.4
"""

import logging
from typing import List, Optional, Tuple
from backend.app.schemas.state import RaceStateVector
from backend.app.schemas.simulation import CandidateStrategy, SimulationResponse
from backend.app.engine.simulator import MonteCarloSimulator

logger = logging.getLogger(__name__)

SUPPORTED_COMPOUNDS = ["SOFT", "MEDIUM", "HARD"]


class StrategyOptimizer:
    """Optimizes race strategy using a two-stage coarse-to-fine search."""

    def __init__(self, simulator: Optional[MonteCarloSimulator] = None):
        self.simulator = simulator or MonteCarloSimulator()

    def generate_candidate_strategies(
        self, current_lap: int, total_laps: int, step_size: int = 3
    ) -> List[CandidateStrategy]:
        """Generate feasible 1-stop and 2-stop candidate pit strategies."""
        candidates: List[CandidateStrategy] = []
        laps_remaining = total_laps - current_lap

        # 0-Stop / Stay Out baseline
        candidates.append(CandidateStrategy(strategy_id="STAY_OUT", pit_laps=[]))

        if laps_remaining < 2:
            return candidates

        # 1-Stop Strategies
        for pit_lap in range(current_lap, total_laps, step_size):
            for compound in SUPPORTED_COMPOUNDS:
                strat_id = f"PIT_L{pit_lap}_{compound}"
                candidates.append(
                    CandidateStrategy(
                        strategy_id=strat_id,
                        pit_laps=[pit_lap],
                        target_compound=compound,
                    )
                )

        # 2-Stop Strategies (for races with > 15 laps remaining)
        if laps_remaining >= 15:
            mid_lap = current_lap + (laps_remaining // 2)
            for compound in SUPPORTED_COMPOUNDS:
                strat_id = f"PIT_L{current_lap}_L{mid_lap}_{compound}"
                candidates.append(
                    CandidateStrategy(
                        strategy_id=strat_id,
                        pit_laps=[current_lap, mid_lap],
                        target_compound=compound,
                    )
                )

        return candidates

    def optimize(
        self,
        race_state: RaceStateVector,
        target_driver_id: str,
        coarse_sims: int = 500,
        fine_sims: int = 5000,
        seed: int = 42,
    ) -> SimulationResponse:
        """
        Execute two-stage strategy optimization:
        Stage 1: Coarse Grid Search (coarse_sims runs) across candidate domain.
        Stage 2: Fine Refinement (fine_sims runs) on top 5 candidate strategies.
        """
        current_lap = race_state.lap_number
        total_laps = race_state.total_laps

        # 1. Generate coarse candidate strategies
        coarse_candidates = self.generate_candidate_strategies(current_lap, total_laps, step_size=3)

        # 2. Stage 1: Fast Coarse Simulation Screening
        coarse_res = self.simulator.run(
            race_state=race_state,
            candidate_strategies=coarse_candidates,
            target_driver_id=target_driver_id,
            num_simulations=coarse_sims,
            seed=seed,
        )

        # Rank candidates by coarse expected utility U(a)
        sorted_evals = sorted(coarse_res.evaluations, key=lambda x: x.expected_utility, reverse=True)
        top_evals = sorted_evals[:5]

        # Map back to candidate objects
        top_strategy_ids = {e.strategy_id for e in top_evals}
        refined_candidates = [c for c in coarse_candidates if c.strategy_id in top_strategy_ids]

        # 3. Stage 2: Full Fine Simulation Evaluation
        fine_res = self.simulator.run(
            race_state=race_state,
            candidate_strategies=refined_candidates,
            target_driver_id=target_driver_id,
            num_simulations=fine_sims,
            seed=seed,
        )

        return fine_res
