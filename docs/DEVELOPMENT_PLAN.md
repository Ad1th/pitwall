# PITWALL — Implementation Roadmap & Stage Plan

`docs/DEVELOPMENT_PLAN.md`

---

## 1. Overview & Execution Strategy

PITWALL's development is broken into **16 modular, incremental stages (Stage 0 to Stage 15)** designed for rapid execution by autonomous coding agents.

**Core Principle**: Every stage must leave the repository in a fully runnable, passing state with zero breaking errors. Acceptance criteria focus on statistical validity, data integrity, and functional correctness without requiring hardcoded analytical outcomes.

---

## 2. Stage Breakdown

### Stage 0: System Blueprint & Repository Initialization *(COMPLETED)*
- **Goal**: Authoritative architecture design, database schema, data ecosystem research, and PRD specifications.
- **Files Created**: `README.md`, `docs/*.md`, `.gitignore`, `.env.example`, `docker-compose.yml`.
- **Dependencies**: None.
- **Tasks**: Initialize git repository, write all project documentation files.
- **Tests**: Verify all documentation links and repository structure.
- **Acceptance Criteria**: Repository initialized with complete, unambiguous specifications.
- **Demo Milestone**: Documentation suite complete and committed to git.
- **Must NOT Do**: Write backend/frontend code or run data downloads.

---

### Stage 1: Data Ingestion & DuckDB Pipeline Foundation
- **Goal**: Build FastF1 and Jolpica API data ingestion scripts and DuckDB schema initialization.
- **Files Affected**: `backend/app/db/`, `backend/app/ingestion/`, `scripts/seed_db.py`.
- **Dependencies**: Stage 0.
- **Tasks**: Set up DuckDB table DDL, implement `fastf1_adapter.py` and `jolpica_adapter.py`, create database seeding script for benchmark races (2021 Abu Dhabi, 2022 Monaco, 2022 Silverstone, 2023 Zandvoort). OpenF1 data is supplemental for 2023+ only.
- **Tests**: `tests/test_ingestion.py` (verifies row counts, column types, non-null lap times).
- **Acceptance Criteria**: Running `python scripts/seed_db.py --race 2021-abu-dhabi` populates DuckDB tables without error.
- **Demo Milestone**: DuckDB contains clean lap data for benchmark races.
- **Must NOT Do**: Build ML models or UI components.

---

### Stage 2: Race State Reconstruction & Dual Mode Engine
- **Goal**: Implement vector state reconstructor `RaceState(t)` supporting `Decision-Time Mode` and `Hindsight / Oracle Mode`.
- **Files Affected**: `backend/app/engine/state.py`, `backend/app/schemas/state.py`.
- **Dependencies**: Stage 1.
- **Tasks**: Implement lap state extraction returning full 20-car spatial vector at lap \( t \), compute interval gaps, track compound wear, track flag statuses, and support operational mode flags.
- **Tests**: `tests/test_state_engine.py` (verifies position ordering, gap consistency, and mode separation).
- **Acceptance Criteria**: `RaceState.from_db(race_id='2021-abu-dhabi', lap=53, mode='decision_time')` returns valid spatial vectors and gap matrices without error.
- **Demo Milestone**: State engine unit tests passing.
- **Must NOT Do**: Build Monte Carlo simulator or API server.

---

### Stage 3: Baseline Tyre Degradation, Pace & Overtaking Models
- **Goal**: Fit baseline statistical tyre degradation curves, fuel-load pace models, and logistic overtaking probability models.
- **Files Affected**: `backend/app/models/tyre_deg.py`, `backend/app/models/pace.py`, `backend/app/models/overtaking.py`.
- **Dependencies**: Stage 2.
- **Tasks**: Implement Ridge Regression and GAM models for compound wear rate; fit clean-air base pace and fuel load penalty coefficients empirically; fit logistic overtaking probability model based on pace deltas, tyre age deltas, and circuit friction.
- **Tests**: `tests/test_models.py` (verifies positive degradation slope with tyre age and valid overtaking probabilities in [0, 1]).
- **Acceptance Criteria**: Models train cleanly on historical data and return valid pace and overtaking predictions without hardcoded constant assumptions.
- **Demo Milestone**: Model training script saves weights to `models/artifacts/`.
- **Must NOT Do**: Implement LightGBM hyperparameter search or complex neural nets.

---

