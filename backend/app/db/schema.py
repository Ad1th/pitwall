"""
PITWALL DuckDB Schema Definitions and Database Initialization.
Ref: docs/DATABASE.md
"""

import os
import duckdb

CREATE_CIRCUITS_TABLE = """
CREATE TABLE IF NOT EXISTS circuits (
    circuit_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    location VARCHAR,
    country VARCHAR,
    latitude DOUBLE,
    longitude DOUBLE,
    length_km DOUBLE NOT NULL,
    turns INT,
    pit_lane_loss_sec DOUBLE,
    base_degradation_mult DOUBLE DEFAULT 1.0,
    overtaking_difficulty_mult DOUBLE DEFAULT 1.0
);
"""

CREATE_RACES_TABLE = """
CREATE TABLE IF NOT EXISTS races (
    race_id VARCHAR PRIMARY KEY,
    year INT NOT NULL,
    round INT NOT NULL,
    circuit_id VARCHAR REFERENCES circuits(circuit_id),
    name VARCHAR NOT NULL,
    date DATE NOT NULL,
    total_laps INT NOT NULL,
    official_winner_driver_id VARCHAR
);
"""

CREATE_DRIVERS_TABLE = """
CREATE TABLE IF NOT EXISTS drivers (
    driver_id VARCHAR PRIMARY KEY,
    code VARCHAR(3) UNIQUE NOT NULL,
    permanent_number INT,
    first_name VARCHAR,
    last_name VARCHAR,
    nationality VARCHAR
);
"""

CREATE_CONSTRUCTORS_TABLE = """
CREATE TABLE IF NOT EXISTS constructors (
    constructor_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    nationality VARCHAR
);
"""

CREATE_LAP_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS lap_data (
    race_id VARCHAR NOT NULL,
    driver_id VARCHAR NOT NULL,
    constructor_id VARCHAR NOT NULL,
    lap_number INT NOT NULL,
    position INT,
    lap_time_sec DOUBLE,
    sector1_sec DOUBLE,
    sector2_sec DOUBLE,
    sector3_sec DOUBLE,
    speed_st DOUBLE,
    compound VARCHAR(15),
    tyre_age_laps INT,
    stint_number INT,
    is_pit_lap BOOLEAN DEFAULT FALSE,
    is_accurate BOOLEAN DEFAULT TRUE,
    track_status VARCHAR(10) DEFAULT '1',
    gap_to_leader_sec DOUBLE,
    interval_to_ahead_sec DOUBLE,
    PRIMARY KEY (race_id, driver_id, lap_number)
);
"""

CREATE_PIT_STOPS_TABLE = """
CREATE TABLE IF NOT EXISTS pit_stops (
    race_id VARCHAR NOT NULL,
    driver_id VARCHAR NOT NULL,
    stop_number INT NOT NULL,
    lap_number INT NOT NULL,
    duration_sec DOUBLE NOT NULL,
    total_pit_lane_time_sec DOUBLE,
    PRIMARY KEY (race_id, driver_id, stop_number)
);
"""

CREATE_WEATHER_TELEMETRY_TABLE = """
CREATE TABLE IF NOT EXISTS weather_telemetry (
    race_id VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    air_temp_c DOUBLE,
    track_temp_c DOUBLE,
    humidity_pct DOUBLE,
    pressure_mbar DOUBLE,
    rainfall_flag BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (race_id, timestamp)
);
"""

CREATE_SIMULATION_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS simulation_runs (
    simulation_id VARCHAR PRIMARY KEY,
    race_id VARCHAR NOT NULL,
    target_driver_id VARCHAR NOT NULL,
    decision_lap INT NOT NULL,
    simulation_mode VARCHAR NOT NULL DEFAULT 'decision_time',
    num_iterations INT NOT NULL DEFAULT 5000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    seed INT DEFAULT 42
);
"""

CREATE_STRATEGY_EVALUATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS strategy_evaluations (
    evaluation_id VARCHAR PRIMARY KEY,
    simulation_id VARCHAR REFERENCES simulation_runs(simulation_id),
    strategy_code VARCHAR NOT NULL,
    planned_pit_laps VARCHAR,
    expected_utility DOUBLE NOT NULL,
    expected_finish_pos DOUBLE NOT NULL,
    expected_finish_pos_ci95_lower DOUBLE NOT NULL,
    expected_finish_pos_ci95_upper DOUBLE NOT NULL,
    outcome_pos_p05 DOUBLE NOT NULL,
    outcome_pos_p95 DOUBLE NOT NULL,
    win_probability DOUBLE NOT NULL,
    podium_probability DOUBLE NOT NULL,
    points_probability DOUBLE NOT NULL,
    dnf_probability DOUBLE NOT NULL,
    utility_regret DOUBLE NOT NULL DEFAULT 0.0,
    expected_position_delta DOUBLE NOT NULL DEFAULT 0.0,
    is_statistically_distinct BOOLEAN
);
"""

CREATE_RACE_STATE_SNAPSHOT_VIEW = """
CREATE VIEW IF NOT EXISTS v_race_state_snapshot AS
SELECT 
    race_id,
    lap_number,
    driver_id,
    constructor_id,
    position,
    gap_to_leader_sec,
    interval_to_ahead_sec,
    compound,
    tyre_age_laps,
    stint_number,
    track_status,
    lap_time_sec
FROM lap_data;
"""


def init_db(conn: duckdb.DuckDBPyConnection) -> None:
    """Initialize all DuckDB tables and views."""
    conn.execute(CREATE_CIRCUITS_TABLE)
    conn.execute(CREATE_RACES_TABLE)
    conn.execute(CREATE_DRIVERS_TABLE)
    conn.execute(CREATE_CONSTRUCTORS_TABLE)
    conn.execute(CREATE_LAP_DATA_TABLE)
    conn.execute(CREATE_PIT_STOPS_TABLE)
    conn.execute(CREATE_WEATHER_TELEMETRY_TABLE)
    conn.execute(CREATE_SIMULATION_RUNS_TABLE)
    conn.execute(CREATE_STRATEGY_EVALUATIONS_TABLE)
    conn.execute(CREATE_RACE_STATE_SNAPSHOT_VIEW)


def get_db_connection(db_path: str = "data/pitwall.duckdb") -> duckdb.DuckDBPyConnection:
    """Connect to DuckDB database and ensure parent directory exists."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = duckdb.connect(db_path)
    init_db(conn)
    return conn
