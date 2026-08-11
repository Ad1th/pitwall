# PITWALL — End-to-End System Architecture Specification

`docs/ARCHITECTURE.md`

---

## 1. Architectural Overview

PITWALL is built as a single-repository, highly modular sports analytics system. It decouples high-performance analytical modeling (Python / NumPy / DuckDB) from modern web visualization (FastAPI / React / Recharts).

```
 ┌───────────────────────────────────────────────────────────┐
 │                      DATA INGESTION                       │
 │  FastF1 API  │  Jolpica API  │ Static Kaggle │ OpenF1(23+)│
 └────────────────────────────┬──────────────────────────────┘
                              │
                              ▼
 ┌───────────────────────────────────────────────────────────┐
 │                   ANALYTICAL STORAGE                      │
 │    DuckDB (`pitwall.duckdb`)  │  Parquet Feature Cache    │
 └────────────────────────────┬──────────────────────────────┘
                              │
                              ▼
 ┌───────────────────────────────────────────────────────────┐
 │                   CORE ANALYTICAL ENGINE                  │
 │  ┌─────────────────────────────────────────────────────┐  │
 │  │ 1. Race State Engine: Reconstructs RaceState(t)     │  │
 │  ├─────────────────────────────────────────────────────┤  │
 │  │ 2. Dual Mode Controller: Decision-Time vs Hindsight │  │
 │  ├─────────────────────────────────────────────────────┤  │
 │  │ 3. Predictive Models: Tyre Deg + Pace + Overtaking  │  │
 │  ├─────────────────────────────────────────────────────┤  │
 │  │ 4. Strategy Optimizer: Coarse-to-Fine Search        │  │
 │  ├─────────────────────────────────────────────────────┤  │
 │  │ 5. Monte Carlo Engine: Vectorized 5k Sim Runs       │  │
 │  ├─────────────────────────────────────────────────────┤  │
 │  │ 6. Counterfactual Regret & Confidence Evaluator     │  │
 │  └─────────────────────────────────────────────────────┘  │
 └────────────────────────────┬──────────────────────────────┘
                              │
                              ▼
 ┌───────────────────────────────────────────────────────────┐
 │                       REST API LAYER                      │
 │      FastAPI Python Server (`backend/app/main.py`)        │
 └────────────────────────────┬──────────────────────────────┘
                              │
                              ▼
 ┌───────────────────────────────────────────────────────────┐
 │                   FRONTEND VISUALIZATION                  │
 │      React / Next.js / Tailwind / Recharts Command Center  │
 └────────────────────────────┬──────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Data Ingestion Engine (`backend/app/ingestion/`)
- `fastf1_adapter.py`: Wrapper for FastF1 API with built-in retry handling and local disk caching (`data/cache/fastf1/`, git-ignored).
- `jolpica_adapter.py`: Async HTTP client fetching session classifications, qualifying grid, and pit stop durations.
- `openf1_adapter.py`: Supplemental telemetry fetcher for 2023+ sessions only.
- `normalizer.py`: Sanitizes lap times, flags invalid out/in laps, handles compound standardization.

### 2.2 Race State Engine (`backend/app/engine/state.py`)
Reconstructs the full spatial-temporal vector \( \text{RaceState}(t) \) at any historical lap \( t \):
- Car positions \( [1 \dots 20] \)
- Inter-car time gaps (leader gap, ahead gap, behind gap)
- Current tyre compound and tyre age
- Completed stint history
- Track status (Green, Yellow, SC, VSC)
- Operational mode (`DECISION_TIME` vs `HINDSIGHT`)

### 2.3 Monte Carlo Simulator Engine (`backend/app/engine/simulator.py`)
Vectorized simulation kernel implemented using NumPy arrays:
- **State Vector Shape**: `(N_sims=5000, N_drivers=20, N_laps_remaining)`
- **Overtaking Kernel**: Integrates two-stage overtaking friction (dirty air delay when interval \(\le 1.0\text{s}\) + logistic overtake probability position swaps).
- **Stochastic Noise Injection**: Samples pace variance \( \epsilon \sim \mathcal{N}(0, \sigma_{\text{pace}}^2) \), pit stop duration variance \( \tau \sim \text{LogNormal}(\mu_{\text{pit}}, \sigma_{\text{pit}}^2) \), and Safety Car occurrence \( \text{Bernoulli}(p_{\text{sc}}) \).
- **Statistical Validity Priority**: Simulation physical validity and overtaking mechanics are primary acceptance criteria; vectorized NumPy broadcasting targets execution in **< 450ms** on CPU.

### 2.4 Strategy Optimizer (`backend/app/engine/optimizer.py`)
Executes coarse-to-fine search:
- **Coarse Grid Search**: Screens feasible FIA compound combinations across 1-stop, 2-stop, 3-stop strategies using fast 500-run Monte Carlo iterations.
- **Fine Refinement**: Takes top 5 candidate strategies and refines pit windows at 1-lap resolution using 5,000-run Monte Carlo iterations.

### 2.5 Counterfactual Regret Engine (`backend/app/engine/counterfactual.py`)
Runs paired baseline vs counterfactual simulations:
1. Simulates actual historical strategy \( S_{\text{actual}} \) \(\to\) yields outcome distribution \( Y_{\text{actual}} \).
2. Simulates candidate counterfactual strategy \( S_{\text{cf}} \) \(\to\) yields outcome distribution \( Y_{\text{cf}} \).
3. Computes **Strategy Regret** with 95% Monte Carlo confidence intervals.
4. Performs two-sample Kolmogorov-Smirnov test to detect and flag **Statistically Indistinguishable** strategies.

### 2.6 Backend API (`backend/app/api/`)
FastAPI application providing typed endpoints with Pydantic response models, CORS middleware, DuckDB connection pooling, and `mode` flag selection.

### 2.7 Frontend Command Center (`frontend/`)
Single Page React Application featuring dark mode telemetry styling, interactive lap scrubbers, strategy search sandboxes, mode toggles, and Monte Carlo finish position density curves with 95% confidence bounds.

---

## 3. Technology Stack Justification

| Layer | Chosen Technology | Reason for Choice |
| :--- | :--- | :--- |
| **Backend Language** | Python 3.11+ | Native compatibility with FastF1, NumPy, SciPy, LightGBM, and DuckDB. |
| **Backend Web Framework**| FastAPI | High-speed ASGI framework with automatic OpenAPI spec generation and Pydantic validation. |
| **Database** | DuckDB | Embedded OLAP engine with zero network overhead, sub-10ms analytical queries on lap data. |
| **Monte Carlo Engine** | Vectorized NumPy | Eliminates Python loop overhead while preserving statistical validity and overtaking physics. |
| **Frontend Framework** | React / Vite | Ultra-fast HMR, modular UI components, robust charting library support. |
| **Styling** | Custom Vanilla CSS + Glassmorphism tokens | High visual impact, dark racing aesthetic without framework setup overhead. |
| **Charts & Graphics** | Canvas / Recharts / D3 | High performance rendering of Monte Carlo trajectories and confidence density regions. |
