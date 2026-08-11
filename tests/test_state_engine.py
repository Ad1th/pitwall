"""
Stage 2 RaceState Reconstruction & Dual Mode Engine Unit Tests.
Ref: docs/DEVELOPMENT_PLAN.md Stage 2
"""

import pytest
from backend.app.db.schema import get_db_connection
from backend.app.schemas.state import SimulationMode, RaceStateVector
from backend.app.engine.state import RaceStateEngine
from scripts.seed_db import seed_race


@pytest.fixture
def seeded_db():
    """Fixture initializing temporary in-memory DuckDB seeded with 2021 Abu Dhabi race."""
    conn = get_db_connection(":memory:")
    seed_race("2021-abu-dhabi", conn, force_offline=True)
    yield conn
    conn.close()


def test_reconstruct_state_abu_dhabi(seeded_db):
    """Test RaceState reconstruction for Abu Dhabi 2021 Lap 53."""
    engine = RaceStateEngine(seeded_db)
    state = engine.reconstruct_state("2021-abu-dhabi", 53, mode=SimulationMode.DECISION_TIME)

    assert state is not None
    assert isinstance(state, RaceStateVector)
    assert state.race_id == "2021-abu-dhabi"
    assert state.lap_number == 53
    assert state.total_laps == 58
    assert state.mode == SimulationMode.DECISION_TIME
    assert state.track_status == "4"  # Safety Car status

    # Verify drivers
    assert len(state.drivers) >= 2
    ham = state.get_driver("HAM")
    ver = state.get_driver("VER")

    assert ham is not None
    assert ham.position == 1
    assert ham.compound == "HARD"
    assert ham.tyre_age == 39
    assert ham.stint_number == 2
    assert ham.gap_to_leader_sec == 0.0

    assert ver is not None
    assert ver.position == 2
    assert ver.compound == "HARD"
    assert ver.tyre_age == 17
    assert ver.stint_number == 3
    assert ver.gap_to_leader_sec == 11.942


def test_reconstruct_state_modes(seeded_db):
    """Test decision_time vs hindsight mode selection."""
    engine = RaceStateEngine(seeded_db)
    dt_state = engine.reconstruct_state("2021-abu-dhabi", 53, mode=SimulationMode.DECISION_TIME)
    hs_state = engine.reconstruct_state("2021-abu-dhabi", 53, mode=SimulationMode.HINDSIGHT)

    assert dt_state.mode == SimulationMode.DECISION_TIME
    assert hs_state.mode == SimulationMode.HINDSIGHT


def test_nonexistent_race(seeded_db):
    """Test graceful handling of unknown race ID."""
    engine = RaceStateEngine(seeded_db)
    state = engine.reconstruct_state("2025-invalid-race", 10)
    assert state is None
