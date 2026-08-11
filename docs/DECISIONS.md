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
- **Context**: The simulation kernel must compute 5,000 randomized race futures across 20 cars over 30+ laps within 500ms to maintain real-time web UI responsiveness.
- **Alternatives Considered**:
  1. Pure Python nested loops
  2. Multiprocessing / Celery task queues
  3. Vectorized 3D NumPy array operations (`N_sims, N_drivers, N_laps`)
- **Decision**: Implement a **Vectorized 3D NumPy Kernel**.
- **Rationale**: Array broadcasting in C-native NumPy eliminates Python interpreter overhead, enabling 5,000 race futures to be calculated in under 300ms on standard CPUs without complex process management or IPC serialization latency.
- **Consequences**: Simple, single-threaded high performance. Maximum reproducibility with deterministic seed management (`np.random.default_rng(seed)`).

---

## ADR-003: Primary Data Ingestion Library

- **Status**: Accepted
- **Context**: Need reliable, legal, open-source access to Formula 1 lap timing, telemetry, tyre compounds, and weather telemetry.
- **Alternatives Considered**:
  1. Web scraping official f1.com timing pages (High fragile risk, potential TOS issues)
  2. Deprecated Ergast API directly (Ceased updates at end of 2024)
  3. FastF1 Python Library + Jolpica F1 API (Official open-source standard)
- **Decision**: Adopt **FastF1** coupled with **Jolpica-F1 API**.
- **Rationale**: FastF1 handles timing data parsing, local disk caching, and compound extraction out-of-the-box. Jolpica provides robust Ergast-compatible REST endpoints for historical classifications.
- **Consequences**: Standardized data structures. Built-in rate-limit protection and offline caching.

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
