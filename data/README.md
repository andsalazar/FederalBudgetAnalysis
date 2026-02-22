# Data Provenance & Reproduction Guide

This document specifies every external data source consumed by the analysis
pipeline, along with download instructions and expected file manifests. A
reviewer should be able to reproduce all tables in `output/FINDINGS.md` by
following these steps on a clean machine.

---

## 1. Environment Setup

```bash
# Create and activate a fresh environment (conda or venv)
conda create -n fba python=3.13 -y && conda activate fba
# — or —
python -m venv .venv && source .venv/bin/activate  # Unix
python -m venv .venv && .venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### FRED API Key

Many collection scripts require a
[FRED API key](https://fred.stlouisfed.org/docs/api/api_key.html) (free
registration).  Set it **one** of two ways:

| Method | Example |
|--------|---------|
| Environment variable (preferred) | `export FRED_API_KEY=your_key` |
| `config.yaml` field | `collectors.fred.api_key: "your_key"` |

---

## 2. Data Sources

### 2.1 Federal Reserve Economic Data (FRED)

| Item | Detail |
|------|--------|
| Provider | Federal Reserve Bank of St. Louis |
| URL | <https://fred.stlouisfed.org/> |
| API docs | <https://fred.stlouisfed.org/docs/api/fred/> |
| Series count | 48 macro-economic series (GDP, CPI, employment, interest) + 12 CPI sub-indices + 11 BEA NIPA government spending series |
| Frequency | Monthly / quarterly / annual (varies by series) |
| Time span | 1947 – 2026 |
| Collection script | `collect_granular_data.py`, `src/collectors/fred_collector.py` |
| Observations | ~53,291 |

Key FRED series IDs used (non-exhaustive):

- **GDP/GNP:** `GDP`, `GDPC1`, `GNP` …
- **CPI:** `CPIAUCSL`, `CPILFESL`, sub-indices for vehicles, apparel, food, electronics, etc.
- **Employment:** `UNRATE`, `PAYEMS`, `CE16OV` …
- **Interest:** `DGS10`, `FEDFUNDS` …

The full list of series is stored in `config.yaml` under `collectors.fred.series`.

### 2.2 U.S. Treasury Fiscal Data (Monthly Treasury Statement)

| Item | Detail |
|------|--------|
| Provider | U.S. Department of the Treasury, Bureau of the Fiscal Service |
| URL | <https://fiscaldata.treasury.gov/> |
| API endpoint | `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/` |
| Tables | MTS Table 5 (Outlays by Budget Function) & Table 9 (Outlays by Agency) |
| Frequency | Monthly (aggregated to fiscal-year) |
| Time span | FY 2015 – FY 2025 |
| Collection scripts | `collect_budget_functions.py`, `collect_agency_outlays.py` |
| Observations | ~11,197 |
| Authentication | None required (public API) |

### 2.3 Congressional Budget Office (CBO) Historical & Projections

| Item | Detail |
|------|--------|
| Provider | Congressional Budget Office |
| Publications | *The Budget and Economic Outlook: 2026 to 2036* (Feb 2026) |
| URL | <https://www.cbo.gov/publication/61882> |
| Files used | `Annual_CY_February2026.csv` (economic variables) |
| Location | `data/raw/Annual_CY_February2026.csv` |
| Series count | 67 historical budget aggregates |
| Time span | FY 1962 – FY 2035 (projections) |
| Collection script | `load_cbo_data.py` |
| Observations | ~4,691 |

**Manual download:** Download the supplemental data ZIP from the CBO
publication page, extract `Annual_CY_February2026.csv`, and place it in
`data/raw/`.

### 2.4 Census Bureau — Income Distribution (Table H-2)

| Item | Detail |
|------|--------|
| Provider | U.S. Census Bureau |
| Table | Historical Income Tables, Table H-2 |
| URL | <https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html> |
| Series | Household income quintile shares (Bottom 20% … Top 5%) |
| Time span | 2000 – 2023 (24 annual observations) |
| Collection script | `collect_historical_distribution.py` |

### 2.5 CPS ASEC Microdata

| Item | Detail |
|------|--------|
| Provider | U.S. Census Bureau, via Census Bureau API |
| Surveys | Current Population Survey, Annual Social and Economic Supplement |
| Benchmark years | CY 2002, 2005, 2008, 2011, 2014, 2017, 2020, 2023 |
| Primary cross-section | CPS ASEC March 2024 (income reference year CY 2023) |
| Collection script | `acquire_cps_asec.py` |
| Total records | ~1.4 million person-records (benchmarks) + 115,836 (primary) |

**Key variables used:**

| Variable | Description |
|----------|-------------|
| `PH_SEQ` | Household sequence identifier |
| `MARSUPWT` | Supplement person weight |
| `PTOTVAL` | Total person income |
| `ERN_VAL` | Earnings |
| `SS_VAL` | Social Security income |
| `SSI_VAL` | Supplemental Security Income |
| `PAW_VAL` | Public assistance / welfare income |
| `VET_VAL` | Veterans' payments |
| `UC_VAL` | Unemployment compensation |
| `FEDTAX_AC` | Federal income tax (Census model) |
| `FICA` | Social insurance contributions |

**Output file:** `data/external/cps_asec_2024_microdata.csv`

### 2.6 Bureau of Labor Statistics — Consumer Expenditure Survey (CEX)

| Item | Detail |
|------|--------|
| Provider | BLS |
| Publication | Consumer Expenditure Surveys, 2023 Annual Report |
| URL | <https://www.bls.gov/cex/tables.htm> |
| Table | Table 1101 — Quintiles of income before taxes |
| Usage | Expenditure shares by income quintile for tariff-incidence weighting |
| Derived output | `output/tables/b50_calibration.json` |

The CEX table is hand-entered in `compute_b50_calibration.py`. The B50
calibration factor (0.414 × Q4) is documented in §2.5 of FINDINGS.md and
validated against CPS ASEC person-weighted household income.

---

## 3. Processed / Derived Data

These files are generated by analysis scripts and should **not** be edited
manually:

| File | Generated by | Description |
|------|-------------|-------------|
| `data/processed/cbo_25year_trends.csv` | `run_25year_analysis.py` | 26-year budget aggregates |
| `data/processed/derived_25year_series.csv` | `run_25year_analysis.py` | Derived ratio series |
| `data/processed/census_income_quintiles.csv` | `collect_historical_distribution.py` | Census H-2 time series |
| `data/processed/cps_asec_historical_quintiles.csv` | `acquire_cps_asec.py` | 8-year microdata quintile stats |
| `output/tables/structural_break_tests.json` | `run_25year_analysis.py` | Z-scores for 4 structural breaks |
| `output/tables/counterfactual_analysis_results.json` | `run_counterfactual_analysis.py` | CBO counterfactual + B50 attribution |
| `output/tables/robustness_summary.json` | `run_robustness_checks.py` | 6-dimension robustness battery |
| `output/tables/tariff_incidence_analysis.json` | `run_tariff_incidence_analysis.py` | CPI pass-through estimates |
| `output/tables/real_terms_analysis.json` | `run_real_analysis.py` | CPI-deflated real terms |
| `output/tables/b50_calibration.json` | `compute_b50_calibration.py` | CEX→B50 mapping weights |

---

## 4. Database

The pipeline stores all collected data in a local SQLite database:

| File | Description |
|------|-------------|
| `federal_budget.db` | 160+ economic series, ~69,000 observations |

The database is created automatically by the collection scripts. Schema is
defined in `src/database/models.py` (tables: `economic_series`,
`observations`).

---

## 5. Reproduction Steps

```bash
# 1. Install dependencies
make install

# 2. Collect raw data (requires FRED API key + network access)
make data

# 3. Run unit tests
make test

# 4. Run full analysis pipeline
make analysis

# 5. (Optional) Generate figures and report
make figures
make report
```

Or, equivalently:

```bash
make all   # install + test + analysis in one step
```

### Expected runtime

| Step | Approximate time |
|------|-----------------|
| `make data` | 5–15 min (network-bound) |
| `make test` | < 2 sec |
| `make analysis` | 2–5 min (bootstrap-bound) |

---

## 6. Versioning & Reproducibility Notes

- **Python version:** Tested on 3.13.5 (Windows 11); compatible with ≥ 3.10.
- **Random seeds:** All stochastic procedures (bootstrap, simulation) use
  fixed seeds (`np.random.RandomState(42)`) for exact reproducibility.
- **CBO data vintage:** February 2026 baseline (publication 61882).
- **CPS ASEC vintage:** March 2024 supplement (income reference CY 2023).
- **FRED data:** Retrieved through January 2026 CPI releases.
- **FY 2025 data provenance:** Treasury MTS through June 2025; remaining
  months annualized using seasonal factors from FY 2019–FY 2024.