### Stage 4: Paired Monte Carlo Race Simulator Kernel (CRN)
- **Goal**: Build high-performance NumPy simulation engine using Common Random Numbers (CRN), overtaking friction, and statistical validity priority.
- **Files Affected**: `backend/app/engine/simulator.py`.
- **Dependencies**: Stage 3.
- **Tasks**: Implement `MonteCarloSimulator.run(state, candidate_strategies, n_sims=5000)` using vectorized array broadcasting and Common Random Numbers. Sample pace noise, pit stop variances, overtaking friction swaps, and SC probabilities.
- **Tests**: `tests/test_simulator.py` (verifies 20-car position transitions, statistical correctness, CRN pairing variance reduction, and deterministic outputs given fixed random seed).
- **Acceptance Criteria**: **Primary Criteria**: Physical state vector correctness, CRN variance reduction, and overtaking logic validation. **Optimization Target**: Execution under 450ms on CPU.
- **Demo Milestone**: Simulator test suite passing with deterministic reproducibility.
- **Must NOT Do**: Sacrifice model statistical validity for speed optimizations.

---

### Stage 5: Counterfactual Regret Engine & Strategy Optimizer
- **Goal**: Build paired counterfactual simulation engine, coarse-to-fine strategy search optimizer, Utility Regret evaluator, and confidence interval calculator.
- **Files Affected**: `backend/app/engine/counterfactual.py`, `backend/app/engine/optimizer.py`.
- **Dependencies**: Stage 4.
- **Tasks**: Implement coarse grid search screening (500 runs) + fine local refinement (5,000 runs); compute Utility Regret \( U(a^*) - U(a) \ge 0 \) and Expected Position Delta; compute 95% confidence bounds on pairwise utility differences \( \text{CI}_{95\%}(\Delta U) \); perform precise indistinguishability tests (\( 0 \in \text{CI}_{95\%}(\Delta U) \)).
- **Tests**: `tests/test_counterfactual.py`.
- **Acceptance Criteria**: Counterfactual engine runs paired CRN simulations, outputs 95% confidence intervals, flags statistically indistinguishable strategies when \( 0 \in \text{CI}_{95\%}(\Delta U) \), and computes non-negative Utility Regret without hardcoded answer assertions.
- **Demo Milestone**: Counterfactual engine CLI outputs Utility Regret score and 95% CIs.
- **Must NOT Do**: Integrate LLM natural language generator yet.

---

### Stage 6: FastAPI Backend REST Services
- **Goal**: Wrap state engine, simulator, and counterfactual engine in REST API endpoints supporting mode selection.
- **Files Affected**: `backend/app/main.py`, `backend/app/api/v1/`.
- **Dependencies**: Stage 5.
- **Tasks**: Build `/api/v1/races`, `/state/{lap}`, `/simulate`, `/counterfactual`, `/autopsy` endpoints using FastAPI and Pydantic schemas, supporting `mode` query parameter.
- **Tests**: `tests/test_api.py` (using `httpx.AsyncClient` / `TestClient`).
- **Acceptance Criteria**: OpenAPI spec interactive docs at `http://localhost:8000/docs` return 200 OK for all endpoints with correct expected utility confidence interval and outcome quantile fields.
- **Demo Milestone**: Live API server executing simulations via curl request.
- **Must NOT Do**: Build complex websocket streaming if HTTP JSON is sufficient.

---

### Stage 7: Frontend Foundation & Design System Setup
- **Goal**: Initialize React / Vite application with dark F1 telemetry design system.
- **Files Affected**: `frontend/src/index.css`, `frontend/src/components/common/`.
- **Dependencies**: Stage 6.
- **Tasks**: Configure CSS tokens, glassmorphism card components, loading spinners, and global layout shell with top navigation bar.
- **Tests**: `npm run build` succeeds cleanly without lint errors.
- **Acceptance Criteria**: App loads in browser with dark F1 telemetry styling.
- **Demo Milestone**: Skeleton frontend rendering header and layout shell.
- **Must NOT Do**: Add third-party unstyled component UI libraries.

---

### Stage 8: Race Command Center View Implementation
- **Goal**: Build main live race scrub and telemetry view with mode toggle.
- **Files Affected**: `frontend/src/views/CommandCenter.jsx`, `frontend/src/components/standings/`.
- **Dependencies**: Stage 7.
- **Tasks**: Build lap scrubber slider, operational mode toggle (`Decision-Time` vs `Hindsight`), live driver standings leaderboard, position gap meters, and tyre compound badges.
- **Tests**: Component render unit tests.
- **Acceptance Criteria**: Scrubbing lap slider updates standings table and gap deltas in real-time (< 50ms UI update).
- **Demo Milestone**: Interactive lap scrubber showing race progression.
- **Must NOT Do**: Connect strategy simulator yet.

---

### Stage 9: Interactive Strategy Simulator View
- **Goal**: Build strategy builder UI with coarse grid search, expected utility CIs, and outcome prediction quantile visualizations.
- **Files Affected**: `frontend/src/views/StrategySimulator.jsx`, `frontend/src/components/simulator/`.
- **Dependencies**: Stage 8.
- **Tasks**: Build strategy editor toolbar (coarse grid search toggle, pit lap picker, compound selector), trigger API POST `/api/v1/simulate`, and render Monte Carlo finish position density charts with shaded outcome quantiles, expected utility 95% CIs, and indistinguishability alert banners when \( 0 \in \text{CI}_{95\%}(\Delta U) \).
- **Tests**: End-to-end API simulation call integration test.
- **Acceptance Criteria**: Triggering simulation updates probability density curve, confidence bounds, and outcome quantiles within 500ms.
- **Demo Milestone**: Interactive strategy sandbox operational with confidence visualization.
- **Must NOT Do**: Over-complicate chart animations.

