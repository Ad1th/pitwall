"""
FastAPI Routes for Strategy Simulation and Counterfactual Evaluations.
Ref: docs/API.md Section 3.2
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from backend.app.db.connection import DatabaseManager
from backend.app.schemas.state import SimulationMode
from backend.app.schemas.simulation import (
    CandidateStrategy,
    SimulationResponse,
)
from backend.app.engine.state import RaceStateEngine
from backend.app.engine.simulator import MonteCarloSimulator
from backend.app.engine.counterfactual import CounterfactualEngine

router = APIRouter()


class SimulateRequest(BaseModel):
    race_id: str
    decision_lap: int
    target_driver_id: str
    mode: SimulationMode = SimulationMode.DECISION_TIME
    num_simulations: int = 1000
    seed: int = 42
    candidate_strategies: List[CandidateStrategy] = Field(default_factory=list)


class CounterfactualRequest(BaseModel):
    race_id: str
    decision_lap: int
    target_driver_id: str
    mode: SimulationMode = SimulationMode.DECISION_TIME
    num_simulations: int = 1000
    seed: int = 42
    actual_strategy: CandidateStrategy
    counterfactual_strategies: List[CandidateStrategy] = Field(default_factory=list)


@router.post("/simulate", response_model=SimulationResponse)
def run_simulation(req: SimulateRequest) -> SimulationResponse:
    """Run paired Monte Carlo strategy simulation (CRN) for a target driver."""
    db = DatabaseManager().connect()
    state_engine = RaceStateEngine(db)
    state = state_engine.reconstruct_state(req.race_id, req.decision_lap, mode=req.mode)
    if not state:
        raise HTTPException(
            status_code=404,
            detail=f"Race state for '{req.race_id}' at lap {req.decision_lap} not found.",
        )

    if not req.candidate_strategies:
        req.candidate_strategies = [
            CandidateStrategy(strategy_id="STAY_OUT", pit_laps=[]),
            CandidateStrategy(strategy_id="PIT_NOW_SOFT", pit_laps=[req.decision_lap], target_compound="SOFT"),
        ]

    simulator = MonteCarloSimulator()
    res = simulator.run(
        race_state=state,
        candidate_strategies=req.candidate_strategies,
        target_driver_id=req.target_driver_id,
        num_simulations=req.num_simulations,
        seed=req.seed,
    )
    return res


@router.post("/counterfactual", response_model=SimulationResponse)
def run_counterfactual(req: CounterfactualRequest) -> SimulationResponse:
    """Evaluate counterfactual race strategy vs actual historical decision."""
    db = DatabaseManager().connect()
    state_engine = RaceStateEngine(db)
    state = state_engine.reconstruct_state(req.race_id, req.decision_lap, mode=req.mode)
    if not state:
        raise HTTPException(
            status_code=404,
            detail=f"Race state for '{req.race_id}' at lap {req.decision_lap} not found.",
        )

    cf_engine = CounterfactualEngine()
    res = cf_engine.evaluate_counterfactual(
        race_state=state,
        target_driver_id=req.target_driver_id,
        actual_strategy=req.actual_strategy,
        counterfactual_strategies=req.counterfactual_strategies,
        num_simulations=req.num_simulations,
        seed=req.seed,
    )
    return res
