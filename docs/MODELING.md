# PITWALL — Statistical & Machine Learning Modeling Specification

`docs/MODELING.md`

---

## 1. Overview & Predictive Hierarchy

PITWALL relies on three decoupled, statistical/ML models to feed the Monte Carlo simulation engine:

1. **Tyre Degradation Model**: Predicts the continuous pace loss per lap \( \Delta T_{\text{deg}}(\text{compound}, \text{age}, \text{track\_temp}, \dots) \).
2. **Expected Pace Baseline Model**: Predicts clean air base lap pace for a driver/car combination on fresh tyres at a given race phase.
3. **Probabilistic Race Incident & Weather Model**: Estimates lap-by-lap probabilities of Safety Car (SC), Virtual Safety Car (VSC), and rain onset.

```
┌────────────────────────────────────────────────────────────┐
│                    Predictive Pipeline                     │
├──────────────────────┬──────────────────────┬──────────────┤
│ Tyre Degradation     │ Pace Baseline Model  │ Incident/Wx  │
│ - Compound wear      │ - Car/Driver delta   │ - SC/VSC p   │
│ - Thermal thermal    │ - Fuel mass decay    │ - Rain Markov│
└──────────┬───────────┴──────────┬───────────┴──────┬───────┘
           │                      │                  │
           └──────────────────┬───┴──────────────────┘
                              ▼
           ┌─────────────────────────────────────┐
           │ Vectorized Monte Carlo Simulator    │
           └─────────────────────────────────────┘
```

---

## 2. Tyre Degradation Model Design

### 2.1 Problem Formulation
Let \( \text{LapTime}_{i, d, c, t} \) be the lap time of driver \( d \) in constructor \( c \) on lap \( t \) with tyre age \( a \). We decompose lap time into:

\[
\text{LapTime}_{i, d, c, t} = \text{BasePace}_{d, c, t} + \text{FuelPenalty}(t) + f_{\text{deg}}(a, \text{compound}, \text{track\_temp}, \text{car}) + \text{TrafficPenalty} + \epsilon
\]

Target variable for the Tyre Degradation Model:
\[
y_{\text{deg}} = \text{LapTime}_{\text{accurate}} - \text{BasePace}_{\text{fresh}} - \text{FuelEffect}
\]

### 2.2 Feature Matrix
| Feature Name | Type | Description |
| :--- | :--- | :--- |
| `tyre_age` | int | Laps completed on current tyre set \( a \in [1, 50] \). |
| `tyre_age_sq` | float | Quadratic age term \( a^2 \) (captures non-linear cliff). |
| `compound` | categorical | Standardized compound (`SOFT`, `MEDIUM`, `HARD`, `INTER`, `WET`). |
| `track_temp_c` | float | Track surface temperature in °C. |
| `air_temp_c` | float | Ambient temperature in °C. |
| `circuit_abrasiveness` | float | Index [1.0, 5.0] derived from historical circuit wear statistics. |
| `constructor_deg_mult` | float | Derived team tyre management coefficient. |
| `is_fresh` | bool | 1 if tyre set was unused prior to stint, 0 if scrubbed. |

### 2.3 Evaluated Model Families
1. **Baseline**: Linear Regression per compound: \( y = \beta_0 + \beta_1 \cdot a \).
2. **Generalized Additive Models (GAM)**: Spline-based smooth curves for tyre cliff: \( y = s(a) + s(\text{track\_temp}) + \text{compound} \).
3. **Random Forest / Extra Trees Regressor**: Non-parametric tree ensemble.
4. **LightGBM / XGBoost Regressor**: Gradient boosted decision trees with monotone constraints on `tyre_age` (lap pace must not improve purely due to tyre aging under green flag).

### 2.4 Baseline vs Preferred Model Selection Criteria
- **Primary Metric**: Root Mean Squared Error (RMSE) in seconds/lap under green-flag conditions.
- **Secondary Metric**: Mean Absolute Error (MAE) on high-age laps (\( a > 15 \)).
- **Success Threshold**: RMSE \( \le 0.35 \) seconds/lap across temporal holdout test set.
- **Fallback**: If LightGBM overfits or lacks data for rare compounds, fallback to regularized GAM / quadratic polynomial per compound.

---

## 3. Pace Baseline & Fuel Load Model Design

### 3.1 Base Pace Formulation
Car weight decreases by ~0.8kg to 1.1kg per lap as fuel burns, improving lap time by roughly \( 0.03 \text{s} - 0.045 \text{s} \) per lap.

\[
\text{BasePace}(t) = \mu_{\text{circuit}} + \delta_{\text{constructor}} + \delta_{\text{driver}} - \gamma_{\text{fuel}} \cdot (N_{\text{total}} - t)
\]

Where:
- \( \mu_{\text{circuit}} \): Baseline circuit benchmark pace.
- \( \delta_{\text{constructor}} \): Constructor relative performance offset.
- \( \delta_{\text{driver}} \): Driver relative skill offset.
- \( \gamma_{\text{fuel}} \): Fuel burn rate gain coefficient (~0.035 s/lap).

### 3.2 Traffic & Overtaking Penalty
When a car is within 1.0 second of the car ahead (`interval_to_ahead <= 1.0s`), dirty air reduces downforce and lap pace by a traffic delay factor:
\[
\text{PaceLoss}_{\text{traffic}} = \mathcal{N}(\mu_{\text{dirty\_air}}, \sigma_{\text{dirty\_air}}^2) \quad \text{where } \mu_{\text{dirty\_air}} \approx 0.4 \text{s/lap}
\]

---

## 4. Probabilistic Incident & Weather Models

### 4.1 Safety Car / VSC Probability Model
Safety Car probability is modeled as a Bernoulli trial per lap \( t \):
\[
P(\text{SC}_t = 1) = \text{Bernoulli}(\lambda_{\text{circuit}} \cdot \text{PhaseMult}(t))
\]
Where \( \lambda_{\text{circuit}} \) is the historical SC rate per lap for the circuit (e.g., Monaco = 0.06, Monza = 0.015), and `PhaseMult(t)` elevates probability on Lap 1 (start congestion) and late race restart laps.

### 4.2 Weather State Transition (Markov Chain)
Track condition is modeled as a discrete-time Markov Chain with states \( S \in \{\text{DRY}, \text{DAMP}, \text{WET}\} \):

\[
P(S_{t+1} \mid S_t) = \begin{bmatrix} P_{\text{dry}\to\text{dry}} & P_{\text{dry}\to\text{damp}} & 0 \\ P_{\text{damp}\to\text{dry}} & P_{\text{damp}\to\text{damp}} & P_{\text{damp}\to\text{wet}} \\ 0 & P_{\text{wet}\to\text{damp}} & P_{\text{wet}\to\text{wet}} \end{bmatrix}
\]

Transition probabilities are conditioned on decision-time weather forecasts or historical race rain transition distributions.

---

## 5. Temporal Leakage Prevention Protocol

To strictly eliminate temporal leakage:
1. **Train/Val/Test Split**: Training set strictly consists of historical seasons prior to target season (e.g., train on 2018–2022, validate on 2023, holdout test on 2024).
2. **Rolling-Origin Evaluation**: When evaluating Lap \( t \), feature transformations and driver pace baselines are computed using strictly data available at or prior to Lap \( t \). Future lap information from the target race is completely inaccessible to the model pipeline.
