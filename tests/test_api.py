"""
Stage 6 FastAPI Backend REST Endpoints Integration Tests.
Ref: docs/DEVELOPMENT_PLAN.md Stage 6
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.schema import get_db_connection
from scripts.seed_db import seed_race


@pytest.fixture(scope="module", autouse=True)
def seed_test_database():
    """Seed test database once before running API tests."""
    conn = get_db_connection("data/pitwall.duckdb")
    seed_race("2021-abu-dhabi", conn, force_offline=True)
    conn.close()


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check route."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_list_races_endpoint(client):
    """Test list races route."""
    response = client.get("/api/v1/races")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    race_ids = [r["race_id"] for r in data]
    assert "2021-abu-dhabi" in race_ids


def test_get_race_endpoint(client):
    """Test get race details route."""
    response = client.get("/api/v1/races/2021-abu-dhabi")
    assert response.status_code == 200
    data = response.json()
    assert data["race_id"] == "2021-abu-dhabi"
    assert data["year"] == 2021


def test_get_race_state_endpoint(client):
    """Test get race state reconstruction route."""
    response = client.get("/api/v1/races/2021-abu-dhabi/state/53?mode=decision_time")
    assert response.status_code == 200
    data = response.json()
    assert data["race_id"] == "2021-abu-dhabi"
    assert data["lap_number"] == 53
    assert data["mode"] == "decision_time"
    assert len(data["drivers"]) >= 2


def test_simulate_endpoint(client):
    """Test POST simulation route."""
    payload = {
        "race_id": "2021-abu-dhabi",
        "decision_lap": 53,
        "target_driver_id": "HAM",
        "mode": "decision_time",
        "num_simulations": 100,
        "seed": 42,
        "candidate_strategies": [
            {"strategy_id": "STAY_OUT", "pit_laps": []},
            {"strategy_id": "PIT_NOW_SOFT", "pit_laps": [53], "target_compound": "SOFT"},
        ],
    }
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["race_id"] == "2021-abu-dhabi"
    assert len(data["evaluations"]) == 2


def test_counterfactual_endpoint(client):
    """Test POST counterfactual evaluation route."""
    payload = {
        "race_id": "2021-abu-dhabi",
        "decision_lap": 53,
        "target_driver_id": "HAM",
        "mode": "decision_time",
        "num_simulations": 100,
        "seed": 42,
        "actual_strategy": {"strategy_id": "STAY_OUT", "pit_laps": []},
        "counterfactual_strategies": [
            {"strategy_id": "PIT_NOW_SOFT", "pit_laps": [53], "target_compound": "SOFT"}
        ],
    }
    response = client.post("/api/v1/counterfactual", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["evaluations"]) == 2


def test_autopsy_endpoint(client):
    """Test GET race autopsy route."""
    response = client.get("/api/v1/races/2021-abu-dhabi/autopsy?mode=decision_time")
    assert response.status_code == 200
    data = response.json()
    assert data["race_id"] == "2021-abu-dhabi"
    assert "key_decisions" in data


def test_invalid_race_endpoint(client):
    """Test 404 response for invalid race ID."""
    response = client.get("/api/v1/races/2025-invalid/state/10")
    assert response.status_code == 404
