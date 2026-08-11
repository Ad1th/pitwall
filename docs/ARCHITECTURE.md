# PITWALL — End-to-End System Architecture Specification

`docs/ARCHITECTURE.md`

---

## 1. Architectural Overview

PITWALL is built as a single-repository, highly modular sports analytics system. It decouples high-performance analytical modeling (Python / NumPy / DuckDB) from modern web visualization (FastAPI / React / Recharts).

```
 ┌───────────────────────────────────────────────────────────┐
 │                      DATA INGESTION                       │
 │    FastF1 API  │  Jolpica F1 API  │  Static Kaggle CSV    │
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
 │  │ 2. Predictive Models: Tyre Deg + Pace + Weather     │  │
 │  ├─────────────────────────────────────────────────────┤  │
 │  │ 3. Monte Carlo Engine: Vectorized 5,000 Sim Runs    │  │
 │  ├─────────────────────────────────────────────────────┤  │
 │  │ 4. Counterfactual Engine: Evaluates Strategy Regret │  │
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
 └───────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Data Ingestion Engine (`backend/app/ingestion/`)
- `fastf1_adapter.py`: Wrapper for FastF1 API with built-in retry handling and disk caching.
- `jolpica_adapter.py`: Async HTTP client fetching session classifications and standings.
- `normalizer.py`: Sanitizes lap times, flags invalid out/in laps, handles compound standardization.

### 2.2 Race State Engine (`backend/app/engine/state.py`)
Reconstructs the full spatial-temporal vector \( \text{RaceState}(t) \) at any historical lap \( t \):
- Car positions \( [1 \dots 20] \)
- Inter-car time gaps (leader gap, ahead gap, behind gap)
- Current tyre compound and tyre age
- Completed stint history
- Track status (Green, Yellow, SC, VSC)

### 2.3 Monte Carlo Simulator Engine (`backend/app/engine/simulator.py`)
Vectorized simulation kernel implemented using NumPy arrays:
- **State Vector Shape**: `(N_sims=5000, N_drivers=20, N_laps_remaining)`
- **Simulation Loop**: Marches forward lap-by-lap from lap \( t \) to \( N_{\text{total}} \).
- **Stochastic Noise Injection**: Samples pace variance \( \epsilon \sim \mathcal{N}(0, \sigma_{\text{pace}}^2) \), pit stop duration variance \( \tau \sim \text{LogNormal}(\mu_{\text{pit}}, \sigma_{\text{pit}}^2) \), and Safety Car occurrence \( \text{Bernoulli}(p_{\text{sc}}) \).
- **Runtime Performance**: 5,000 iterations for 20 cars over 30 remaining laps executes in **< 450ms** on CPU via vectorized NumPy array broadcasting.

### 2.4 Counterfactual Regret Engine (`backend/app/engine/counterfactual.py`)
Runs paired baseline vs counterfactual simulations:
1. Simulates actual historical strategy \( S_{\text{actual}} \) \(\to\) yields outcome distribution \( Y_{\text{actual}} \).
2. Simulates candidate counterfactual strategy \( S_{\text{cf}} \) \(\to\) yields outcome distribution \( Y_{\text{cf}} \).
3. Computes **Strategy Regret**:
   \[
   \text{Regret}(S_{\text{cf}}) = \mathbb{E}[\text{Position}(S_{\text{actual}})] - \mathbb{E}[\text{Position}(S_{\text{cf}})]
   \]
4. Ranks decisions by strategic impact to highlight team mistakes or masterstrokes.

### 2.5 Backend API (`backend/app/api/`)
FastAPI application providing typed endpoints with Pydantic response models, CORS middleware, and DuckDB connection pooling.

### 2.6 Frontend Command Center (`frontend/`)
Single Page React Application featuring dark mode, telemetry charts, race position interactive replay, strategy decision trees, and Monte Carlo finish position density curves.

---

## 3. Technology Stack Justification

| Layer | Chosen Technology | Reason for Choice |
| :--- | :--- | :--- |
| **Backend Language** | Python 3.11+ | Native compatibility with FastF1, NumPy, SciPy, LightGBM, and DuckDB. |
| **Backend Web Framework**| FastAPI | High-speed ASGI framework with automatic OpenAPI spec generation and Pydantic validation. |
| **Database** | DuckDB | Embedded OLAP engine with zero network overhead, sub-10ms analytical queries on lap data. |
| **Monte Carlo Engine** | Vectorized NumPy | Eliminates Python loop overhead; runs 5k race simulations in under 500 milliseconds. |
| **Frontend Framework** | React / Vite | Ultra-fast HMR, modular UI components, robust charting library support. |
| **Styling** | Custom Vanilla CSS + Glassmorphism tokens | High visual impact, dark racing aesthetic without Tailwind setup overhead. |
| **Charts & Graphics** | Canvas / Recharts / D3 | High performance rendering of 5,000 Monte Carlo trajectories and lap telemetry. |
