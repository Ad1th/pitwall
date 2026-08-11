"""
PITWALL Database Seeding Script.
Populates DuckDB database with Formula 1 timing, telemetry, and pit stop records.
Ref: docs/DEVELOPMENT_PLAN.md Stage 1
"""

import sys
import os
import json
import argparse
import logging
from typing import Any, Dict, List, Optional

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.schema import get_db_connection
from backend.app.ingestion.fastf1_adapter import FastF1Adapter
from backend.app.ingestion.jolpica_adapter import JolpicaAdapter
from backend.app.ingestion.openf1_adapter import OpenF1Adapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("seed_db")

BENCHMARK_RACES = {
    "2021-abu-dhabi": {"year": 2021, "round": 22, "name": "Abu Dhabi Grand Prix"},
    "2022-monaco": {"year": 2022, "round": 7, "name": "Monaco Grand Prix"},
    "2022-silverstone": {"year": 2022, "round": 10, "name": "British Grand Prix"},
    "2023-zandvoort": {"year": 2023, "round": 13, "name": "Dutch Grand Prix"},
}


def load_offline_seed(race_slug: str) -> Optional[Dict[str, Any]]:
    """Load pre-seeded static JSON data for offline execution."""
    seed_file = os.path.join("data", "seed", f"{race_slug}.json")
    if os.path.exists(seed_file):
        try:
            with open(seed_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as err:
            logger.warning(f"Failed to read static seed file {seed_file}: {err}")
    return None


def insert_circuit(conn: Any, c: Dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO circuits 
        (circuit_id, name, location, country, latitude, longitude, length_km, turns, pit_lane_loss_sec, base_degradation_mult, overtaking_difficulty_mult)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            c.get("circuit_id"),
            c.get("name"),
            c.get("location"),
            c.get("country"),
            c.get("latitude"),
            c.get("longitude"),
            c.get("length_km", 5.0),
            c.get("turns", 16),
            c.get("pit_lane_loss_sec"),
            c.get("base_degradation_mult", 1.0),
            c.get("overtaking_difficulty_mult", 1.0),
        ],
    )


def insert_race(conn: Any, r: Dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO races 
        (race_id, year, round, circuit_id, name, date, total_laps, official_winner_driver_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            r.get("race_id"),
            r.get("year"),
            r.get("round"),
            r.get("circuit_id"),
            r.get("name"),
            r.get("date"),
            r.get("total_laps"),
            r.get("official_winner_driver_id"),
        ],
    )


def insert_driver(conn: Any, d: Dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO drivers
        (driver_id, code, permanent_number, first_name, last_name, nationality)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            d.get("driver_id"),
            d.get("code"),
            d.get("permanent_number"),
            d.get("first_name"),
            d.get("last_name"),
            d.get("nationality"),
        ],
    )


def insert_constructor(conn: Any, c: Dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO constructors
        (constructor_id, name, nationality)
        VALUES (?, ?, ?)
        """,
        [c.get("constructor_id"), c.get("name"), c.get("nationality")],
    )


def insert_laps(conn: Any, laps: List[Dict[str, Any]]) -> None:
    for lap in laps:
        conn.execute(
            """
            INSERT OR IGNORE INTO lap_data
            (race_id, driver_id, constructor_id, lap_number, position, lap_time_sec, sector1_sec, sector2_sec, sector3_sec, speed_st, compound, tyre_age_laps, stint_number, is_pit_lap, is_accurate, track_status, gap_to_leader_sec, interval_to_ahead_sec)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                lap.get("race_id"),
                lap.get("driver_id"),
                lap.get("constructor_id"),
                lap.get("lap_number"),
                lap.get("position"),
                lap.get("lap_time_sec"),
                lap.get("sector1_sec"),
                lap.get("sector2_sec"),
                lap.get("sector3_sec"),
                lap.get("speed_st"),
                lap.get("compound"),
                lap.get("tyre_age_laps"),
                lap.get("stint_number"),
                lap.get("is_pit_lap", False),
                lap.get("is_accurate", True),
                lap.get("track_status", "1"),
                lap.get("gap_to_leader_sec"),
                lap.get("interval_to_ahead_sec"),
            ],
        )


