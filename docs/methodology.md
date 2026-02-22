# Research Methodology

## Overview

This project employs a combination of descriptive time-series analysis,
econometric modeling, and counterfactual estimation to assess the impact of
U.S. fiscal and trade policy changes on federal budgets and taxpayer welfare
over FY 2000 – FY 2025 (26 annual observations). The primary data sources are
the CBO Historical Budget Data, U.S. Treasury Monthly Treasury Statement,
FRED macro series, CPS ASEC microdata, and BLS Consumer Expenditure Survey.
Detailed provenance information is in `data/README.md`.

---

## Analytical Framework

### 1. Structural Trend Analysis (§3 of FINDINGS)

We fit OLS time-trends to 32 budget aggregates over FY 2000 – FY 2024 (the
pre-policy training window) and test whether FY 2025 deviates significantly
using prediction standard errors:

$$
SE_{pred} = \hat\sigma \sqrt{1 + \frac{1}{n} + \frac{(x_{new} - \bar x)^2}{SS_x}}
$$

where $\hat\sigma$ is the residual standard deviation from the training
regression, $n = 25$ training observations, and $SS_x = \sum (x_i - \bar x)^2$.
The z-score is $(y_{2025} - \hat y_{2025}) / SE_{pred}$, interpreted against
a $|z| > 2.0$ threshold. This formula accounts for both residual uncertainty
and the leverage of the extrapolation point.

**Implementation:** `run_25year_analysis.py → run_structural_break_tests()`
using `scipy.stats.linregress()`.

### 2. Interrupted Time Series (§4 of FINDINGS)

For within-year dynamics, we estimate segmented regressions of the form:

$$
Y_t = \beta_0 + \beta_1 t + \beta_2 D_t + \beta_3 (t - T_0) D_t + \varepsilon_t
$$

where $D_t = \mathbf{1}[t \ge T_0]$ is the post-intervention indicator.
$\beta_2$ captures the immediate level shift; $\beta_3$ captures the change
in trend slope.

Standard errors use **Newey–West HAC** covariance with lag length
$L = \max\bigl(1,\; \lfloor 0.75 \, T^{1/3} \rfloor\bigr)$
following Schwert (1989), correcting for serial correlation in quarterly
fiscal series.

**Implementation:** `src/analysis/policy_impact.py → interrupted_time_series()`
using `statsmodels.OLS` with `cov_type='HAC'`.

### 3. Tariff Incidence & Pass-Through (§6 of FINDINGS)

We measure consumer-price pass-through using 12 CPI-U sub-indices (FRED,
through January 2026) for tariff-affected goods vs. control goods. The
Spearman rank correlation between tariff exposure and price acceleration
provides a non-parametric test of pass-through.

Deadweight loss (DWL) is estimated as a multiplier on the direct tariff
revenue:

$$
\text{DWL multiplier} = 1 + \frac{1}{2}\,\varepsilon_d\,\varepsilon_s
    \frac{t^2}{\varepsilon_d + \varepsilon_s}
$$

Default elasticities: $\varepsilon_d = 0.5$, $\varepsilon_s = 1.0$,
effective tariff rate $t = 0.25$, yielding DWL multiplier ≈ 1.4×.
Sensitivity analysis varies each elasticity ±50% (Table 14).

**Implementation:** `run_tariff_incidence_analysis.py`

### 4. Distributional Attribution (§5–6 of FINDINGS)

Spending cuts and tariff consumer burden are attributed to income quintiles
using program-specific propensity weights derived from CPS ASEC receipt data
(Medicaid, SSI, public assistance, EITC/CTC concentrations).

The **bottom 50%** (B50) is defined via a CPS ASEC–calibrated CEX mapping:
$$
B50 = Q1 + Q2 + Q3 + 0.414 \times Q4
$$
yielding 186.5 million persons. The 0.414 factor is the share of Q4
persons with household income below the CPS ASEC person-weighted 50th
percentile ($96,000), derived in `compute_b50_calibration.py` and validated
against BLS CEX 2023 expenditure quintile boundaries.

This mapping is applied consistently in both the spending-cut attribution
(`run_counterfactual_analysis.py`) and the robustness checks
(`run_robustness_checks.py`).

### 5. Counterfactual & CBO Baseline (§4 of FINDINGS)

The FY 2025 counterfactual is defined as the CBO January 2025 baseline
projection (*The Budget and Economic Outlook: 2025 to 2035*). The spending
gap ($188B) is decomposed by budget function (Medicaid, income security,
nondefense discretionary, other) and attributed distributionally per §4 above.

### 6. Robustness Battery (§8 of FINDINGS)

Six robustness dimensions are tested:

1. **Alternate CBO baselines** — Vary the counterfactual ±10%
2. **Elasticity sensitivity** — DWL multiplier under alternate $\varepsilon_d, \varepsilon_s$
3. **Income concept** — Pre-tax vs. post-tax B50 shares
4. **Time window** — Restrict to FY 2005 – FY 2025 (shorter training period)
5. **Cluster-bootstrap confidence intervals** — 500 replications, clustered
   at the household level (preserving intra-household correlation), computing
   B50 income share and Gini with 95% percentile CIs
6. **Specification robustness** — 21 ITS specifications varying lag, window,
   and trend assumptions

All six must pass for the result to be reported as robust. The cluster
bootstrap uses vectorized NumPy fancy-indexing for performance
(`np.concatenate` over pre-grouped household row arrays).

**Implementation:** `run_robustness_checks.py`

---

## Data Processing Pipeline

1. **Collection** → Pull from FRED, Treasury, CBO, Census APIs (`make data`)
2. **Cleaning** → Handle missing values, frequency alignment, seasonal adjustment
3. **Storage** → Normalized SQLite database (`federal_budget.db`) with metadata
4. **Transformation** → Real-dollar conversion (CPI-U deflators), per-capita normalization
5. **Analysis** → Structural breaks, ITS, distributional attribution, robustness
6. **Visualization** → Publication-quality charts (`generate_charts.py`) and dashboards

See `data/README.md` for full provenance and `Makefile` for the reproducibility
pipeline.

---

## Statistical Software & Reproducibility

- **Python ≥ 3.10** (tested on 3.13.5)
- `statsmodels` ≥ 0.14 — HAC-robust OLS, ITS regression
- `scipy` ≥ 1.11 — `linregress`, hypothesis tests
- `pandas` ≥ 2.1 — Data manipulation and time-series alignment
- `numpy` ≥ 1.25 — Vectorized bootstrap, array operations
- Fixed random seeds (`np.random.RandomState(42)`) ensure exact reproducibility
  of all stochastic results (bootstrap CIs, simulated welfare distributions)
- Unit test suite (56 tests, `pytest`) validates all key formulas

---

## Limitations & Caveats

- Causal identification is inherently limited in macro-fiscal analysis.
  ITS identifies structural breaks but cannot rule out confounders with
  contemporaneous timing.
- The B50 calibration assumes stable expenditure shares within CEX quintiles;
  within-quintile heterogeneity may bias person-level attributions.
- FY 2025 data for October–June are actual (Treasury MTS); July–September
  are annualized using FY 2019 – FY 2024 seasonal factors.
- CPS ASEC misses the top 0.1% of the income distribution due to top-coding;
  our results describe distributional effects within the survey universe.
- Multiple simultaneous policy changes (tariffs, spending cuts, agency
  restructuring) make clean attribution to any single cause challenging.
- Data revisions by CBO, Treasury, or BLS may alter future replications.
