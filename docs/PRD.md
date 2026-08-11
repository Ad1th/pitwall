# PITWALL — Authoritative Product Requirement Document (PRD)

`docs/PRD.md`

---

## 1. Executive Summary & Tagline

> **"Don't analyze the race. Re-run it."**

**PITWALL** is a Counterfactual Race Strategy Engine built for Formula 1 motor racing and submitted to the **AQX Sports Analytics Data Bowl 3.0**. Unlike conventional sports dashboards or static race outcome prediction models, PITWALL reconstructs historical race states \( \text{RaceState}(t) \) and answers the fundamental strategic question:

> *"Given everything that was known at lap \( t \), what decision should the pit wall have made, and what would probably have happened if they had chosen a different path?"*

By combining historical telemetry, statistical tyre degradation modeling, fuel pace decay equations, probabilistic overtaking friction kernels, stochastic weather Markov chains, and high-speed vectorized Monte Carlo simulation (5,000 iterations using Common Random Numbers), PITWALL quantifies **Utility Regret** and identifies actionable strategic masterstrokes and mistakes.

---

## 2. Competition Alignment & "Why PITWALL Can Win"

The AQX Sports Analytics Data Bowl 3.0 evaluates submissions across three core judging criteria:

### 2.1 Practical Application (Weight: 35%)
- **Generic Hackathon Baseline**: Static position charts or naive post-race "who won" classifiers.
- **PITWALL Advantage**: Directly models real-world race engineering decisions (Pit Now vs Stay Out, Compound Selection, Undercut/Overcut windows under dirty air). Provides actionable counterfactual decision intelligence usable by race strategists.

### 2.2 Analytical Insight (Weight: 35%)
- **Generic Hackathon Baseline**: Standard linear regression fitting lap time to lap number.
- **PITWALL Advantage**: Decouples compound wear from fuel mass burn, traffic dirty air delays, track surface temperature, and Safety Car probabilistic restarts. Produces full probability distributions (expected utility, win/podium probability, variance, outcome prediction quantiles, and utility regret) rather than fragile point predictions. Incorporates explicit probabilistic overtaking mechanisms, paired Common Random Numbers (CRN) simulation, and dual operational modes (Decision-Time vs Hindsight).

### 2.3 Data Presentation (Weight: 30%)
- **Generic Hackathon Baseline**: Basic unstyled Streamlit app or matplotlib notebooks.
- **PITWALL Advantage**: Dark-mode Formula 1 Pit Wall telemetry Command Center featuring glassmorphic UI tokens, interactive lap scrubbers, real-time strategy builders, statistical confidence bounds on expected utility, outcome prediction quantiles, and Monte Carlo finish position density charts.

---

## 3. Mathematical Problem Formalization

### 3.1 State Representation \( \text{RaceState}(t) \)
At lap \( t \in [1, N_{\text{total}}] \), the race state is defined as:

\[
\text{RaceState}(t) = \left\langle t, \mathbf{P}_t, \mathbf{G}_t, \mathbf{C}_t, \mathbf{A}_t, \mathbf{S}_t, T_t, W_t, \Phi_t, \mathcal{M} \right\rangle
\]

Where for each driver \( i \in [1, 20] \):
- \( \mathbf{P}_t[i] \in [1, 20] \): Track position at lap \( t \).
- \( \mathbf{G}_t[i] \in \mathbb{R} \): Gap to race leader in seconds.
- \( \mathbf{C}_t[i] \in \{\text{SOFT}, \text{MEDIUM}, \text{HARD}, \text{INTER}, \text{WET}\} \): Active tyre compound.
- \( \mathbf{A}_t[i] \in \mathbb{N} \): Current tyre age in laps.
- \( \mathbf{S}_t[i] \in \mathbb{N} \): Stint number.
- \( T_t \in \mathbb{R} \): Track surface temperature (°C).
- \( W_t \in \{\text{DRY}, \text{DAMP}, \text{WET}\} \): Weather state.
- \( \Phi_t \in \{\text{GREEN}, \text{YELLOW}, \text{VSC}, \text{SC}\} \): Track flag status.
- \( \mathcal{M} \in \{\text{DECISION\_TIME}, \text{HINDSIGHT}\} \): Operational simulation mode.

### 3.2 Strategy Space & Optimization Objective
For a target driver at lap \( t \), candidate strategies \( a \in \mathcal{A} \) consist of planned pit stops:
\[
a = \{ (\text{pit\_lap}_k, \text{compound}_k) \}_{k=1}^{K}
\]
The Strategy Optimizer searches this space using a **Two-Stage Coarse-to-Fine Search** to maximize expected utility:

\[
U(a) = \mathbb{E}_{\omega} \left[ \text{Points}(\mathbf{P}_{N_{\text{total}}}(a)) \right] - \lambda \cdot \text{Var}(\mathbf{P}_{N_{\text{total}}}(a))
\]

