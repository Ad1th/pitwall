# PITWALL — Statistical & Machine Learning Modeling Specification

`docs/MODELING.md`

---

## 1. Predictive Engine Architecture & Dual-Mode Framework

PITWALL relies on four statistical/ML model components feeding the Monte Carlo simulation engine:

1. **Tyre Degradation Model**: Predicts continuous lap pace wear rate \( \Delta T_{\text{deg}}(\text{compound}, \text{age}, T_{\text{track}}, \dots) \).
2. **Expected Base Pace & Fuel Model**: Estimates clean-air base lap pace for a driver/constructor combination, incorporating estimated fuel mass burn.
3. **Probabilistic Overtaking & Position Transition Model**: Determines position swaps and dirty-air traffic delays when cars interact on track.
4. **Race Incident & Weather State Model**: Operates in two distinct modes:
   - **Decision-Time Mode**: Strictly uses probabilistic information, weather forecasts, and historical SC transition rates available at lap \( t \).
   - **Hindsight / Oracle Mode**: Uses actual post-hoc realized weather and SC deployment timelines to isolate pure strategy execution from forecast error.

---

## 2. Parameter Estimation Strategy (Calibrated Priors vs Hardcoded Constants)

PITWALL does **NOT** treat parameters such as fuel mass decay or dirty air delays as immutable hardcoded constants. Instead, parameters are estimated empirically from historical lap timing telemetry using regression models with physical priors:

| Parameter Symbol | Description | Initial Calibrated Prior | Estimation Method |
| :--- | :--- | :--- | :--- |
| \( \gamma_{\text{fuel}} \) | Fuel Mass Burn Pace Gain (sec/lap) | \( \mathcal{N}(0.035, 0.005^2) \) | Estimated per circuit via clean-stint linear regression over lap index. |
| \( \delta_{\text{dirty\_air}} \) | Base Dirty Air Traffic Delay (sec/lap) | \( \mathcal{N}(0.40, 0.10^2) \) | Estimated via lap time deltas when `interval_to_ahead <= 1.0s`. |
| \( \mu_{\text{pit\_loss}} \) | Base Pit Lane Time Loss (sec) | Circuit-specific (e.g. Monza=21s, Monaco=24s) | Measured median from historical pit stop telemetry per circuit. |
| \( k_{\text{deg}} \) | Compound Wear Multiplier | Compound-specific prior | Fitted via spline / GBDT on clean-air stints. |

---

## 3. Tyre Degradation Model Design

### 3.1 Problem Formulation
Let \( \text{LapTime}_{i, d, c, t} \) be the lap time of driver \( d \) in constructor \( c \) on lap \( t \) with tyre age \( a \). We decompose lap time into:

\[
\text{LapTime}_{i, d, c, t} = \text{BasePace}_{d, c, t} - \gamma_{\text{fuel}} \cdot (N_{\text{total}} - t) + f_{\text{deg}}(a, \text{compound}, T_{\text{track}}) + \text{TrafficPenalty}_{i, t} + \epsilon
\]

Target variable for fitting:
\[
y_{\text{deg}} = \text{LapTime}_{\text{clean}} - \text{BasePace}_{\text{fresh}} + \gamma_{\text{fuel}} \cdot (N_{\text{total}} - t)
\]

### 3.2 Evaluated Model Families & Monotone Constraints
1. **Baseline**: Linear Regression per compound: \( y = \beta_0 + \beta_1 \cdot a \).
2. **Generalized Additive Models (GAM)**: Spline-based smooth curves for non-linear tyre cliff: \( y = s(a) + s(T_{\text{track}}) + \text{compound} \).
3. **LightGBM / XGBoost Regressor**: Gradient boosted decision trees enforcing **monotone non-decreasing constraints** on `tyre_age` under green-flag conditions.

---

## 4. Probabilistic Overtaking & Position Transition Mechanism

In a 20-car simulation over multiple laps, cars with varying pace and tyre wear frequently catch each other. PITWALL models position transitions through a **Two-Stage Overtaking Friction Kernel**:

### 4.1 Stage 1: Traffic Detection & Dirty Air Delay
When Car \( i \) closes within 1.0 second of Car \( j \) ahead (\( \text{Interval}_{i,j} \le 1.0\text{s} \)), Car \( i \) enters dirty air and suffers a lap pace reduction:
\[
\text{Pace}_{i, t}^{\text{actual}} = \text{Pace}_{i, t}^{\text{clean}} + \delta_{\text{dirty\_air}} \cdot \text{CircuitAeroSensitivity}
\]

### 4.2 Stage 2: Overtake Probability & Position Swap
For each lap where Car \( i \) is behind Car \( j \) with positive pace differential \( \Delta \text{Pace}_{i,j} = \text{Pace}_j - \text{Pace}_i > 0 \), the probability of a successful overtake on lap \( t \) is modeled via a logistic function:

\[
P(\text{Overtake}_{i \to j} \mid t) = \frac{1}{1 + \exp\left( -\left( \beta_0 + \beta_1 \Delta \text{Pace}_{i,j} + \beta_2 \Delta \text{TyreAge}_{i,j} + \beta_3 \text{DRS}_t - \beta_4 \text{CircuitOvertakeDifficulty} \right) \right)}
\]

- **If Overtake Succeeds** (\( u \sim U(0,1) < P(\text{Overtake}) \)): Positions in state vector swap (\( \mathbf{P}_t[i] \leftrightarrow \mathbf{P}_t[j] \)), and Car \( i \) escapes dirty air.
- **If Overtake Fails**: Car \( i \) remains behind Car \( j \), blocked at Car \( j \)'s pace plus dirty air delay for that lap.

---

## 5. Strategy Optimizer Search Space & Optimization Algorithm

The Strategy Optimizer finds candidate pit strategies \( a \in \mathcal{A} \) that maximize expected utility. To prevent exhaustive combinatorial explosion while guaranteeing deep strategic coverage, PITWALL employs a **Two-Stage Coarse-to-Fine Search**:

```
┌────────────────────────────────────────────────────────────┐
│ 1. Feasible Domain Filtering (FIA Rules & Window Constraints│
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ 2. Coarse Grid Search (Evaluate 1-Stop, 2-Stop, 3-Stop)     │
│    - Step size: 3-lap intervals across stint boundaries   │
│    - Fast 500-iteration Monte Carlo screening              │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│ 3. Fine-Grained Local Refinement                           │
│    - Top 5 candidate strategies from Coarse Search         │
│    - 1-lap step size around candidate pit laps             │
│    - Full 5,000-iteration Monte Carlo evaluation          │
└────────────────────────────────────────────────────────────┘
```

---

## 6. Uncertainty & Confidence Reporting

For any strategy evaluation \( U(a) \), PITWALL outputs full outcome distributions and statistical confidence intervals:

1. **95% Monte Carlo Confidence Bounds**: Computed via empirical 5th and 95th percentiles of simulated finish positions (\( P_{05}, P_{95} \)).
2. **Strategy Indistinguishability Test**: Two candidate strategies \( a_1, a_2 \) are flagged as **Statistically Indistinguishable** if their 95% confidence intervals overlap significantly and a two-sample Kolmogorov-Smirnov test on position outcomes fails to reject the null hypothesis at \( \alpha = 0.05 \).
3. **Regret Confidence Reporting**: Strategy Regret is reported as a point estimate with explicit standard error and confidence bounds, preventing over-confident claims on marginal strategy differences.
