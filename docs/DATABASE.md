# PITWALL — Database Architecture & ERD Specification

`docs/DATABASE.md`

---

## 1. Hybrid Analytical Database Architecture

PITWALL utilizes a **Hybrid DuckDB + Parquet Analytical Architecture** optimized for high-speed columnar filtering, rolling lap window aggregations, and fast Monte Carlo state initialization:

- **DuckDB Core (`data/pitwall.duckdb`)**: Embedded columnar OLAP database handling all lap times, sector telemetry, tyre wear vectors, circuit metadata, and model artifacts. DuckDB provides vectorized SQL execution, seamless Pandas/Polars zero-copy interoperability, and single-file serverless deployment.
- **Parquet Cache Layer (`data/parquet/`)**: Compressed, partitioned storage for raw lap telemetry and simulation iteration snapshots (`data/parquet/simulations/race_{id}_lap_{lap}.parquet`).

---

## 2. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    SEASONS ||--|{ RACES : includes
    CIRCUITS ||--|{ RACES : hosts
    RACES ||--|{ SESSIONS : divides
    RACES ||--|{ LAP_DATA : contains
    DRIVERS ||--|{ LAP_DATA : records
    CONSTRUCTORS ||--|{ LAP_DATA : fields
    RACES ||--|{ STINTS : tracks
    DRIVERS ||--|{ STINTS : completes
    RACES ||--|{ PIT_STOPS : logs
    DRIVERS ||--|{ PIT_STOPS : executes
    RACES ||--|{ WEATHER_TELEMETRY : samples
    RACES ||--|{ SIMULATION_RUNS : spawns
    SIMULATION_RUNS ||--|{ STRATEGY_EVALUATIONS : yields
    SIMULATION_RUNS ||--|{ COUNTERFACTUAL_RESULTS : compares
```

---

## 3. Detailed Table Schemas (DuckDB DDL)

### 3.1 `circuits`
```sql
CREATE TABLE IF NOT EXISTS circuits (
    circuit_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    location VARCHAR,
    country VARCHAR,
    latitude DOUBLE,
    longitude DOUBLE,
    length_km DOUBLE NOT NULL,
    turns INT,
    pit_lane_loss_sec DOUBLE, -- Estimated pit lane time loss (sec), populated via model prior/fitting
    base_degradation_mult DOUBLE DEFAULT 1.0,
    overtaking_difficulty_mult DOUBLE DEFAULT 1.0 -- Circuit overtaking resistance factor
);
```

### 3.2 `races`
```sql
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
```

### 3.3 `drivers`
```sql
CREATE TABLE IF NOT EXISTS drivers (
    driver_id VARCHAR PRIMARY KEY,
    code VARCHAR(3) UNIQUE NOT NULL,
    permanent_number INT,
    first_name VARCHAR,
    last_name VARCHAR,
    nationality VARCHAR
);
```

### 3.4 `lap_data` (Core Analytical Fact Table)
```sql
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
```

### 3.5 `simulation_runs`
```sql
CREATE TABLE IF NOT EXISTS simulation_runs (
    simulation_id VARCHAR PRIMARY KEY,
    race_id VARCHAR NOT NULL,
    target_driver_id VARCHAR NOT NULL,
    decision_lap INT NOT NULL,
    simulation_mode VARCHAR NOT NULL DEFAULT 'decision_time', -- 'decision_time' vs 'hindsight'
    num_iterations INT NOT NULL DEFAULT 5000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    seed INT DEFAULT 42
);
```

### 3.6 `strategy_evaluations`
```sql
CREATE TABLE IF NOT EXISTS strategy_evaluations (
    evaluation_id VARCHAR PRIMARY KEY,
    simulation_id VARCHAR REFERENCES simulation_runs(simulation_id),
    strategy_code VARCHAR NOT NULL, -- e.g., 'PIT_NOW_HARD', 'STAY_OUT'
    planned_pit_laps VARCHAR, -- e.g., '[32]'
    expected_utility DOUBLE NOT NULL,
    expected_finish_pos DOUBLE NOT NULL,
    expected_finish_pos_ci95_lower DOUBLE NOT NULL, -- 95% CI for expected finish position mean
    expected_finish_pos_ci95_upper DOUBLE NOT NULL, -- 95% CI for expected finish position mean
    outcome_pos_p05 DOUBLE NOT NULL, -- 5th percentile outcome prediction quantile
    outcome_pos_p95 DOUBLE NOT NULL, -- 95th percentile outcome prediction quantile
    win_probability DOUBLE NOT NULL,
    podium_probability DOUBLE NOT NULL,
    points_probability DOUBLE NOT NULL,
    dnf_probability DOUBLE NOT NULL,
    utility_regret DOUBLE NOT NULL DEFAULT 0.0, -- U(a*) - U(a) >= 0 relative to optimal strategy
    expected_position_delta DOUBLE NOT NULL DEFAULT 0.0, -- E[Pos(a)] - E[Pos(a*)]
    is_statistically_distinct BOOLEAN -- Computed via pairwise 95% CI check on DeltaU (NO DEFAULT)
);
```

---

## 4. Analytical Indexing & Optimization Strategy

1. **Composite Primary Keys**: Enforces entity integrity on multi-tenant race tables (`race_id`, `driver_id`, `lap_number`).
2. **Columnar Compression**: DuckDB auto-compresses telemetry columns using ZSTD / Bitpacking, reducing disk memory footprint.
3. **Pre-computed View `v_race_state_snapshot`**: Materializes exact race state \( \text{RaceState}(t) \) at lap \( t \) including current position, compound, tyre age, and gap vectors for fast simulation initial condition bootstrapping.
