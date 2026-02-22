# ===========================================================================
#  Federal Budget Analysis — Reproducibility Makefile
#  ---------------------------------------------------
#  Recreates every table and figure from raw inputs.
#
#  Quick-start
#  -----------
#    make install       # install Python dependencies
#    make test          # run unit tests
#    make analysis      # run the full analysis pipeline
#    make all           # install + test + analysis
#    make clean         # remove generated outputs
#
#  Prerequisites
#  -------------
#    • Python ≥ 3.10 (tested on 3.13)
#    • pip / conda environment activated
#    • FRED API key set via  FRED_API_KEY  env variable or config.yaml
#    • Raw data files in  data/raw/  (see data/README.md)
# ===========================================================================

PYTHON := python
PYTEST := $(PYTHON) -m pytest

# Directories
OUT      := output
TABLES   := $(OUT)/tables
FIGURES  := $(OUT)/figures
REPORTS  := $(OUT)/reports

# Key output artefacts
STRUCT_BREAK  := $(TABLES)/structural_break_tests.json
COUNTERFACT   := $(TABLES)/counterfactual_analysis_results.json
ROBUSTNESS    := $(TABLES)/robustness_summary.json
TARIFF        := $(TABLES)/tariff_incidence_analysis.json
REAL_TERMS    := $(TABLES)/real_terms_analysis.json
B50_CAL       := $(TABLES)/b50_calibration.json
FINDINGS_MD   := $(OUT)/FINDINGS.md

# ───────────────────────────────────────────────────────────────────────
#  Phony targets
# ───────────────────────────────────────────────────────────────────────
.PHONY: all install test analysis clean help

all: install test analysis  ## Install deps, test, run full pipeline

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'

# ───────────────────────────────────────────────────────────────────────
#  Environment
# ───────────────────────────────────────────────────────────────────────
install:  ## Install Python dependencies
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

# ───────────────────────────────────────────────────────────────────────
#  Unit tests
# ───────────────────────────────────────────────────────────────────────
test:  ## Run the test suite
	$(PYTEST) tests/ -v --tb=short

# ───────────────────────────────────────────────────────────────────────
#  Data collection  (requires network + API keys)
# ───────────────────────────────────────────────────────────────────────
data: ## Collect raw data from external APIs (FRED, Treasury, CBO)
	$(PYTHON) collect_budget_functions.py
	$(PYTHON) collect_agency_outlays.py
	$(PYTHON) collect_historical_distribution.py
	$(PYTHON) collect_granular_data.py
	$(PYTHON) load_cbo_data.py

# ───────────────────────────────────────────────────────────────────────
#  Core analysis  (deterministic from collected data)
# ───────────────────────────────────────────────────────────────────────
$(STRUCT_BREAK): run_25year_analysis.py src/analysis/policy_impact.py
	$(PYTHON) run_25year_analysis.py

$(COUNTERFACT): run_counterfactual_analysis.py compute_b50_calibration.py
	$(PYTHON) run_counterfactual_analysis.py

$(ROBUSTNESS): run_robustness_checks.py $(COUNTERFACT)
	$(PYTHON) run_robustness_checks.py

$(TARIFF): run_tariff_incidence_analysis.py
	$(PYTHON) run_tariff_incidence_analysis.py

$(REAL_TERMS): run_real_analysis.py
	$(PYTHON) run_real_analysis.py

analysis: $(STRUCT_BREAK) $(COUNTERFACT) $(ROBUSTNESS) $(TARIFF) $(REAL_TERMS)  ## Run all analysis scripts

# ───────────────────────────────────────────────────────────────────────
#  Robustness (standalone)
# ───────────────────────────────────────────────────────────────────────
robustness: $(ROBUSTNESS)  ## Run robustness checks only

# ───────────────────────────────────────────────────────────────────────
#  Figures & report
# ───────────────────────────────────────────────────────────────────────
figures: analysis  ## Generate all charts / figures
	$(PYTHON) generate_charts.py

report: analysis  ## Render FINDINGS to HTML preview
	$(PYTHON) generate_pdf.py

# ───────────────────────────────────────────────────────────────────────
#  Clean
# ───────────────────────────────────────────────────────────────────────
clean:  ## Remove generated tables, figures, and cache
	rm -f $(TABLES)/*.json $(TABLES)/*.csv
	rm -f $(FIGURES)/*.png $(FIGURES)/*.html
	rm -rf __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache
	@echo "Cleaned generated outputs."
