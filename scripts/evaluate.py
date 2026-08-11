#!/usr/bin/env python3
"""
PITWALL Multi-Race Benchmark & Rolling-Origin Model Evaluation Script.
Ref: docs/VALIDATION.md Section 3 & docs/DEVELOPMENT_PLAN.md Stage 11
"""

import os
import json
import sys
import argparse
import logging
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.schema import get_db_connection
from backend.app.validation.evaluator import RollingOriginEvaluator
from scripts.seed_db import seed_race, BENCHMARK_RACES

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("evaluate")


def parse_args():
    parser = argparse.ArgumentParser(description="PITWALL Multi-Race Benchmark Evaluator")
    parser.add_argument("--no-tyre-deg", action="store_true", help="Ablate tyre degradation model")
    parser.add_argument("--no-traffic", action="store_true", help="Ablate dirty air and traffic model")
    parser.add_argument("--no-weather-markov", action="store_true", help="Ablate weather update model")
    parser.add_argument("--db", default="data/pitwall.duckdb", help="DuckDB database path")
    parser.add_argument("--output", default="data/validation_report.json", help="Output JSON path")
    return parser.parse_args()


def main():
    args = parse_args()

    # 1. Connect and ensure benchmark races are seeded
    conn = get_db_connection(args.db)
    logger.info("Ensuring benchmark races are seeded in database...")
    for race_slug in BENCHMARK_RACES.keys():
        seed_race(race_slug, conn, force_offline=True)

    # 2. Run rolling-origin evaluation
    evaluator = RollingOriginEvaluator(
        conn=conn,
        no_tyre_deg=args.no_tyre_deg,
        no_traffic=args.no_traffic,
        no_weather_markov=args.no_weather_markov,
    )

    logger.info("Running rolling-origin evaluation across benchmark races...")
    race_results = []
    for race_slug in BENCHMARK_RACES.keys():
        res = evaluator.evaluate_race(race_slug)
        race_results.append(res)

    # Aggregate overall metrics
    all_rmse = [r["metrics"]["rmse"] for r in race_results]
    all_mae = [r["metrics"]["mae"] for r in race_results]
    all_brier = [r["metrics"]["brier_score"] for r in race_results]
    all_rps = [r["metrics"]["mean_rps"] for r in race_results]

    report: Dict[str, Any] = {
        "benchmark_summary": {
            "races_evaluated": len(race_results),
            "ablations": {
                "no_tyre_deg": args.no_tyre_deg,
                "no_traffic": args.no_traffic,
                "no_weather_markov": args.no_weather_markov,
            },
            "mean_rmse": round(float(sum(all_rmse) / len(all_rmse)), 3) if all_rmse else 0.0,
            "mean_mae": round(float(sum(all_mae) / len(all_mae)), 3) if all_mae else 0.0,
            "mean_brier_score": round(float(sum(all_brier) / len(all_brier)), 4) if all_brier else 0.0,
            "mean_rps": round(float(sum(all_rps) / len(all_rps)), 4) if all_rps else 0.0,
        },
        "race_details": race_results,
    }

    # 3. Save machine-readable output JSON
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Machine-readable evaluation report saved to '{args.output}'.")

    # 4. Print human-readable summary table
    print("\n" + "=" * 60)
    print(" === PITWALL BENCHMARK VALIDATION REPORT ===")
    print("=" * 60)
    print(f" Ablations Active: TyreDeg={args.no_tyre_deg}, Traffic={args.no_traffic}, Weather={args.no_weather_markov}")
    print("-" * 60)
    print(f" {'Race Slug':<20} | {'RMSE':<8} | {'MAE':<8} | {'Brier':<8} | {'RPS':<8}")
    print("-" * 60)
    for r in race_results:
        m = r["metrics"]
        print(f" {r['race_id']:<20} | {m['rmse']:<8.3f} | {m['mae']:<8.3f} | {m['brier_score']:<8.4f} | {m['mean_rps']:<8.4f}")
    print("-" * 60)
    summary = report["benchmark_summary"]
    print(f" OVERALL MEAN         | {summary['mean_rmse']:<8.3f} | {summary['mean_mae']:<8.3f} | {summary['mean_brier_score']:<8.4f} | {summary['mean_rps']:<8.4f}")
    print("=" * 60 + "\n")

    conn.close()


if __name__ == "__main__":
    main()
