# PITWALL — API Specification

`docs/API.md`

---

## 1. Overview & Standards

The PITWALL Backend API is served via FastAPI at base URL `/api/v1`. All request and response bodies use strict JSON formatting. HTTP error responses adhere to standard HTTP status codes and return detailed RFC 7807 error objects.

*Note: All numerical values appearing in example payloads below are strictly `[ILLUSTRATIVE EXAMPLE PAYLOADS]` for schema demonstration purposes.*

---

## 2. API Endpoints Matrix

| HTTP Method | Endpoint Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/races` | List all available historical F1 races in database. |
| `GET` | `/api/v1/races/{race_id}` | Get race metadata, total laps, circuit profile, and driver grid. |
| `GET` | `/api/v1/races/{race_id}/state/{lap}` | Get exact reconstructed \( \text{RaceState}(t) \) at lap \( t \). |
| `POST` | `/api/v1/simulate` | Run Monte Carlo strategy simulation for a driver at a specific lap. |
| `POST` | `/api/v1/counterfactual` | Evaluate counterfactual decision vs actual historical outcome. |
| `GET` | `/api/v1/races/{race_id}/autopsy` | Run automated historical race autopsy; rank key decision points by regret. |
| `GET` | `/api/v1/models/metrics` | Retrieve cross-validation accuracy metrics for tyre, pace, and overtaking models. |
| `GET` | `/api/v1/health` | Health check endpoint. |

---

## 3. Endpoint Schema Definitions

### 3.1 `GET /api/v1/races/{race_id}/state/{lap}`

**Parameters**:
- `race_id` (path, string): Unique race slug (e.g., `'2021-abu-dhabi'`).
- `lap` (path, int): Lap number \( t \in [1, N_{\text{total}}] \).

**Response Schema (`200 OK`) `[ILLUSTRATIVE EXAMPLE PAYLOAD]`**:
```json
{
  "race_id": "2021-abu-dhabi",
  "lap_number": 53,
  "track_status": "4",
  "weather": {
    "track_temp_c": 29.4,
    "air_temp_c": 24.1,
    "rainfall": false
  },
  "drivers": [
    {
      "driver_id": "HAM",
      "position": 1,
      "constructor_id": "mercedes",
      "compound": "HARD",
      "tyre_age": 39,
      "stint_number": 2,
      "gap_to_leader_sec": 0.0,
      "interval_ahead_sec": 0.0,
      "last_lap_time_sec": 87.214
    },
    {
      "driver_id": "VER",
      "position": 2,
      "constructor_id": "red_bull",
      "compound": "HARD",
      "tyre_age": 17,
      "stint_number": 3,
      "gap_to_leader_sec": 11.942,
      "interval_ahead_sec": 11.942,
      "last_lap_time_sec": 86.810
    }
  ]
}
```

---

### 3.2 `POST /api/v1/simulate`

**Request Body**:
```json
{
  "race_id": "2021-abu-dhabi",
  "decision_lap": 53,
  "target_driver_id": "HAM",
  "mode": "decision_time",
  "num_simulations": 5000,
  "candidate_strategies": [
    {
      "strategy_id": "STAY_OUT",
      "pit_laps": [],
      "target_compound": null
    },
    {
      "strategy_id": "PIT_NOW_SOFT",
      "pit_laps": [53],
      "target_compound": "SOFT"
    }
  ]
}
```

**Response Schema (`200 OK`) `[ILLUSTRATIVE EXAMPLE PAYLOAD]`**:
```json
{
  "simulation_id": "sim-2021-ad-ham-l53",
  "race_id": "2021-abu-dhabi",
  "target_driver_id": "HAM",
  "decision_lap": 53,
  "mode": "decision_time",
  "execution_time_ms": 284.5,
  "evaluations": [
    {
      "strategy_id": "STAY_OUT",
      "expected_finish_pos": 1.84,
      "confidence_interval_95": [1.00, 2.00],
      "win_probability": 0.32,
      "podium_probability": 1.00,
      "position_distribution": {
        "P1": 1600,
        "P2": 3400
      },
      "strategy_regret_vs_optimal": 0.68,
      "is_statistically_distinct": true
    },
    {
      "strategy_id": "PIT_NOW_SOFT",
      "expected_finish_pos": 1.16,
      "confidence_interval_95": [1.00, 2.00],
      "win_probability": 0.84,
      "podium_probability": 1.00,
      "position_distribution": {
        "P1": 4200,
        "P2": 800
      },
      "strategy_regret_vs_optimal": 0.00,
      "is_statistically_distinct": true
    }
  ]
}
```

---

### 3.3 `GET /api/v1/races/{race_id}/autopsy`

**Query Parameters**:
- `mode` (optional, string): `"decision_time"` (default) or `"hindsight"`.

**Response Schema (`200 OK`) `[ILLUSTRATIVE EXAMPLE PAYLOAD]`**:
```json
{
  "race_id": "2021-abu-dhabi",
  "mode": "decision_time",
  "total_laps": 58,
  "winner": "VER",
  "key_decisions": [
    {
      "rank": 1,
      "lap_number": 53,
      "driver_id": "HAM",
      "team": "Mercedes",
      "actual_decision": "STAY_OUT",
      "recommended_decision": "PIT_NOW_SOFT",
      "estimated_regret_positions": 0.68,
      "regret_confidence_interval_95": [0.24, 1.12],
      "is_statistically_distinct": true,
      "primary_contributing_factors": [
        "Safety car tire age delta advantage under model assumptions",
        "Dirty air friction mitigation on restart lap",
        "Probabilistic position transition model output"
      ]
    }
  ]
}
```

---

## 4. Error Handling Schema

```json
{
  "error": {
    "code": "RACE_NOT_FOUND",
    "message": "Race ID '2025-monaco' was not found in DuckDB database.",
    "details": {
      "requested_race": "2025-monaco",
      "available_seasons": [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    }
  }
}
```
