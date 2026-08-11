# PITWALL — User Interface & Visualization Specification

`docs/UI.md`

---

## 1. Design Aesthetics & Visual Tokens

PITWALL adopts a **Formula 1 Pit Wall Telemetry Aesthetic**: sleek dark mode, high-contrast typography (Inter / JetBrains Mono), translucent glassmorphism cards, and accent colors indicating tyre compounds and strategic alert levels.

```
┌───────────────────────────────────────────────────────────┐
│                    Design System Tokens                   │
├───────────────────┬───────────────────┬───────────────────┤
│ Dark Background   │ Glass Card        │ Accent Glow       │
│ `#0A0D14`         │ `rgba(16,22,34,0.7)`│ `#E10600` (F1 Red) │
├───────────────────┼───────────────────┼───────────────────┤
│ Soft Compound     │ Medium Compound   │ Hard Compound     │
│ `#FF1801` (Red)   │ `#FFF200` (Yellow)│ `#FFFFFF` (White) │
└───────────────────┴───────────────────┴───────────────────┘
```

---

## 2. Core User Experience Views

### 2.1 View 1: Race Command Center
- **Purpose**: Main live-replay screen displaying lap-by-lap race state, positions, and live strategy recommendations.
- **Components**:
  - **Operational Mode Toggle**: Switch between `Decision-Time Mode` (lap \( t \) forecast info) and `Hindsight / Oracle Mode` (actual realized weather/SC timeline).
  - **Lap Scrubber / Slider**: Scrub through laps 1 to \( N_{\text{total}} \).
  - **Live Standings Leaderboard**: Real-time position table with driver gap, compound badge, tyre age meter, and pit stop counter.

### 2.2 View 2: Strategy Simulator
- **Purpose**: Interactive playground enabling race engineers to run coarse grid searches or build custom multi-stop strategies using paired CRN simulations.
- **Components**:
  - **Search Strategy Toolbar**: Choose between Coarse Grid Search screening or Manual Multi-Stop Strategy Builder.
  - **Monte Carlo Finishing Density Chart**: Overlaid density curves comparing finish position probabilities with **outcome prediction quantiles** (\( q_{05}, q_{95} \)) and **95% confidence intervals on expected utility**.
  - **Indistinguishability Alert Banner**: Displays a yellow warning badge when the 95% confidence interval for pairwise utility difference contains zero (\( 0 \in \text{CI}_{95\%}(\Delta U) \)).

### 2.3 View 3: Race Autopsy
- **Purpose**: Post-race decision report detailing major strategy mistakes and masterstrokes.
- **Components**:
  - **Strategic Impact Timeline**: Interactive timeline highlighting laps where teams made high Utility Regret decisions.
  - **Mistake Ranking Table**: Ranked list of strategic errors sorted by Utility Regret \( U(a^*) - U(a) \) with 95% confidence bounds and Expected Position Delta.
  - **Explanation Card**: Human-readable narrative detailing dirty air, tyre degradation, and safety car window factors under model assumptions.

### 2.4 View 4: Counterfactual Replay
- **Purpose**: Side-by-side split screen comparing historical reality vs counterfactual race outcome under paired CRN simulations.
- **Components**:
  - **Dual Track Position Chart**: Re-runs the race with the counterfactual decision injected; displays actual vs simulated position curves with overtaking friction flags.
  - **Gap to Winner Delta**: Shows how the pit lap change impacts gap to race leader over time.

### 2.5 View 5: Team Strategy Profile
- **Purpose**: Aggregate analytics evaluating team decision-making tendencies across an entire season (e.g., Aggressiveness rating, Undercut Success Rate, Safety Car Response Efficiency).

---

## 3. Visualization Specification Matrix

| Visualization Name | Chart Type | X-Axis | Y-Axis | Interaction / Filter | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Race Position History** | Line Chart | Lap Number (1 to N) | Driver Position (1 to 20, inverted) | Hover driver to highlight trajectory; click lap to jump state. | Visualizes position changes and overtake points over race distance. |
| **Tyre Degradation Curves** | Smooth Line / Spline | Tyre Age (Laps) | Lap Time Delta (Seconds) | Filter by Compound / Constructor / Driver. | Shows compound wear rate and tyre cliff onset point. |
| **Stint Timeline Waterfall** | Horizontal Bar Chart | Lap Range | Driver / Compound | Click stint to inspect tyre age & pace. | High-level view of entire grid's pit stop timing & compound choices. |
| **Monte Carlo Finish Density** | Kernel Density + Shaded Outcome Quantiles | Finish Position (P1 to P20) | Probability Density (%) | Toggle 95% CI on mean vs outcome prediction quantiles; compare strategies. | Displays outcome uncertainty distribution and statistical overlap. |
| **Strategic Regret Heatmap** | Matrix Heatmap | Lap Number | Driver / Team | Hover cell to display Utility Regret \( U(a^*) - U(a) \) & 95% CI. | Instantly highlights critical laps where strategic choices changed race results. |