Let \( a^* = \arg\max_{a' \in \mathcal{A}} U(a') \) be the optimal strategy under the model objective.

### 3.3 Utility Regret vs Expected Position Delta
We strictly distinguish between two evaluation metrics:

1. **Utility Regret**: The loss in expected utility relative to the optimizer's chosen optimal strategy:
   \[
   \text{UtilityRegret}(a) = U(a^*) - U(a) \ge 0
   \]
   Utility Regret is non-negative by definition and measures sub-optimality relative to the objective function.

2. **Expected Position Delta**: The difference in expected finishing position:
   \[
   \text{ExpectedPositionDelta}(a) = \mathbb{E}[\mathbf{P}_{N_{\text{total}}}(a)] - \mathbb{E}[\mathbf{P}_{N_{\text{total}}}(a^*)]
   \]
   This metric isolates the expected finishing rank shift.

### 3.4 Paired Monte Carlo Simulation & Indistinguishability Criterion
Counterfactual comparisons use **Paired Monte Carlo Simulations with Common Random Numbers (CRN)**. Both baseline strategy \( a_0 \) and counterfactual strategy \( a \) evaluate under identical exogenous random seed realizations \( \omega_m \).

Strategies \( a_1 \) and \( a_2 \) are defined as **Statistically Indistinguishable** if and only if the 95% confidence interval for their pairwise utility difference contains zero:

\[
0 \in \text{CI}_{95\%}(\Delta U_{a_1, a_2})
\]

---

## 4. Functional Requirements Matrix

### 4.1 System & Data Requirements
- `FR-001`: Ingest FastF1 lap timing, sector split times, tyre compounds, tyre age, and track status for seasons 2018–2024.
- `FR-002`: Import Jolpica-F1 (community Ergast-compatible API) session classifications, driver grid positions, and pit stop durations.
- `FR-003`: Store all ingested facts in DuckDB database (`data/pitwall.duckdb`) with execution latency \( < 10\text{ms} \).
- `FR-004`: Pre-seed offline benchmark dataset for 4 holdout races (2021 Abu Dhabi, 2022 Monaco, 2022 Silverstone, 2023 Zandvoort). OpenF1 data is supplemental for 2023+ only.

### 4.2 Analytical & Modeling Requirements
- `MODEL-001`: Implement tyre degradation model predicting lap pace wear rate \( \Delta T_{\text{deg}}(a, \text{compound}, T_{\text{track}}) \).
- `MODEL-002`: Estimate fuel-load pace decay, dirty air traffic delay, and pit-lane time loss parameters empirically per circuit/car rather than using fixed hardcoded constants.
- `MODEL-003`: Enforce strict temporal leakage prevention in Decision-Time Mode (zero look-ahead data usage).
- `MODEL-004`: Implement probabilistic overtaking and position-transition mechanism for 20-car simulations.
- `MODEL-005`: Support two distinct operational modes: **Decision-Time Mode** and **Hindsight / Oracle Mode**.

### 4.3 Simulation Requirements
- `SIM-001`: Execute paired Monte Carlo race iterations per strategy evaluation using Common Random Numbers (5,000 iterations for full evaluation; 500 for coarse search).
- `SIM-002`: Compute outcome prediction quantiles (\( q_{05}, q_{95} \)) and expected utility 95% confidence intervals.
- `SIM-003`: **Primary Criteria**: Enforce statistical validity, physical overtaking constraints, and state vector correctness.
- `SIM-004`: **Optimization Target**: Target simulation completion in \( < 450\text{ms} \) via NumPy array broadcasting without sacrificing physical model validity.
- `SIM-005`: Ensure deterministic simulation output when seeded with fixed integer (`seed=42`).

### 4.4 Counterfactual & Autopsy Requirements
- `CF-001`: Calculate Utility Regret \( U(a^*) - U(a) \ge 0 \) and Expected Position Delta with 95% confidence bounds.
- `CF-002`: Rank top strategic errors in historical races by Utility Regret magnitude.
- `CF-003`: Identify and explicitly report when alternative candidate strategies are statistically indistinguishable (\( 0 \in \text{CI}_{95\%}(\Delta U) \)).
- `CF-004`: Produce model-driven counterfactual results without relying on hardcoded expected outcomes.

### 4.5 API Requirements
- `API-001`: Expose FastAPI REST endpoints `/api/v1/races`, `/state/{lap}`, `/simulate`, `/counterfactual`, and `/autopsy`.
- `API-002`: Support `mode` parameter (`"decision_time"` vs `"hindsight"`) across simulation endpoints.
- `API-003`: Enforce strict typing with Pydantic schemas.