---

### Stage 10: Race Autopsy & Counterfactual Replay View
- **Goal**: Build retrospective autopsy report and split-screen counterfactual replay views.
- **Files Affected**: `frontend/src/views/RaceAutopsy.jsx`, `frontend/src/views/CounterfactualReplay.jsx`.
- **Dependencies**: Stage 9.
- **Tasks**: Render Utility Regret mistake ranking table with 95% CIs and Expected Position Delta, narrative breakdown cards, and dual-trajectory race replay line charts.
- **Tests**: Frontend snapshot & rendering tests.
- **Acceptance Criteria**: Autopsy view renders top ranked Utility Regret events dynamically based on API output.
- **Demo Milestone**: Complete race autopsy screen functioning.
- **Must NOT Do**: Add extraneous static text.

---

### Stage 11: Quantitative Model Validation & Model Ablation Suite
- **Goal**: Execute full temporal backtesting benchmark suite, model ablation tests, and generate calibration reports.
- **Files Affected**: `scripts/evaluate.py`, `reports/validation_results.json`, `docs/VALIDATION.md`.
- **Dependencies**: Stage 10.
- **Tasks**: Run rolling-origin evaluation across 4 benchmark holdout races; calculate RMSE, MAE, Brier scores, RPS, and EMD; execute model ablation runs (`--no-tyre-deg`, `--no-traffic`); update validation reports.
- **Tests**: Verification script execution.
- **Acceptance Criteria**: Validation suite executes and outputs empirical evaluation metrics and ablation tables without errors.
- **Demo Milestone**: Validation report generated and committed to repo.
- **Must NOT Do**: Mutate validation dataset to artificial perfection.

---

### Stage 12: Visualization & UI Polish
- **Goal**: Refine micro-interactions, smooth animations, glassmorphism glows, and empty/error state handling.
- **Files Affected**: `frontend/src/styles/`, `frontend/src/components/`.
- **Dependencies**: Stage 11.
- **Tasks**: Add hover tooltips, smooth canvas chart transitions, compound color highlights, and responsive container resizing.
- **Tests**: Visual check across screen resolutions.
- **Acceptance Criteria**: UI delivers a high visual impact matching professional F1 telemetry.
- **Demo Milestone**: High-fidelity UI complete.
- **Must NOT Do**: Introduce breaking layout shifts.

---

### Stage 13: End-to-End System Integration & Verification
- **Goal**: Execute full end-to-end pipeline test from raw data to UI simulation visualization.
- **Files Affected**: `tests/test_e2e.py`, `Makefile`.
- **Dependencies**: Stage 12.
- **Tasks**: Run full pipeline test: seed DuckDB \(\to\) train baseline model \(\to\) spin up FastAPI server \(\to\) execute simulation API call \(\to\) verify frontend response.
- **Tests**: `pytest tests/test_e2e.py`.
- **Acceptance Criteria**: `make test-e2e` passes with zero failures.
- **Demo Milestone**: Seamless end-to-end functionality verified.
- **Must NOT Do**: Add unverified new features.

---

### Stage 14: Docker Containerization & Deployment Setup
- **Goal**: Create reproducible Docker environment and local deployment Makefile.
- **Files Affected**: `Dockerfile`, `docker-compose.yml`, `Makefile`.
- **Dependencies**: Stage 13.
- **Tasks**: Write multi-stage Docker build for backend FastAPI and frontend static build (Nginx/serve); test single-command startup `docker-compose up`.
- **Tests**: `docker-compose up` smoke test.
- **Acceptance Criteria**: Entire application runs inside Docker container with full functionality.
- **Demo Milestone**: Docker container running on port 8000/3000.
- **Must NOT Do**: Rely on complex multi-cluster orchestration.

---

### Stage 15: Competition Devpost Submission & Demo Artifact Packaging
- **Goal**: Draft competition narrative, export demo video screenshots, compile open-source release package.
- **Files Affected**: `docs/DEVPOST_SUBMISSION.md`, `README.md`, `demo/`.
- **Dependencies**: Stage 14.
- **Tasks**: Write Devpost project description highlighting counterfactual decision intelligence, generate architectural diagrams, compile reproducibility guide.
- **Tests**: Final documentation check.
- **Acceptance Criteria**: Complete competition submission package ready for judges.
- **Demo Milestone**: Final competition-ready release package.
- **Must NOT Do**: Fabricate analytical results or present unverified claims.
