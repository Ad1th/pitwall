"""
Pydantic Schemas and Data Models for Strategy Simulation and Monte Carlo Results.
Ref: docs/PRD.md Section 3.4 & docs/ARCHITECTURE.md Section 2.3
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CandidateStrategy(BaseModel):
    strategy_id: str
    pit_laps: List[int] = Field(default_factory=list)
    target_compound: Optional[str] = "HARD"


class StrategyEvaluationResult(BaseModel):
    strategy_id: str
    expected_utility: float
    expected_finish_pos: float
    expected_finish_pos_ci95: List[float]  # [lower_bound, upper_bound] for mean
    outcome_prediction_quantiles: List[float]  # [q05, q95] outcome percentiles
    win_probability: float
    podium_probability: float
    points_probability: float
    dnf_probability: float
    position_distribution: Dict[str, int]  # e.g. {"P1": 1600, "P2": 3400}
    utility_regret: float = 0.0
    expected_position_delta: float = 0.0
    is_statistically_distinct: Optional[bool] = None


class SimulationResponse(BaseModel):
    simulation_id: str
    race_id: str
    target_driver_id: str
    decision_lap: int
    mode: str = "decision_time"
    execution_time_ms: float
    evaluations: List[StrategyEvaluationResult] = Field(default_factory=list)
