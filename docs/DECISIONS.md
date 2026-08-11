# PITWALL — Architectural Decision Records (ADRs)

`docs/DECISIONS.md`

---

## ADR-001: Analytical Storage Engine Selection

- **Status**: Accepted
- **Context**: PITWALL requires sub-second queries across 100,000+ lap records, sector times, and tyre age features during Monte Carlo initial state bootstrapping.
- **Alternatives Considered**:
  1. PostgreSQL (Relational DB)
  2. Pandas DataFrames directly in memory
  3. DuckDB (Embedded Columnar OLAP)
- **Decision**: Use **DuckDB** as the primary analytical database engine.
- **Rationale**: DuckDB provides zero-network overhead embedded OLAP speed, vectorization, seamless zero-copy Python arrow integration, and simple file-based persistence (`data/pitwall.duckdb`), eliminating external database setup complexity for competition judges.
- **Consequences**: Fast, zero-config deployment. Relational queries execute in under 10ms.

---

## ADR-002: Monte Carlo Simulation Implementation Strategy

- **Status**: Accepted
- **Context**: The simulation kernel must compute 5,000 randomized race futures across 20 cars over 30+ laps within 500ms while preserving physical overtaking mechanics and statistical validity.
- **Alternatives Considered**:
  1. Pure Python nested loops
  2. Multiprocessing / Celery task queues
  3. Vectorized 3D NumPy array operations (`N_sims, N_drivers, N_laps`)
- **Decision**: Implement a **Vectorized 3D NumPy Kernel**.
- **Rationale**: Array broadcasting in C-native NumPy eliminates Python interpreter overhead, enabling 5,000 race futures to be calculated in under 300ms on standard CPUs without complex process management or IPC serialization latency. Physical model validity is maintained as the primary acceptance criterion.
- **Consequences**: Simple, single-threaded high performance. Maximum reproducibility with deterministic seed management (`np.random.default_rng(seed)`).

---

## ADR-003: Primary Data Ingestion Library & Data Rights

- **Status**: Accepted
- **Context**: Need reliable, legal, open-source access to Formula 1 lap timing, telemetry, tyre compounds, and weather telemetry.
- **Alternatives Considered**:
  1. Web scraping official f1.com timing pages (High fragile risk, potential TOS issues)
  2. Deprecated Ergast API directly (Ceased updates at end of 2024)
  3. FastF1 Python Library + Jolpica F1 API (Official open-source standard) with OpenF1 as supplemental 2023+ source.
- **Decision**: Adopt **FastF1** coupled with **Jolpica-F1 API**, with OpenF1 strictly as a supplemental source for 2023+ telemetry.
- **Rationale**: FastF1 handles timing data parsing, local disk caching, and compound extraction out-of-the-box. Jolpica provides robust Ergast-compatible REST endpoints for historical classifications. Pre-2023 benchmark races operate cleanly without OpenF1 dependency. Local cache directories (`.fastf1-cache/`, `data/raw/`) are excluded from git, while redistributable synthetic feature matrices are committed.
- **Consequences**: Standardized data structures. Built-in rate-limit protection and offline caching compliance.

---

## ADR-004: Frontend Visual Design Framework

- **Status**: Accepted
- **Context**: PITWALL must deliver a premium visual impression ("F1 Pit Wall Telemetry") that wows competition judges at first glance.
- **Alternatives Considered**:
  1. Streamlit / Gradio (Quick to build, generic "hackathon" aesthetic)
  2. React + Tailwind CSS
  3. React + Custom Vanilla CSS + F1 Telemetry Glassmorphism Tokens
- **Decision**: Use **React (Vite) + Custom Vanilla CSS Design System**.
- **Rationale**: Custom Vanilla CSS gives exact control over glassmorphism filters, dark palette tokens, neon compound highlights, and smooth chart transitions without Tailwind configuration bloat or generic framework appearance.
- **Consequences**: Distinctive, professional visual branding aligned with AQX judging criteria.

---

## ADR-005: Probabilistic Overtaking Mechanism & Two-Stage Friction Kernel

- **Status**: Accepted
- **Context**: In 20-car simulations, faster cars catching slower cars require a physical, probabilistic mechanism to model position swaps and dirty-air pace penalties.
- **Alternatives Considered**:
  1. Instant unconstrained position swaps based purely on lap pace (unrealistic, ignores circuit track geometry)
  2. Fixed deterministic overtake lap delays
  3. Two-Stage Probabilistic Kernel: Dirty air pace penalty when interval \(\le 1.0\text{s}\) + logistic overtake probability based on pace deltas, tyre age deltas, and circuit friction.
- **Decision**: Adopt the **Two-Stage Probabilistic Overtaking Friction Kernel**.
- **Rationale**: Captures real-world F1 dirty air mechanics and track overtakability resistance without introducing unnecessary micro-simulation complexity.
- **Consequences**: Realistic traffic simulation and track-position defensive value modeling.

---

## ADR-006: Dual Mode Simulation Architecture (Decision-Time vs Hindsight)

- **Status**: Accepted
- **Context**: Strategy evaluation must distinguish between decisions made with incomplete decision-time information versus evaluating counterfactual execution against realized race events.
- **Alternatives Considered**:
  1. Single hybrid mode mixing future weather and past statistics (causes look-ahead ambiguity)
  2. Explicit Dual Mode Framework: **Decision-Time Mode** (strictly uses info available at lap \( t \)) and **Hindsight / Oracle Mode** (uses actual realized weather/SC timelines).
- **Decision**: Adopt the **Explicit Dual Mode Framework**.
- **Rationale**: Provides clarity for judges by clearly separating forecast uncertainty from pure strategic decision regret.
- **Consequences**: Clear API parameters (`mode: "decision_time"` vs `"hindsight"`) and transparent UI mode toggles.

---

## ADR-007: Statistical Validation Standards & Confidence Interval Reporting

- **Status**: Accepted
- **Context**: Evaluation metrics and counterfactual recommendations must be scientifically defensible without hardcoding expected historical answers or relying on expert opinion as ground truth.
- **Alternatives Considered**:
  1. Asserting fixed predetermined regret numbers in unit tests (e.g. requiring `+0.68` regret)
  2. Evaluating win probabilities with regression MSE
  3. Rigorous Task Separation: Empirical validation using Brier Score for binary win probability and RPS / EMD for 20-class position distributions; Monte Carlo 95% confidence intervals and statistical indistinguishability tests for counterfactual recommendations.
- **Decision**: Adopt **Rigorous Task Separation & 95% Confidence Interval Standards**.
- **Rationale**: Prevents scientific bias, handles strategy uncertainty honestly, and avoids false claims of certainty on marginal strategy differences.
- **Consequences**: Statistically defensible validation reporting and robust confidence interval visualizations.

---

## ADR-008: Empirical Parameter Estimation vs Hardcoded Constants

- **Status**: Accepted
- **Context**: Physical parameters such as fuel mass burn pace gain and dirty air traffic delays vary by circuit and vehicle aero package.
- **Alternatives Considered**:
  1. Hardcoding fixed constants (e.g. `0.035s/lap` fuel decay, `0.4s` dirty air delay) across all races
  2. Estimating parameters empirically per circuit/season using clean-stint telemetry with documented priors.
- **Decision**: Adopt **Empirical Parameter Estimation with Documented Priors**.
- **Rationale**: Treats physical parameters as fitted model variables, allowing PITWALL to adapt to specific circuit characteristics (e.g., Monza low-downforce vs Monaco high-downforce).
- **Consequences**: Improved pace model accuracy across diverse track layouts.