def insert_pit_stops(conn: Any, pit_stops: List[Dict[str, Any]]) -> None:
    for ps in pit_stops:
        conn.execute(
            """
            INSERT OR IGNORE INTO pit_stops
            (race_id, driver_id, stop_number, lap_number, duration_sec, total_pit_lane_time_sec)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                ps.get("race_id"),
                ps.get("driver_id"),
                ps.get("stop_number", 1),
                ps.get("lap_number"),
                ps.get("duration_sec"),
                ps.get("total_pit_lane_time_sec"),
            ],
        )


def insert_weather(conn: Any, weather: List[Dict[str, Any]]) -> None:
    for w in weather:
        conn.execute(
            """
            INSERT OR IGNORE INTO weather_telemetry
            (race_id, timestamp, air_temp_c, track_temp_c, humidity_pct, pressure_mbar, rainfall_flag)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                w.get("race_id"),
                w.get("timestamp"),
                w.get("air_temp_c"),
                w.get("track_temp_c"),
                w.get("humidity_pct"),
                w.get("pressure_mbar"),
                w.get("rainfall_flag", False),
            ],
        )


def seed_race(race_slug: str, conn: Any, force_offline: bool = False) -> bool:
    """Ingest and seed database for specified race slug."""
    if race_slug not in BENCHMARK_RACES:
        logger.error(f"Unknown race slug '{race_slug}'. Supported: {list(BENCHMARK_RACES.keys())}")
        return False

    race_meta = BENCHMARK_RACES[race_slug]
    year = race_meta["year"]
    round_num = race_meta["round"]
    logger.info(f"Processing race '{race_slug}' (Year {year}, Round {round_num})...")

    data = None
    if not force_offline:
        fastf1_adapter = FastF1Adapter()
        data = fastf1_adapter.load_race_session(year, round_num)

    if not data:
        logger.info(f"Live data unavailable or offline requested for '{race_slug}'. Using static seed fallback...")
        data = load_offline_seed(race_slug)

    if not data:
        logger.error(f"Failed to load data for '{race_slug}' (neither live nor offline seed available).")
        return False

    # Insert into DuckDB
    if data.get("circuit"):
        insert_circuit(conn, data["circuit"])
    if data.get("race"):
        insert_race(conn, data["race"])
    for d in data.get("drivers", []):
        insert_driver(conn, d)
    for c in data.get("constructors", []):
        insert_constructor(conn, c)
    if data.get("lap_data"):
        insert_laps(conn, data["lap_data"])
    if data.get("pit_stops"):
        insert_pit_stops(conn, data["pit_stops"])
    if data.get("weather_telemetry"):
        insert_weather(conn, data["weather_telemetry"])

    # Attempt Jolpica supplemental pit stop enrich if live
    if not force_offline:
        jolpica = JolpicaAdapter()
        jolpica_stops = jolpica.fetch_pit_stops(year, round_num)
        if jolpica_stops:
            ps_records = []
            for item in jolpica_stops:
                try:
                    ps_records.append({
                        "race_id": race_slug,
                        "driver_id": str(item.get("driverId", "")).upper()[:3],
                        "stop_number": int(item.get("stop", 1)),
                        "lap_number": int(item.get("lap", 1)),
                        "duration_sec": float(item.get("duration", "0").replace(":", "").replace("s", "")),
                        "total_pit_lane_time_sec": None,
                    })
                except Exception:
                    pass
            if ps_records:
                insert_pit_stops(conn, ps_records)

    logger.info(f"Successfully seeded race '{race_slug}'.")
    return True


def print_db_summary(conn: Any) -> None:
    """Log current table row counts from DuckDB."""
    tables = ["circuits", "races", "drivers", "constructors", "lap_data", "pit_stops", "weather_telemetry"]
    logger.info("=== PITWALL DuckDB Database Summary ===")
    for tbl in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        logger.info(f"Table '{tbl}': {count} rows")


def main():
    parser = argparse.ArgumentParser(description="Seed PITWALL DuckDB Database.")
    parser.add_argument("--race", type=str, help="Race slug to seed (e.g., 2021-abu-dhabi)")
    parser.add_argument("--all", action="store_true", help="Seed all benchmark races")
    parser.add_argument("--offline", action="store_true", help="Force offline seed loading")
    parser.add_argument("--db-path", type=str, default="data/pitwall.duckdb", help="Target DuckDB file path")
    args = parser.parse_args()

    conn = get_db_connection(args.db_path)

    if args.all:
        for slug in BENCHMARK_RACES.keys():
            seed_race(slug, conn, force_offline=args.offline)
    elif args.race:
        seed_race(args.race, conn, force_offline=args.offline)
    else:
        # Default to 2021-abu-dhabi if no arg specified
        seed_race("2021-abu-dhabi", conn, force_offline=args.offline)

    print_db_summary(conn)
    conn.close()


if __name__ == "__main__":
    main()
