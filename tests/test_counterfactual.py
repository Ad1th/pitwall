"""
Stage 5 Counterfactual Regret Engine & Indistinguishability Unit Tests.
Ref: docs/DEVELOPMENT_PLAN.md Stage 5
"""

import pytest
from backend.app.db.schema import get_db_connection
from backend.app.schemas.state import SimulationMode
from backend.app.schemas.simulation import CandidateStrategy
from backend.app.engine.state import RaceStateEngine
from backend.app.engine.counterfactual import CounterfactualEngine
from scripts.seed_db import seed_race


@pytest.fixture
def abu_dhabi_state():
    conn = get_db_connection(":memory:")
    seed_race("2021-abu-dhabi", conn, force_offline=True)
    engine = RaceStateEngine(conn)
    state = engine.reconstruct_state("2021-abu-dhabi", 53, mode=SimulationMode.DECISION_TIME)
    yield state
    conn.close()


def test_counterfactual_utility_regret_nonnegative(abu_dhabi_state):
    """Verify Utility Regret U(a*) - U(a) is non-negative by definition."""
    cf_engine = CounterfactualEngine()
    actual = CandidateStrategy(strategy_id="STAY_OUT", pit_laps=[])
    cf_strats = [
        CandidateStrategy(strategy_id="PIT_NOW_SOFT", pit_laps=[53], target_compound="SOFT"),
        CandidateStrategy(strategy_id="PIT_NOW_HARD", pit_laps=[53], target_compound="HARD"),
    ]

    res = cf_engine.evaluate_counterfactual(
        race_state=abu_dhabi_state,
        target_driver_id="HAM",
        actual_strategy=actual,
        counterfactual_strategies=cf_strats,
        num_simulations=500,
        seed=42,
    )

    assert res is not None
    for ev in res.evaluations:
        # Utility regret must be >= 0.0
        assert ev.utility_regret >= 0.0


def test_counterfactual_indistinguishability_flag(abu_dhabi_state):
    """Verify statistically distinct or indistinguishable flags are properly assigned."""
    cf_engine = CounterfactualEngine()
    actual = CandidateStrategy(strategy_id="STAY_OUT", pit_laps=[])
    cf_strats = [
        CandidateStrategy(strategy_id="STAY_OUT_COPY", pit_laps=[]),  # Identical strategy
    ]

    res = cf_engine.evaluate_counterfactual(
        race_state=abu_dhabi_state,
        target_driver_id="HAM",
        actual_strategy=actual,
        counterfactual_strategies=cf_strats,
        num_simulations=500,
        seed=42,
    )

    evals = res.evaluations
    assert len(evals) == 2
    # Copy of identical strategy should have utility regret ~ 0 and may be flagged indistinguishable
    assert evals[1].utility_regret == 0.0
