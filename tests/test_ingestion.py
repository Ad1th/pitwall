"""
Stage 1 Ingestion Pipeline Unit & Integration Tests.
Ref: docs/DEVELOPMENT_PLAN.md Stage 1
"""

import os
import tempfile
import pytest
import duckdb

from backend.app.db.schema import get_db_connection, init_db
from backend.app.ingestion.normalizer import normalize_compound, timedelta_to_seconds, clean_lap_record
from backend.app.ingestion.jolpica_adapter import JolpicaAdapter
from backend.app.ingestion.openf1_adapter import OpenF1Adapter
from backend.app.ingestion.fastf1_adapter import FastF1Adapter
from scripts.seed_db import seed_race, BENCHMARK_RACES


@pytest.fixture
def temp_db():
    """Fixture creating temporary DuckDB database file."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as tmp:
        tmp_path = tmp.name
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    conn = get_db_connection(tmp_path)
    yield conn
    conn.close()
    if os.path.exists(tmp_path):
        os.remove(tmp_path)


def test_schema_initialization(temp_db):
    """Verify DuckDB tables and view are initialized cleanly."""
    tables = temp_db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
    ).fetchall()
    table_names = [t[0] for t in tables]

    assert "circuits" in table_names
    assert "races" in table_names
    assert "drivers" in table_names
    assert "constructors" in table_names
    assert "lap_data" in table_names
    assert "pit_stops" in table_names
    assert "weather_telemetry" in table_names
    assert "simulation_runs" in table_names
    assert "strategy_evaluations" in table_names

    # Check view
    views = temp_db.execute(
        "SELECT table_name FROM information_schema.views WHERE table_schema='main'"
    ).fetchall()
    view_names = [v[0] for v in views]
    assert "v_race_state_snapshot" in view_names


def test_normalizer_compounds():
    """Verify tyre compound string normalization."""
    assert normalize_compound("Soft") == "SOFT"
    assert normalize_compound("MEDIUM") == "MEDIUM"
    assert normalize_compound("Hard") == "HARD"
    assert normalize_compound("Inter") == "INTERMEDIATE"
    assert normalize_compound("Intermediate") == "INTERMEDIATE"
    assert normalize_compound("Full Wet") == "WET"
    assert normalize_compound(None) == "UNKNOWN"


def test_normalizer_timedelta():
    """Verify timedelta to seconds conversion."""
    assert timedelta_to_seconds(87.214) == 87.214
    assert timedelta_to_seconds(None) is None


def test_clean_lap_record():
    """Verify raw lap dict cleaning."""
    raw = {
        "Driver": "HAM",
        "Team": "Mercedes",
        "LapNumber": 53,
        "Position": 1,
        "LapTime": 87.214,
        "Compound": "HARD",
        "TyreLife": 39,
        "Stint": 2,
        "TrackStatus": "4",
        "IsAccurate": True,
    }
    cleaned = clean_lap_record(raw, "2021-abu-dhabi")
    assert cleaned["race_id"] == "2021-abu-dhabi"
    assert cleaned["driver_id"] == "HAM"
    assert cleaned["constructor_id"] == "mercedes"
    assert cleaned["lap_number"] == 53
    assert cleaned["compound"] == "HARD"
    assert cleaned["tyre_age_laps"] == 39
    assert cleaned["stint_number"] == 2
    assert cleaned["is_accurate"] is True


def test_openf1_adapter_pre2023():
    """Verify OpenF1 returns empty list for pre-2023 races (supplemental 2023+ only)."""
    adapter = OpenF1Adapter()
    res = adapter.fetch_session_telemetry(2021, "9999")
    assert res == []


def test_offline_seed_abu_dhabi(temp_db):
    """Test offline seeding of 2021 Abu Dhabi benchmark race."""
    success = seed_race("2021-abu-dhabi", temp_db, force_offline=True)
    assert success is True

    # Verify DuckDB records inserted
    races = temp_db.execute("SELECT * FROM races WHERE race_id='2021-abu-dhabi'").fetchall()
    assert len(races) == 1
    assert races[0][1] == 2021  # year
    assert races[0][2] == 22    # round

    drivers = temp_db.execute("SELECT code FROM drivers").fetchall()
    driver_codes = [d[0] for d in drivers]
    assert "HAM" in driver_codes
    assert "VER" in driver_codes

    laps = temp_db.execute("SELECT * FROM lap_data WHERE race_id='2021-abu-dhabi'").fetchall()
    assert len(laps) >= 2


def test_offline_seed_all_benchmark_races(temp_db):
    """Test offline seeding of all 4 PRD benchmark races."""
    for slug in BENCHMARK_RACES.keys():
        success = seed_race(slug, temp_db, force_offline=True)
        assert success is True

    races_count = temp_db.execute("SELECT COUNT(*) FROM races").fetchone()[0]
    assert races_count == 4
