# PITWALL — Model & Simulation Validation Protocol

`docs/VALIDATION.md`

---

## 1. Validation Philosophy: Separation of Tasks

To ensure scientific defensibility, PITWALL strictly separates **Predictive Model Validation** (evaluating models against empirical ground-truth observations) from **Counterfactual Evaluation** (evaluating unobserved hypothetical strategies):

```
                                    ┌────────────────────────────────────────────────────────┐
                                    │                   VALIDATION FRAMEWORK                 │
                                    └───────────────────────────┬────────────────────────────┘
                                                                │
                                ┌───────────────────────────────┴───────────────────────────────┐
                                ▼                                                               ▼
    ┌───────────────────────────────────────────────────────┐       ┌───────────────────────────────────────────────────────┐
    │ 1. PREDICTIVE VALIDATION (Empirical Ground Truth)     │       │ 2. COUNTERFACTUAL EVALUATION (Unobserved Futures)     │
    ├───────────────────────────────────────────────────────┤       ├───────────────────────────────────────────────────────┤
    │ - Actual Lap Times vs Model Predictions               │       │ - Paired Monte Carlo Simulations (Common Random Numbers│
    │ - Actual Race Winners vs Binary Win Probabilities     │       │ - Utility Regret U(a*) - U(a) & Expected Position Delta│
    │ - Actual Finish Positions vs Multiclass Distributions │       │ - 95% Confidence Intervals for Pairwise Delta U       │
    │ - Metrics: RMSE, Brier Score, RPS, EMD                │       │ - Qualitative Sanity Checks (Expert Consensus treated │
    │                                                       │       │   strictly as sanity check, NOT ground truth)         │
    └───────────────────────────────────────────────────────┘       └───────────────────────────────────────────────────────┘
```

---

## 2. Statistical Metrics & Evaluation Methodology

### 2.1 Continuous Lap Time & Pace Metrics
- **Root Mean Squared Error (RMSE)**: Evaluated on clean-air, green-flag laps across temporal holdout seasons.
- **Mean Absolute Error (MAE)**: Evaluated specifically on high-age tyre stints (\( a > 15 \text{ laps} \)).

### 2.2 Binary Outcome Metrics (Win Probability)
- **Brier Score**: Evaluates binary win probability calibration:
  \[
  \text{BS} = \frac{1}{N} \sum_{i=1}^N (y_i - \hat{p}_i)^2 \quad \text{where } y_i \in \{0, 1\}
  \]
- **Binary Log Loss & Reliability Diagrams**: Visualizes calibration across probability deciles (0–10%, 10–20%, ..., 90–100%).

### 2.3 Multiclass & Distributional Metrics (P1–P20 Finish Distributions)
- **Ranked Probability Score (RPS)**: Measures calibration of ordered position probability distributions:
  \[
  \text{RPS} = \frac{1}{K-1} \sum_{m=1}^{K-1} \left( \sum_{k=1}^m \hat{p}_k - \sum_{k=1}^m y_k \right)^2 \quad (K=20)
  \]
- **Earth Mover's Distance (EMD / 1D Wasserstein)**: Quantifies structural distance between simulated position histograms and actual observed final standings.
- **Probability Integral Transform (PIT) Histograms**: Verifies uniform coverage of predicted quantile distributions.

---

## 3. Quantitative Target Benchmarks `[ILLUSTRATIVE TARGETS]`

*Note: The numerical values below represent illustrative target hypotheses to be empirically measured during validation. They are NOT hardcoded ground truths.*

| Evaluation Metric | Target Hypothesis `[ILLUSTRATIVE]` | Minimum Acceptable `[ILLUSTRATIVE]` | Primary Target Domain |
| :--- | :--- | :--- | :--- |
| **Pace Model Lap Time RMSE** | \( < 0.32 \text{s} \) | \( < 0.45 \text{s} \) | Green-flag clean-air laps |
| **Tyre Degradation MAE** | \( < 0.25 \text{s/lap} \) | \( < 0.40 \text{s/lap} \) | High-age tyre stints (\( a > 15 \)) |
| **Final Race Position MAE** | \( < 1.2 \text{ positions} \) | \( < 2.0 \text{ positions} \) | 20-lap remaining simulation horizon |
| **Win Probability Brier Score** | \( < 0.08 \) | \( < 0.14 \) | Race winner binary prediction |
| **Position Distribution RPS** | \( < 0.06 \) | \( < 0.10 \) | Full 20-car finish order distribution |

---

## 4. Counterfactual Evaluation Protocol (Common Random Numbers & Indistinguishability)

Counterfactual outcomes cannot be validated against direct empirical ground truth because alternative decisions were never run in reality. PITWALL evaluates counterfactual quality via:

1. **Paired Common Random Numbers (CRN) Variance Reduction**: Counterfactual strategy runs reuse identical exogenous random seeds \( \omega_m \), isolating strategy variance from environmental noise.
2. **Utility Regret & Position Delta Bounds**: Reports Utility Regret \( U(a^*) - U(a) \ge 0 \) alongside Expected Position Delta \( \mathbb{E}[\mathbf{P}(a)] - \mathbb{E}[\mathbf{P}(a^*)] \).
3. **Precise Indistinguishability Criterion**: Strategies \( a_1, a_2 \) are flagged as **Statistically Indistinguishable** if \( 0 \in \text{CI}_{95\%}(\Delta U_{a_1, a_2}) \).
4. **Qualitative Sanity Checks**: Retrospective comparisons against consensus expert post-race analysis serve purely as **qualitative sanity checks**, never as mathematical ground truth.
5. **No Hardcoded Test Expectations**: Tests assert structural mathematical properties, non-negativity of Utility Regret, and proper execution of fitted models without asserting fixed numerical results.

---

## 5. Model Ablation & Reproducibility Requirements

To evaluate the contribution of individual architectural components, `scripts/evaluate.py` supports **Model Ablation Flags**:
- `--no-tyre-deg`: Replaces degradation model with flat pace.
- `--no-traffic`: Disables dirty air delay and overtaking friction.
- `--no-weather-markov`: Replaces dynamic weather transitions with static weather.

**Reproducibility Requirement**: Every evaluation run outputs a deterministic execution hash based on dataset checksum, model parameters, and random seed (`seed=42`).
