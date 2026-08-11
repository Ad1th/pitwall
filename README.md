# PITWALL — The Counterfactual Race Strategy Engine

> **Don't analyze the race. Re-run it.**

PITWALL is an open-source sports analytics platform built for the **AQX Sports Analytics Data Bowl 3.0**. It reconstructs historical Formula 1 race states \( \text{RaceState}(t) \) and evaluates counterfactual race strategies using statistical tyre degradation models, fuel pace decay equations, probabilistic overtaking friction kernels, and vectorized Monte Carlo simulation.

---

## 🏎️ Core Features

- **Race State Reconstruction**: Reconstructs complete spatial vectors for all 20 drivers at any historical lap across two operational modes (**Decision-Time Mode** vs **Hindsight / Oracle Mode**).
- **Probabilistic Overtaking Mechanism**: Models dirty air pace delays and logistic overtake probabilities for 20-car traffic dynamics.
- **Vectorized Monte Carlo Simulator**: Simulates 5,000 randomized race futures in under 300ms using NumPy array broadcasting while prioritizing physical model correctness.
- **Coarse-to-Fine Strategy Optimizer**: Screens multi-stop strategies via fast coarse grid search (500 runs) and refines top candidates at 1-lap resolution (5,000 runs).
- **Strategy Regret & Confidence Engine**: Quantifies position regret with 95% Monte Carlo confidence bounds and flags statistically indistinguishable strategies.
- **Automated Race Autopsy**: Ranks key strategic decisions throughout a race by position regret impact without hardcoded pre-determined outcomes.
- **Telemetry Command Center**: Dark-mode telemetry UI featuring glassmorphic components, interactive lap scrubbers, mode toggles, and probability density curves with shaded confidence regions.

---

## 🛠️ Technology Stack

- **Data Ingestion**: `FastF1`, `Jolpica-F1 API`, `OpenF1` (Supplemental 2023+)
- **Analytical Storage**: `DuckDB` (Embedded OLAP)
- **Predictive ML**: `scikit-learn`, `LightGBM`, `SciPy`
- **Monte Carlo Engine**: Vectorized `NumPy`
- **Backend API**: `FastAPI` (Python 3.11+)
- **Frontend UI**: `React` (Vite) + Custom Telemetry Vanilla CSS

---

## 📚 Documentation Index

- [`docs/PRD.md`](docs/PRD.md) — Authoritative Product Requirement Document
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — End-to-End System Architecture Specification
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) — F1 Data Ecosystem & Data Rights Specification
- [`docs/MODELING.md`](docs/MODELING.md) — Statistical & Machine Learning Models Specification
- [`docs/DATABASE.md`](docs/DATABASE.md) — DuckDB Schema & Entity Relationship Diagram
- [`docs/API.md`](docs/API.md) — REST API Endpoints Specification
- [`docs/UI.md`](docs/UI.md) — Frontend User Experience & Chart System
- [`docs/VALIDATION.md`](docs/VALIDATION.md) — Model Validation Protocol & Benchmarks
- [`docs/DEVELOPMENT_PLAN.md`](docs/DEVELOPMENT_PLAN.md) — 16-Stage Implementation Roadmap
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — Architectural Decision Records (ADRs)
- [`docs/AGENT_WORKFLOW.md`](docs/AGENT_WORKFLOW.md) — Workflow Instructions for Future Agents

---

## 🚦 Quick Start (Development)

```bash
# Clone repository
git clone https://github.com/your-org/pitwall.git
cd pitwall

# Seed DuckDB database with benchmark races
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
python scripts/seed_db.py --race 2021-abu-dhabi

# Start FastAPI backend server
uvicorn backend.app.main:app --reload --port 8000

# Start React frontend UI (in a separate terminal)
cd frontend
npm install
npm run dev
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
