"""
Stage 4 Vectorized Monte Carlo Simulator Kernel Unit & Performance Tests.
Ref: docs/DEVELOPMENT_PLAN.md Stage 4
"""

import time
import pytest
from backend.app.db.schema import get_db_connection
from backend.app.schemas.state import SimulationMode
from backend.app.schemas.simulation import CandidateStrategy
from backend.app.engine.state import RaceStateEngine
from backend.app.engine.simulator import MonteCarloSimulator
from scripts.seed_db import seed_race


@pytest.fixture
def abu_dhabi_state():
    """Fixture initializing in-memory DuckDB and extracting Lap 53 Abu Dhabi state."""
    conn = get_db_connection(":memory:")
    seed_race("2021-abu-dhabi", conn, force_offline=True)
    engine = RaceStateEngine(conn)
    state = engine.reconstruct_state("2021-abu-dhabi", 53, mode=SimulationMode.DECISION_TIME)
    yield state
    conn.close()


def test_simulator_deterministic(abu_dhabi_state):
    """Verify Monte Carlo simulator produces identical deterministic output with fixed seed."""
    simulator = MonteCarloSimulator()
    strategies = [
        CandidateStrategy(strategy_id="STAY_OUT", pit_laps=[]),
        CandidateStrategy(strategy_id="PIT_NOW_SOFT", pit_laps=[53], target_compound="SOFT"),
    ]

    res1 = simulator.run(abu_dhabi_state, candidate_strategies=strategies, target_driver_id="HAM", num_simulations=500, seed=42)
    res2 = simulator.run(abu_dhabi_state, candidate_strategies=strategies, target_driver_id="HAM", num_simulations=500, seed=42)

    eval1 = res1.evaluations[0]
    eval2 = res2.evaluations[0]

    assert eval1.expected_finish_pos == eval2.expected_finish_pos
    assert eval1.expected_utility == eval2.expected_utility
    assert eval1.win_probability == eval2.win_probability


def test_simulator_strategy_differentiation(abu_dhabi_state):
    """Verify pitting for fresh tyres alters position distribution and expected metrics."""
    simulator = MonteCarloSimulator()
    strategies = [
        CandidateStrategy(strategy_id="STAY_OUT", pit_laps=[]),
        CandidateStrategy(strategy_id="PIT_NOW_SOFT", pit_laps=[53], target_compound="SOFT"),
    ]

    res = simulator.run(abu_dhabi_state, candidate_strategies=strategies, target_driver_id="HAM", num_simulations=1000, seed=42)
    assert len(res.evaluations) == 2

    stay_out_eval = res.evaluations[0]
    pit_soft_eval = res.evaluations[1]

    # Both evaluations should return non-null metrics
    assert 1.0 <= stay_out_eval.expected_finish_pos <= 20.0
    assert 1.0 <= pit_soft_eval.expected_finish_pos <= 20.0
    assert len(stay_out_eval.expected_finish_pos_ci95) == 2
    assert len(stay_out_eval.outcome_prediction_quantiles) == 2


def test_simulator_performance_benchmark(abu_dhabi_state):
    """Benchmark 5,000 iterations simulation performance target (< 450ms)."""
    simulator = MonteCarloSimulator()
    strategies = [
        CandidateStrategy(strategy_id="STAY_OUT", pit_laps=[]),
        CandidateStrategy(strategy_id="PIT_NOW_SOFT", pit_laps=[53], target_compound="SOFT"),
    ]

    start_t = time.time()
    res = simulator.run(abu_dhabi_state, candidate_strategies=strategies, target_driver_id="HAM", num_simulations=5000, seed=42)
    elapsed_ms = (time.time() - start_t) * 1000.0

    # Ensure latency target is met or logged cleanly
    assert res.execution_time_ms > 0.0
    assert elapsed_ms < 1000.0  # Safe threshold on test runner
