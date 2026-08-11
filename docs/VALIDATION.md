# PITWALL — Model & Simulation Validation Protocol

`docs/VALIDATION.md`

---

## 1. Validation Philosophy & Metrics

To prove statistical defensibility to AQX Data Bowl 3.0 judges, PITWALL enforces rigorous validation standards across all predictive and simulation components:

1. **Strict Temporal Integrity**: Zero look-ahead bias; models trained on past data never access future lap information during validation runs.
2. **Multi-Tiered Evaluation**:
   - **Point Metrics**: Root Mean Squared Error (RMSE) & Mean Absolute Error (MAE) for lap times and positions.
   - **Probabilistic Calibration**: Probability Integral Transform (PIT) histograms and Brier Score for Monte Carlo finish position distributions.
   - **Counterfactual Decision Accuracy**: Historical retrospective agreement with recognized expert race strategy consensus.

---

## 2. Quantitative Benchmark Targets

| Evaluation Metric | Target Threshold | Minimum Acceptable | Primary Target Domain |
| :--- | :--- | :--- | :--- |
| **Pace Model Lap Time RMSE** | \( < 0.32 \text{s} \) | \( < 0.45 \text{s} \) | Green-flag clean-air laps |
| **Tyre Degradation MAE** | \( < 0.25 \text{s/lap} \) | \( < 0.40 \text{s/lap} \) | High-age tyre stints (\( a > 15 \)) |
| **Final Race Position MAE** | \( < 1.2 \text{ positions} \) | \( < 2.0 \text{ positions} \) | 20-lap remaining simulation horizon |
| **Win Probability Calibration Brier Score** | \( < 0.08 \) | \( < 0.14 \) | Race winner prediction |
| **Simulation Latency (5,000 runs)** | \( < 300 \text{ms} \) | \( < 600 \text{ms} \) | End-to-end API response |

---

## 3. Historical Holdout Validation Races

The validation benchmark suite evaluates PITWALL on 4 iconic historical F1 races featuring high strategic volatility:

1. **2021 Abu Dhabi Grand Prix (Yas Marina)**: Late Safety Car stint decision (Lap 53) — Mercedes (Hamilton) vs Red Bull (Verstappen). Tests Safety Car restart tyre delta evaluation.
2. **2022 Monaco Grand Prix (Monte Carlo)**: Dynamic Wet-to-Dry crossover strategy — Ferrari (Leclerc/Sainz) vs Red Bull (Perez/Verstappen). Tests pit window crossover timing under wet conditions.
3. **2022 British Grand Prix (Silverstone)**: Late Safety Car restart decision — Ferrari (Leclerc vs Sainz). Tests team mate split-strategy optimization.
4. **2023 Dutch Grand Prix (Zandvoort)**: Extreme rain chaos on Lap 1–2. Tests rapid rain transition Markov chain and intermediate tyre pit timing.

---

## 4. Rolling-Origin Backtesting Engine (`scripts/evaluate.py`)

Validation is executed automatically via `make evaluate` using rolling-origin backtesting:
- For a target race at Lap \( t \), initialize simulator using state at Lap \( t \).
- Predict future lap pace, pit stops, and final finishing positions for all 20 cars.
- Advance \( t \to t + 5 \) laps and repeat until race finish.
- Log error metrics and generate calibration curves saved to `reports/validation_results.json`.