### 4.6 User Interface Requirements
- `UI-001`: Render dark-mode F1 telemetry Command Center layout.
- `UI-002`: Provide interactive lap scrubber updating standings and gap deltas in real-time.
- `UI-003`: Provide interactive strategy builder toolbar with coarse-to-fine search options and operational mode toggle.
- `UI-004`: Render Monte Carlo finish position density charts with 95% confidence intervals on expected values, outcome prediction quantiles, and strategy indistinguishability warnings.

### 4.7 Testing & Quality Requirements
- `TEST-001`: Maintain unit test coverage across data parsing, state engine, tyre models, overtaking friction, and simulator.
- `TEST-002`: Provide end-to-end test script `make test-e2e` validating data flow from DuckDB to UI payload.
- `TEST-003`: Provide model ablation testing script (`scripts/evaluate.py --no-tyre-deg`, `--no-traffic`, `--no-weather-markov`).

---

## 5. System Tier Categorization

### Tier 1: MVP (Minimum Viable Product — Stage 0 to Stage 8)
- DuckDB ingestion of 2021 Abu Dhabi Grand Prix.
- Reconstructed lap state engine \( \text{RaceState}(t) \).
- Baseline statistical tyre wear, fuel decay, and overtaking model.
- Vectorized Monte Carlo simulator using Common Random Numbers.
- FastAPI REST backend + React Command Center lap scrubber UI.

### Tier 2: Competitive Version (Stage 9 to Stage 13)
- Multi-race benchmark dataset (Abu Dhabi 2021, Monaco 2022, Silverstone 2022, Zandvoort 2023).
- Interactive strategy builder with coarse-to-fine search and 95% CI reporting.
- Automated Race Autopsy ranking mistake Utility Regret.
- Full rolling-origin validation script (`scripts/evaluate.py`) with RPS, EMD, and Brier score metrics.

### Tier 3: Stretch Goals (Stage 14 to Stage 15)
- LLM natural language strategic explanation generator.
- Multi-car team strategy joint optimization (e.g. Mercedes double-stack vs split strategy).
- Docker containerization packaging.

---

## 6. Risk & Fallback Strategy Matrix

| Risk Event | Severity | Detection Method | Fallback Strategy |
| :--- | :--- | :--- | :--- |
| **FastF1 live API rate limited / down** | High | Ingestion HTTP 429/500 error | Instantly fallback to offline Kaggle static DuckDB CSV seed (`data/pitwall.duckdb`). |
| **Telemetry missing compound details** | Medium | Null compound column in lap data | Infer compound from stint length and relative degradation slope; default to `MEDIUM`. |
| **Monte Carlo simulation > 1.0s latency** | High | Benchmark execution timer | Optimize NumPy array broadcasting memory layout or utilize coarse search filtering. |
| **LightGBM tyre model overfits small stint sample** | Medium | Validation RMSE > 0.45s | Fallback to regularized GAM / quadratic polynomial per compound. |

---

## 7. Competition Demo Script Flow (3–5 Minutes) `[ILLUSTRATIVE NARRATIVE]`

1. **The Hook (30s)**: Show the iconic 2021 Abu Dhabi Grand Prix restart at Lap 53. Ask the core question: *"What decision should the pit wall have made under late Safety Car conditions given available information?"*
2. **Race Command Center (60s)**: Scrub to Lap 53 in PITWALL. Toggle between Decision-Time Mode and Hindsight Mode.
3. **Interactive Strategy Simulator (60s)**: Execute paired Monte Carlo simulation using Common Random Numbers for candidate strategies. Display finish position density chart with 95% confidence bounds on expected utility and outcome prediction quantiles.
4. **Counterfactual Replay & Autopsy (60s)**: Re-run the race under counterfactual strategies. Demonstrate how PITWALL quantifies Utility Regret \( U(a^*) - U(a) \) and Expected Position Delta without hardcoded assumptions.
5. **Technical Defensibility (30s)**: Present model cross-validation metrics (Brier Score for win probability, RPS for finish distributions, model ablation tests).

---

## 8. Devpost Submission Narrative Outline

- **Title**: PITWALL — The Counterfactual Race Strategy Engine
- **Tagline**: Don't analyze the race. Re-run it.
- **Problem Statement**: Formula 1 race strategy analysis is dominated by post-hoc commentary and static outcome predictions. Fans and engineers lack tools to simulate alternative decisions under stochastic race conditions.
- **Our Solution**: PITWALL combines historical telemetry, statistical degradation models, probabilistic overtaking mechanisms, and paired Monte Carlo simulation with Common Random Numbers to quantify Utility Regret and answer counterfactual race questions.
- **Data & Rigor**: Uses FastF1 and Jolpica API data across 4 iconic holdout races, backed by DuckDB OLAP storage, strict temporal cross-validation, and model ablation suites.
