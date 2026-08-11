"""
Stage 5 Strategy Optimizer Unit Tests.
Ref: docs/DEVELOPMENT_PLAN.md Stage 5
"""

import pytest
from backend.app.db.schema import get_db_connection
from backend.app.schemas.state import SimulationMode
from backend.app.engine.state import RaceStateEngine
from backend.app.engine.optimizer import StrategyOptimizer
from scripts.seed_db import seed_race


@pytest.fixture
def abu_dhabi_state():
    conn = get_db_connection(":memory:")
    seed_race("2021-abu-dhabi", conn, force_offline=True)
    engine = RaceStateEngine(conn)
    state = engine.reconstruct_state("2021-abu-dhabi", 53, mode=SimulationMode.DECISION_TIME)
    yield state
    conn.close()


def test_optimizer_candidate_generation():
    optimizer = StrategyOptimizer()
    candidates = optimizer.generate_candidate_strategies(current_lap=53, total_laps=58, step_size=3)

    assert len(candidates) > 1
    assert candidates[0].strategy_id == "STAY_OUT"


def test_optimizer_execution(abu_dhabi_state):
    optimizer = StrategyOptimizer()
    res = optimizer.optimize(
        race_state=abu_dhabi_state,
        target_driver_id="HAM",
        coarse_sims=100,
        fine_sims=300,
        seed=42,
    )

    assert res is not None
    assert len(res.evaluations) > 0
    # Evaluations should be ranked or valid
    best_eval = max(res.evaluations, key=lambda x: x.expected_utility)
    assert best_eval.expected_utility >= 0.0
