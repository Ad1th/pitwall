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

PITWALL does **NOT** treat parameters such as fuel mass decay, dirty air delays, or pit-lane time loss as immutable hardcoded constants. Instead, parameters are estimated empirically from historical lap timing telemetry using regression models with physical priors:

| Parameter Symbol | Description | Initial Calibrated Prior | Estimation Method |
| :--- | :--- | :--- | :--- |
| \( \gamma_{\text{fuel}} \) | Fuel Mass Burn Pace Gain (sec/lap) | \( \mathcal{N}(0.035, 0.005^2) \) | Estimated per circuit via clean-stint linear regression over lap index. |
| \( \delta_{\text{dirty\_air}} \) | Base Dirty Air Traffic Delay (sec/lap) | \( \mathcal{N}(0.40, 0.10^2) \) | Estimated via lap time deltas when `interval_to_ahead <= 1.0s`. |
| \( \mu_{\text{pit\_loss}} \) | Estimated Pit Lane Time Loss (sec) | Circuit-specific prior (e.g. Monza ~21s, Monaco ~24s) | Measured median from historical pit stop telemetry per circuit. |
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

## 5. Strategy Optimizer Search Space & Paired Monte Carlo Engine

### 5.1 Optimization Objective & Regret Definitions
The Strategy Optimizer evaluates candidate pit strategies \( a \in \mathcal{A} \) to maximize expected utility:

\[
U(a) = \mathbb{E}_{\omega} \left[ \text{Points}(\mathbf{P}_{N_{\text{total}}}(a)) \right] - \lambda \cdot \text{Var}(\mathbf{P}_{N_{\text{total}}}(a))
\]

Let \( a^* = \arg\max_{a' \in \mathcal{A}} U(a') \) be the optimal strategy under the model. We rigorously distinguish between:

1. **Utility Regret**: The lost expected utility relative to the optimal strategy:
   \[
   \text{UtilityRegret}(a) = U(a^*) - U(a) \ge 0
   \]
   By definition, Utility Regret is non-negative and directly measures sub-optimality against the optimizer's objective.

2. **Expected Position Delta**: The difference in expected finishing position:
   \[
   \text{ExpectedPositionDelta}(a) = \mathbb{E}[\mathbf{P}_{N_{\text{total}}}(a)] - \mathbb{E}[\mathbf{P}_{N_{\text{total}}}(a^*)]
   \]
   This metric specifically measures position changes, allowing strategists to evaluate trade-offs between expected finishing rank and variance reduction.

### 5.2 Paired Monte Carlo Simulations with Common Random Numbers (CRN)
To compare candidate strategy \( a \) against baseline strategy \( a_0 \), PITWALL executes **Paired Monte Carlo Simulations using Common Random Numbers (CRN)**:
- For each simulation run \( m \in [1, M] \), both strategies are evaluated under the **exact same exogenous stochastic realizations** \( \omega_m \) (weather state transitions, Safety Car deployments, driver baseline lap pace noise, and pit stop duration noise).
- The pairwise utility difference for run \( m \) is:
  \[
  \Delta U^{(m)} = U(a, \omega_m) - U(a_0, \omega_m)
  \]
- Because exogenous environmental noise is identical across paired runs, environmental variance cancels out, dramatically reducing the variance of the estimated mean utility difference \( \Delta U \).

---

## 6. Uncertainty Distinction & Precise Indistinguishability Criterion

PITWALL strictly distinguishes between **Outcome Prediction Quantiles** and **Statistical Confidence Intervals**:

1. **Outcome Prediction Quantiles / Outcome Intervals**: The empirical 5th and 95th percentiles (\( q_{05}, q_{95} \)) of simulated finish positions across the \( M = 5,000 \) runs. These describe individual race outcome dispersion resulting from inherent race randomness.
2. **Confidence Intervals (CIs)**: Statistical bounds for estimated expected values, such as the 95% CI for expected utility \( \text{CI}_{95\%}(\mathbb{E}[U(a)]) \) or the 95% CI for the pairwise difference \( \text{CI}_{95\%}(\Delta U) \), calculated via Monte Carlo standard error:
   \[
   \text{SE}(\Delta U) = \frac{s_{\Delta U}}{\sqrt{M}} \implies \text{CI}_{95\%}(\Delta U) = \left[ \Delta U - 1.96 \cdot \text{SE}(\Delta U), \, \Delta U + 1.96 \cdot \text{SE}(\Delta U) \right]
   \]

3. **Precise Indistinguishability Criterion**:
   Two candidate strategies \( a_1 \) and \( a_2 \) are **Statistically Indistinguishable** if and only if the 95% confidence interval for their pairwise utility difference \( \Delta U_{a_1, a_2} \) contains zero:
   \[
   0 \in \text{CI}_{95\%}(\Delta U_{a_1, a_2})
   \]
   If zero is contained in the 95% CI, the system reports no statistically significant preference between \( a_1 \) and \( a_2 \). Distributional diagnostic tests (such as Kolmogorov-Smirnov or Earth Mover's Distance) serve strictly as supporting diagnostics.
