# PITWALL — F1 Data Ecosystem Analysis & Specification

`docs/DATA_SOURCES.md`

---

## 1. Overview & Data Ingestion Philosophy

PITWALL relies on official, open-source, and legally permissible Formula 1 data sources. To ensure high reproducibility, low latency during simulation, and robust offline capabilities, PITWALL adopts a **Hybrid Ingestion & Caching Strategy**:

1. **Primary Ingestion Layer**: `FastF1` Python library for high-granularity lap timing, tyre compound telemetry, pit stop durations, and track weather.
2. **Historical Relational Layer**: `Jolpica-F1 API` (the official community drop-in successor to the Ergast API) for historical race results, driver/constructor standings, and circuit metadata.
3. **High-Frequency Telemetry Layer (Supplemental)**: `OpenF1 REST API` for turn-by-turn speeds, weather telemetry, and driver pit-lane timing delta validation (2023–present).
4. **Offline Benchmark Seed Layer**: Kaggle Formula 1 World Championship static dataset (1950–2024 CSV dump) pre-seeded into DuckDB for offline development and instant smoke testing without API network dependency.

---

## 2. Comprehensive Data Source Matrix

| Data Source | Base URL / Package | License | Historical Coverage | Granularity | Rate Limits | Auth Required | Cache Strategy | Primary Use in PITWALL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FastF1** | `fastf1` (PyPI) / `docs.fastf1.dev` | MIT | 2018 – Present (Full telemetry); 2019+ (Tyre data) | Lap-level, Sector-level, 10Hz Telemetry, Weather | Respects FIA timing server (built-in throttle) | No | Local SQLite/Parquet disk cache in `data/cache/fastf1` | Primary driver for lap times, tyre compound, tyre age, pit stops, and weather track temp. |
| **Jolpica-F1 API** | `api.jolpi.ca/ergast/f1/` | CC BY-NC-SA 4.0 | 1950 – Present | Session / Lap / Pit Stop | 4 req/sec (soft limit) | No | Cached to local DuckDB (`data/pitwall.duckdb`) | Qualifying order, historical grid positions, constructor points, official race classification. |
| **OpenF1 API** | `api.openf1.org/v1/` | MIT / Open Data | 2023 – Present | 1Hz - 10Hz real-time & session telemetry | 30 req/min | No | Cached per session in `data/cache/openf1` | Safety car deployment exact timestamps, interval gaps, pit lane entry/exit delta validation. |
| **Kaggle F1 CSV Dump** | Local static files | CC0 / Public Domain | 1950 – 2024 | Lap / Pit Stop / Results | N/A (Offline) | No | Imported directly to DuckDB on `make setup` | Baseline database seeding, unit tests, fast offline integration tests. |
| **Open-Meteo Historical Weather** | `archive-api.open-meteo.com` | CC BY 4.0 | 1940 – Present | Hourly / 15-min track coordinate weather | 10,000 req/day | No | Parquet cache per circuit/race date | Supplemental ambient temp, relative humidity, track rain probability backtesting. |

---

## 3. Detailed Data Field Extraction Mapping

### 3.1 FastF1 Lap & Tyre Data (`fastf1.core.Laps`)
Extracted per lap per driver:
- `Time` (timedelta): Session elapsed time at lap completion.
- `Driver` (str): 3-letter driver identifier (e.g., `'VER'`, `'HAM'`, `'NOR'`).
- `DriverNumber` (str): Car number.
- `LapNumber` (int): Sequential race lap index \( t \in [1, N_{\text{total}}] \).
- `LapTime` (float): Lap duration in seconds.
- `Stint` (int): Stint index (1, 2, 3...).
- `PitOutTime` / `PitInTime` (timedelta): Identifies pit in/out laps.
- `Sector1Time`, `Sector2Time`, `Sector3Time` (float): Sector times in seconds.
- `SpeedI1`, `SpeedI2`, `SpeedFL`, `SpeedST` (float): Speed trap measurements (km/h).
- `Compound` (str): Tyre compound name (`'SOFT'`, `'MEDIUM'`, `'HARD'`, `'INTERMEDIATE'`, `'WET'`).
- `TyreLife` (int): Laps run on current tyre set.
- `FreshTyre` (bool): Whether the tyre set was new at stint start.
- `TrackStatus` (str): Track flag condition codes (1=Green, 2=Yellow, 4=SC, 5=Red, 6=VSC).
- `IsAccurate` (bool): FastF1 validity flag (filters out out-laps/in-laps and safety car distorted laps for pace modeling).

### 3.2 Weather Data (`fastf1.core.Session.weather_data`)
Extracted per minute:
- `Time` (timedelta): Session time.
- `AirTemp` (float): Ambient air temperature (°C).
- `TrackTemp` (float): Track surface temperature (°C).
- `Humidity` (float): Relative humidity (%).
- `Pressure` (float): Air pressure (mbar).
- `Rainfall` (bool): Binary precipitation flag.
- `WindSpeed` / `WindDirection` (float): Wind telemetry.

### 3.3 Pit Stop Data (Jolpica / FastF1)
- `raceId` (int): Unique race identifier.
- `driverId` (str): Driver slug.
- `stop` (int): Stop number for driver in race.
- `lap` (int): Lap on which pit stop occurred.
- `duration` (float): Pit stop stationery time or total pit lane loss in seconds.

---

## 4. Data Cleaning & Normalization Pipeline

Raw F1 timing data contains noise (Safety Cars, Virtual Safety Cars, yellow flags, blue flag traffic delays, out-laps, in-laps). PITWALL applies strict filtering rules prior to training ML models or fitting baseline pace distributions:

1. **In-Lap and Out-Lap Flagging**: Laps where `PitInTime` or `PitOutTime` is non-null are excluded from pure pace/degradation fitting and labeled as `IsPitLap = True`.
2. **Safety Car & VSC Filtering**: Laps where `TrackStatus` contains `'4'` (SC) or `'6'` (VSC) are flagged `IsCorruptedPace = True`.
3. **Pace Outlier Truncation**: Laps exceeding \( 1.15 \times \text{MedianLapTime}_{\text{stint}} \) under green flag conditions are flagged as traffic-impacted or mistake laps and excluded from pure tyre degradation fitting.
4. **Missing Compound Imputation**: For legacy races missing explicit compound strings, compounds are inferred via stint length and relative degradation slopes or defaulted to standard `SOFT`/`MEDIUM`/`HARD` category mappings.

---

## 5. Storage & Redistribution Compliance

- **Raw Data Redistribution**: Raw telemetry files are cached in local `.fastf1-cache/` and `data/raw/` directories, which are listed in `.gitignore`.
- **Derived Analytics Redistribution**: Synthetic feature tables, trained model weights (`.pkl` / `.onnx`), and processed DuckDB databases (`data/pitwall.duckdb`) contain no copyrighted FIA proprietary code and are fully safe for open-source GitHub distribution under the MIT license.
