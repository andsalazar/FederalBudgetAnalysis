"""
=============================================================================
CPS ASEC 2024 MICRODATA ACQUISITION & DISTRIBUTIONAL ANALYSIS
=============================================================================

Downloads the March 2024 CPS ASEC supplement via Census Bureau API.
The 2024 ASEC reflects income/transfers received during calendar year 2023.

Key variables collected:
  - Income: earnings, wages, self-employment, dividends, interest, cap gains
  - Transfers: SS, SSI, public assistance, unemployment, veterans, disability
  - Tax estimates: federal tax (before/after credits), FICA, EITC, CTC
  - SPM: resources, thresholds, program subsidies (SNAP, WIC, school lunch)
  - Demographics: age, sex, education, race, state FIPS
  - Weights: MARSUPWT (person), HSUP_WGT (household)

Data flow:
  Census API → pandas DataFrames → SQLite database → distributional tables

Reference: Perese (2017), CBO Working Paper; Piketty, Saez & Zucman (2018) QJE
=============================================================================
"""

import sys, os, json, time, warnings
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import requests
from loguru import logger

from src.utils.config import load_config, get_output_path, PROJECT_ROOT
from src.database.models import get_session, EconomicSeries, Observation

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "https://api.census.gov/data/2024/cps/asec/mar"

# We must batch API calls (max ~50 variables per call)
# Group variables by theme for clarity

PERSON_INCOME_VARS = [
    "PTOTVAL",      # Total person income
    "PEARNVAL",     # Total person earnings
    "WSAL_VAL",     # Wage/salary earnings
    "SEMP_VAL",     # Self-employment earnings
    "FRSE_VAL",     # Farm self-employment
    "DIV_VAL",      # Dividends
    "INT_VAL",      # Interest income (total)
    "RNT_VAL",      # Rental income
    "CAP_VAL",      # Capital gains
    "OI_VAL",       # Other income
    "AGI",          # Adjusted gross income
]

PERSON_TRANSFER_VARS = [
    "SS_VAL",       # Social Security
    "SSI_VAL",      # Supplemental Security Income
    "PAW_VAL",      # Public assistance / welfare
    "UC_VAL",       # Unemployment compensation
    "VET_VAL",      # Veterans payments
    "DSAB_VAL",     # Disability income (combined)
    "SRVS_VAL",     # Survivor's income
    "ED_VAL",       # Educational assistance
    "FIN_VAL",      # Financial assistance
    "WC_VAL",       # Worker's compensation
    "CSP_VAL",      # Child support received
    "PNSN_VAL",     # Pension income (combined)
    "ANN_VAL",      # Annuity income
    "DBTN_VAL",     # Retirement distributions
]

PERSON_TAX_VARS = [
    "FEDTAX_AC",    # Federal tax after credits
    "FEDTAX_BC",    # Federal tax before credits
    "STATETAX_A",   # State tax after credits
    "STATETAX_B",   # State tax before credits
    "FICA",         # FICA (Social Security + Medicare tax)
    "EIT_CRED",     # Earned Income Tax Credit
    "CTC_CRD",      # Child Tax Credit
    "ACTC_CRD",     # Additional Child Tax Credit
    "TAX_INC",      # Taxable income
    "MARG_TAX",     # Marginal tax rate
    "FILESTAT",     # Tax filer status
]

PERSON_SPM_VARS = [
    "SPM_ID",           # SPM unit ID
    "SPM_RESOURCES",    # Total SPM resources
    "SPM_POVTHRESHOLD", # SPM poverty threshold
    "SPM_POOR",         # SPM poverty status
    "SPM_TOTVAL",       # SPM cash income
    "SPM_EITC",         # SPM unit EITC
    "SPM_SNAPSUB",      # SNAP subsidy
    "SPM_SCHLUNCH",     # School lunch subsidy
    "SPM_WICVAL",       # WIC subsidy
    "SPM_ENGVAL",       # Energy subsidy
    "SPM_CAPHOUSESUB",  # Housing subsidy
    "SPM_FEDTAX",       # Federal tax (SPM unit)
    "SPM_STTAX",        # State tax (SPM unit)
    "SPM_FICA",         # FICA (SPM unit)
    "SPM_MEDXPNS",      # Medical expenses (SPM unit)
    "SPM_NUMPER",       # Number of persons in SPM unit
    "SPM_NUMADULTS",    # Number of adults
    "SPM_NUMKIDS",      # Number of children
    "SPM_WEIGHT",       # SPM weight
]

PERSON_DEMO_VARS = [
    "A_AGE",        # Age
    "A_SEX",        # Sex
    "A_HGA",        # Education attainment
    "A_MARITL",     # Marital status
    "PRDTRACE",     # Race
    "PEHSPNON",     # Hispanic origin
    "PRCITSHP",     # Citizenship
    "GESTFIPS",     # State FIPS code
    "GEREG",        # Census region
    "GEDIV",        # Census division
]

PERSON_IDS_WEIGHTS = [
    "PH_SEQ",       # Household sequence number
    "P_SEQ",        # Person sequence in household
    "A_LINENO",     # Line number
    "A_FAMNUM",     # Family number
    "MARSUPWT",     # Person March supplement weight (key weight)
    "A_FNLWGT",     # Basic CPS weight
    "RECORD_TYPE",  # Record type (person/household/family)
]

HOUSEHOLD_VARS = [
    "H_SEQ",        # Household sequence number
    "HTOTVAL",      # Household total income
    "HPCTCUT",      # Household income percentile
    "HHINC",        # Household income recode
    "HSUP_WGT",     # Household supplement weight
    "H_NUMPER",     # Number of persons in HH
    "H_TENURE",     # Tenure (own/rent)
    "HFOODSP",      # Food stamp recipient Y/N
    "HFDVAL",       # Food stamp amount
    "HFOODMO",      # Food stamp months
    "HLORENT",      # Reduced rent Y/N
    "HPUBLIC",      # Public housing Y/N
    "HPROP_VAL",    # Property value
    "HPRES_MORT",   # Presence of mortgage
    "HEARNVAL",     # Household earnings
    "HWSVAL",       # Household wage/salary
    "HSEVAL",       # Household self-employment
    "HSSVAL",       # Household Social Security
    "HSSIVAL",      # Household SSI
    "HPAWVAL",      # Household public assistance
    "HUCVAL",       # Household unemployment comp
    "HDIVVAL",      # Household dividends
    "HINTVAL",      # Household interest
    "HVETVAL",      # Household veterans payments
    "HOTHVAL",      # Household other income
    "GESTFIPS",     # State FIPS
    "HMCAID",       # Medicaid in household
    "HCOV",         # Health insurance coverage
]

# Transfer variables that are means-tested (bottom-50% propensity: HIGH)
MEANS_TESTED_TRANSFERS = [
    "SSI_VAL", "PAW_VAL", "FIN_VAL",
]

# Social insurance (broader, not means-tested but still progressive)
SOCIAL_INSURANCE = [
    "SS_VAL", "UC_VAL", "VET_VAL", "DSAB_VAL", "WC_VAL",
]

# Capital income (top-heavy)
CAPITAL_INCOME = [
    "DIV_VAL", "INT_VAL", "RNT_VAL", "CAP_VAL",
]


# ============================================================================
# API FUNCTIONS
# ============================================================================

def fetch_cps_batch(variables, record_type=None, max_retries=3):
    """
    Fetch a batch of variables from the Census CPS ASEC API.
    
    The API returns JSON: first row is headers, subsequent rows are data.
    No API key required for CPS ASEC (public data), but rate-limited.
    """
    # Always include identifiers for merging
    id_vars = ["PH_SEQ", "P_SEQ"]
    all_vars = list(set(id_vars + variables))
    
    var_str = ",".join(all_vars)
    url = f"{BASE_URL}?get={var_str}"
    
    for attempt in range(max_retries):
        try:
            logger.info(f"  API call: {len(all_vars)} variables (attempt {attempt+1})")
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            
            data = resp.json()
            headers = data[0]
            rows = data[1:]
            
            df = pd.DataFrame(rows, columns=headers)
            logger.info(f"  → {len(df):,} records received")
            return df
            
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 400:
                logger.error(f"  Bad request — likely invalid variable. URL: {url[:200]}...")
                # Try to identify bad variables by halving
                if len(variables) > 2:
                    logger.info("  Retrying with first half of variables...")
                    mid = len(variables) // 2
                    df1 = fetch_cps_batch(variables[:mid], record_type, max_retries)
                    df2 = fetch_cps_batch(variables[mid:], record_type, max_retries)
                    if df1 is not None and df2 is not None:
                        return pd.merge(df1, df2, on=["PH_SEQ", "P_SEQ"], how="outer")
                return None
            logger.warning(f"  HTTP {resp.status_code}: {e}")
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            logger.warning(f"  Error: {e}")
            time.sleep(5 * (attempt + 1))
    
    logger.error(f"  Failed after {max_retries} attempts")
    return None


def fetch_household_batch(variables, max_retries=3):
    """Fetch household-level variables (different record structure)."""
    id_vars = ["H_SEQ"]
    all_vars = list(set(id_vars + variables))
    var_str = ",".join(all_vars)
    url = f"{BASE_URL}?get={var_str}"
    
    for attempt in range(max_retries):
        try:
            logger.info(f"  HH API call: {len(all_vars)} variables (attempt {attempt+1})")
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            
            data = resp.json()
            headers = data[0]
            rows = data[1:]
            
            df = pd.DataFrame(rows, columns=headers)
            logger.info(f"  → {len(df):,} HH records received")
            return df
            
        except Exception as e:
            logger.warning(f"  Error: {e}")
            time.sleep(5 * (attempt + 1))
    
    return None


# ============================================================================
# DATA PROCESSING
# ============================================================================

def clean_numeric(df, exclude_cols=None):
    """Convert string columns to numeric, handling Census coding conventions."""
    exclude = set(exclude_cols or [])
    exclude.update(["PH_SEQ", "P_SEQ", "H_SEQ", "RECORD_TYPE", "SPM_ID",
                     "SPM_HEAD", "SPM_POOR", "SPM_FAMTYPE", "SPM_TENMORTSTATUS",
                     "SPM_HRACE", "SPM_HHISP", "SPM_HMARITALSTATUS",
                     "SPM_WCOHABIT", "SPM_WFOSTER22", "SPM_WNEWHEAD", 
                     "SPM_WNEWPARENT", "SPM_WUI_LT15"])
    
    for col in df.columns:
        if col in exclude:
            continue
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def compute_income_components(df):
    """
    Compute income aggregates following CBO/Piketty-Saez-Zucman conventions.
    
    Market income = earnings + capital income (dividends, interest, rent, cap gains)
    Pre-tax income = market income + social insurance (SS, UI, WC, veterans, disability)
    Post-tax income = pre-tax income + means-tested transfers - federal taxes - FICA
    """
    # Market income (pre-government)
    df['market_income'] = (
        df.get('PEARNVAL', 0).fillna(0) +
        df.get('DIV_VAL', 0).fillna(0) +
        df.get('INT_VAL', 0).fillna(0) +
        df.get('RNT_VAL', 0).fillna(0) +
        df.get('CAP_VAL', 0).fillna(0) +
        df.get('PNSN_VAL', 0).fillna(0) +
        df.get('ANN_VAL', 0).fillna(0) +
        df.get('DBTN_VAL', 0).fillna(0)
    )
    
    # Social insurance transfers (not means-tested)
    df['social_insurance'] = (
        df.get('SS_VAL', 0).fillna(0) +
        df.get('UC_VAL', 0).fillna(0) +
        df.get('VET_VAL', 0).fillna(0) +
        df.get('DSAB_VAL', 0).fillna(0) +
        df.get('WC_VAL', 0).fillna(0) +
        df.get('SRVS_VAL', 0).fillna(0)
    )
    
    # Means-tested transfers (HIGH propensity for bottom 50%)
    df['means_tested'] = (
        df.get('SSI_VAL', 0).fillna(0) +
        df.get('PAW_VAL', 0).fillna(0) +
        df.get('FIN_VAL', 0).fillna(0) +
        df.get('ED_VAL', 0).fillna(0) +
        df.get('CSP_VAL', 0).fillna(0)
    )
    
    # Capital income (top-heavy)
    df['capital_income'] = (
        df.get('DIV_VAL', 0).fillna(0) +
        df.get('INT_VAL', 0).fillna(0) +
        df.get('RNT_VAL', 0).fillna(0) +
        df.get('CAP_VAL', 0).fillna(0)
    )
    
    # Pre-tax national income (PSZ definition)
    df['pretax_income'] = df['market_income'] + df['social_insurance']
    
    # Federal taxes (estimated by Census tax model)
    df['federal_taxes'] = (
        df.get('FEDTAX_AC', 0).fillna(0) +
        df.get('FICA', 0).fillna(0)
    )
    
    # Tax credits received
    df['tax_credits'] = (
        df.get('EIT_CRED', 0).fillna(0) +
        df.get('CTC_CRD', 0).fillna(0) +
        df.get('ACTC_CRD', 0).fillna(0)
    )
    
    # Post-tax-and-transfer income
    df['posttax_income'] = (
        df['pretax_income'] +
        df['means_tested'] -
        df.get('FEDTAX_AC', 0).fillna(0) -
        df.get('FICA', 0).fillna(0) -
        df.get('STATETAX_A', 0).fillna(0)
    )
    
    # Total income (Census definition — should match PTOTVAL)
    df['total_income'] = df.get('PTOTVAL', 0).fillna(0)
    
    return df


def compute_quintile_stats(df, income_col='pretax_income', weight_col='MARSUPWT'):
    """
    Compute distributional statistics by income quintile.
    
    Following CBO methodology (Perese 2017):
    - Weight by MARSUPWT
    - Compute quintile boundaries on weighted distribution
    - Report mean income, transfer receipt, tax burden by quintile
    """
    valid = df[df[weight_col] > 0].copy()
    valid = valid.sort_values(income_col)
    
    # Compute weighted cumulative share
    valid['cum_weight'] = valid[weight_col].cumsum()
    total_weight = valid[weight_col].sum()
    valid['cum_pct'] = valid['cum_weight'] / total_weight
    
    # Assign quintiles
    valid['quintile'] = pd.cut(
        valid['cum_pct'],
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=['Q1 (Bottom 20%)', 'Q2', 'Q3', 'Q4', 'Q5 (Top 20%)'],
        include_lowest=True
    )
    
    # Also create bottom 50% flag
    valid['bottom_50'] = valid['cum_pct'] <= 0.50
    
    # Top 10%, top 1%
    valid['top_10'] = valid['cum_pct'] > 0.90
    valid['top_1'] = valid['cum_pct'] > 0.99
    
    # Weighted statistics by quintile
    results = []
    for q in valid['quintile'].cat.categories:
        qdf = valid[valid['quintile'] == q]
        w = qdf[weight_col]
        n_persons = w.sum()
        
        row = {
            'quintile': q,
            'n_records': len(qdf),
            'weighted_persons': n_persons,
        }
        
        # Weighted means for key variables
        for col in ['market_income', 'social_insurance', 'means_tested',
                     'capital_income', 'pretax_income', 'federal_taxes',
                     'tax_credits', 'posttax_income', 'total_income']:
            if col in qdf.columns:
                row[f'mean_{col}'] = np.average(qdf[col], weights=w)
        
        # Transfer receipt rates (weighted)
        for col in ['SS_VAL', 'SSI_VAL', 'PAW_VAL', 'UC_VAL', 'VET_VAL']:
            if col in qdf.columns:
                receipt = (qdf[col] > 0).astype(float)
                row[f'pct_receiving_{col}'] = np.average(receipt, weights=w) * 100
        
        # Effective federal tax rate
        if 'mean_federal_taxes' in row and 'mean_pretax_income' in row:
            if row['mean_pretax_income'] > 0:
                row['effective_fed_tax_rate'] = row['mean_federal_taxes'] / row['mean_pretax_income'] * 100
            else:
                row['effective_fed_tax_rate'] = 0
        
        # EITC amount (mean)
        if 'EIT_CRED' in qdf.columns:
            row['mean_eitc'] = np.average(qdf['EIT_CRED'].fillna(0), weights=w)
        
        results.append(row)
    
    # Bottom 50% summary
    b50 = valid[valid['bottom_50']]
    w50 = b50[weight_col]
    bottom_50_row = {
        'quintile': 'Bottom 50%',
        'n_records': len(b50),
        'weighted_persons': w50.sum(),
    }
    for col in ['market_income', 'social_insurance', 'means_tested',
                 'capital_income', 'pretax_income', 'federal_taxes',
                 'tax_credits', 'posttax_income', 'total_income']:
        if col in b50.columns:
            bottom_50_row[f'mean_{col}'] = np.average(b50[col], weights=w50)
    
    for col in ['SS_VAL', 'SSI_VAL', 'PAW_VAL', 'UC_VAL', 'VET_VAL']:
        if col in b50.columns:
            receipt = (b50[col] > 0).astype(float)
            bottom_50_row[f'pct_receiving_{col}'] = np.average(receipt, weights=w50) * 100
    
    if bottom_50_row.get('mean_pretax_income', 0) > 0:
        bottom_50_row['effective_fed_tax_rate'] = (
            bottom_50_row.get('mean_federal_taxes', 0) / 
            bottom_50_row['mean_pretax_income'] * 100
        )
    
    results.append(bottom_50_row)
    
    # Top 10% summary
    t10 = valid[valid['top_10']]
    w10 = t10[weight_col]
    top_10_row = {
        'quintile': 'Top 10%',
        'n_records': len(t10),
        'weighted_persons': w10.sum(),
    }
    for col in ['market_income', 'social_insurance', 'means_tested',
                 'capital_income', 'pretax_income', 'federal_taxes',
                 'tax_credits', 'posttax_income', 'total_income']:
        if col in t10.columns:
            top_10_row[f'mean_{col}'] = np.average(t10[col], weights=w10)
    
    if top_10_row.get('mean_pretax_income', 0) > 0:
        top_10_row['effective_fed_tax_rate'] = (
            top_10_row.get('mean_federal_taxes', 0) /
            top_10_row['mean_pretax_income'] * 100
        )
    
    results.append(top_10_row)
    
    return pd.DataFrame(results), valid


def compute_income_shares(df, weight_col='MARSUPWT'):
    """
    Compute income shares by group (Piketty-Saez-Zucman framework).
    
    Returns: dict of income shares for bottom 50%, middle 40%, top 10%, top 1%
    """
    valid = df[df[weight_col] > 0].copy()
    
    shares = {}
    for income_type in ['pretax_income', 'posttax_income', 'market_income', 'capital_income']:
        if income_type not in valid.columns:
            continue
            
        valid_sorted = valid.sort_values(income_type)
        valid_sorted['cum_weight'] = valid_sorted[weight_col].cumsum()
        total_weight = valid_sorted[weight_col].sum()
        valid_sorted['cum_pct'] = valid_sorted['cum_weight'] / total_weight
        
        total = np.sum(valid_sorted[income_type] * valid_sorted[weight_col])
        
        if total <= 0:
            continue
        
        # Bottom 50%
        b50 = valid_sorted[valid_sorted['cum_pct'] <= 0.50]
        b50_total = np.sum(b50[income_type] * b50[weight_col])
        
        # Middle 40% (50th-90th percentile)
        m40 = valid_sorted[(valid_sorted['cum_pct'] > 0.50) & (valid_sorted['cum_pct'] <= 0.90)]
        m40_total = np.sum(m40[income_type] * m40[weight_col])
        
        # Top 10%
        t10 = valid_sorted[valid_sorted['cum_pct'] > 0.90]
        t10_total = np.sum(t10[income_type] * t10[weight_col])
        
        # Top 1%
        t1 = valid_sorted[valid_sorted['cum_pct'] > 0.99]
        t1_total = np.sum(t1[income_type] * t1[weight_col])
        
        shares[income_type] = {
            'bottom_50_share': b50_total / total * 100,
            'middle_40_share': m40_total / total * 100,
            'top_10_share': t10_total / total * 100,
            'top_1_share': t1_total / total * 100,
            'total': total,
        }
    
    return shares


def compute_state_level_stats(df, weight_col='MARSUPWT'):
    """
    Compute state-level distributional statistics for SDID analysis.
    
    Following Autor, Dorn & Hanson (2013) methodology of using
    geographic variation for identification.
    """
    if 'GESTFIPS' not in df.columns:
        logger.warning("No state FIPS available — skipping state-level analysis")
        return None
    
    valid = df[(df[weight_col] > 0) & (df['GESTFIPS'].notna())].copy()
    valid['state_fips'] = valid['GESTFIPS'].astype(int)
    
    state_stats = []
    for fips in sorted(valid['state_fips'].unique()):
        state_df = valid[valid['state_fips'] == fips]
        w = state_df[weight_col]
        
        if len(state_df) < 50:  # Skip tiny samples
            continue
        
        row = {
            'state_fips': fips,
            'n_records': len(state_df),
            'weighted_pop': w.sum(),
        }
        
        for col in ['pretax_income', 'posttax_income', 'market_income',
                     'means_tested', 'social_insurance', 'capital_income',
                     'federal_taxes', 'tax_credits']:
            if col in state_df.columns:
                row[f'mean_{col}'] = np.average(state_df[col], weights=w)
                row[f'median_{col}'] = state_df[col].median()
        
        # Gini coefficient (weighted)
        if 'pretax_income' in state_df.columns:
            inc = state_df['pretax_income'].values
            wts = w.values
            sorted_idx = np.argsort(inc)
            inc_sorted = inc[sorted_idx]
            wts_sorted = wts[sorted_idx]
            cum_wts = np.cumsum(wts_sorted)
            cum_inc = np.cumsum(inc_sorted * wts_sorted)
            total_w = cum_wts[-1]
            total_inc = cum_inc[-1]
            if total_inc > 0 and total_w > 0:
                row['gini'] = 1 - 2 * np.sum(
                    cum_inc / total_inc * wts_sorted / total_w
                )
        
        # Transfer dependency rate (% receiving means-tested)
        for col in ['SSI_VAL', 'PAW_VAL']:
            if col in state_df.columns:
                receipt = (state_df[col] > 0).astype(float)
                row[f'pct_receiving_{col}'] = np.average(receipt, weights=w) * 100
        
        # SNAP receipt (household level flag)
        if 'HFOODSP' in state_df.columns:
            snap = (state_df['HFOODSP'] == 1).astype(float)
            row['pct_snap'] = np.average(snap, weights=w) * 100
        
        # Bottom 50% mean income
        state_sorted = state_df.sort_values('pretax_income')
        state_sorted['cum_w'] = state_sorted[weight_col].cumsum()
        total_w = state_sorted[weight_col].sum()
        state_sorted['cum_pct'] = state_sorted['cum_w'] / total_w
        b50 = state_sorted[state_sorted['cum_pct'] <= 0.50]
        if len(b50) > 0:
            row['bottom_50_mean_income'] = np.average(
                b50['pretax_income'], weights=b50[weight_col]
            )
        
        state_stats.append(row)
    
    return pd.DataFrame(state_stats)


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    logger.info("=" * 70)
    logger.info("CPS ASEC 2024 MICRODATA ACQUISITION")
    logger.info("=" * 70)
    logger.info("Source: Census Bureau API")
    logger.info("Survey: Current Population Survey, Annual Social & Economic Supplement")
    logger.info("Year: 2024 (income reference year: 2023)")
    logger.info("")
    
    TABLES = get_output_path("tables")
    EXTERNAL = PROJECT_ROOT / "data" / "external"
    os.makedirs(TABLES, exist_ok=True)
    os.makedirs(EXTERNAL, exist_ok=True)
    
    # ------------------------------------------------------------------
    # STEP 1: Download person-level data in batches
    # ------------------------------------------------------------------
    logger.info("STEP 1: Downloading person-level data from Census API...")
    
    batches = {
        'ids_weights': PERSON_IDS_WEIGHTS,
        'income': PERSON_INCOME_VARS,
        'transfers': PERSON_TRANSFER_VARS,
        'taxes': PERSON_TAX_VARS,
        'spm': PERSON_SPM_VARS,
        'demographics': PERSON_DEMO_VARS,
    }
    
    dfs = {}
    for name, var_list in batches.items():
        logger.info(f"\n  Batch: {name} ({len(var_list)} variables)")
        df = fetch_cps_batch(var_list)
        if df is not None:
            dfs[name] = df
            logger.info(f"  ✓ {name}: {len(df):,} records, {len(df.columns)} columns")
        else:
            logger.error(f"  ✗ Failed to fetch {name}")
        time.sleep(2)  # Rate limiting
    
    if len(dfs) < 3:
        logger.error("Too many batch failures — aborting")
        return
    
    # Merge all batches on PH_SEQ + P_SEQ
    logger.info("\n  Merging batches...")
    person_df = dfs['ids_weights']
    for name, df in dfs.items():
        if name == 'ids_weights':
            continue
        # Drop duplicate merge keys
        merge_cols = [c for c in df.columns if c not in person_df.columns or c in ['PH_SEQ', 'P_SEQ']]
        person_df = pd.merge(
            person_df, 
            df[merge_cols],
            on=['PH_SEQ', 'P_SEQ'], 
            how='left'
        )
    
    logger.info(f"  Merged person data: {len(person_df):,} records × {len(person_df.columns)} columns")
    
    # Clean numeric values
    person_df = clean_numeric(person_df)
    
    # Filter to person records (adults 15+ with positive weight)
    if 'RECORD_TYPE' in person_df.columns:
        person_df = person_df[person_df['RECORD_TYPE'] == 'PER']  # Person records
    
    # Keep persons 15+ with positive supplement weight
    person_df = person_df[
        (person_df['A_AGE'] >= 15) & 
        (person_df['MARSUPWT'] > 0)
    ].copy()
    
    logger.info(f"  After filtering (age 15+, weight > 0): {len(person_df):,} persons")
    
    # ------------------------------------------------------------------
    # STEP 2: Compute derived income components
    # ------------------------------------------------------------------
    logger.info("\nSTEP 2: Computing income components (CBO/PSZ framework)...")
    person_df = compute_income_components(person_df)
    
    # Quick validation
    avg_income = np.average(person_df['pretax_income'], weights=person_df['MARSUPWT'])
    avg_earnings = np.average(person_df['PEARNVAL'].fillna(0), weights=person_df['MARSUPWT'])
    logger.info(f"  Weighted mean pre-tax income: ${avg_income:,.0f}")
    logger.info(f"  Weighted mean earnings: ${avg_earnings:,.0f}")
    
    # ------------------------------------------------------------------
    # STEP 3: Distributional analysis by quintile
    # ------------------------------------------------------------------
    logger.info("\nSTEP 3: Computing distributional statistics by quintile...")
    quintile_df, enriched_df = compute_quintile_stats(person_df)
    
    logger.info("\n  === INCOME DISTRIBUTION (CPS ASEC 2024, Income Year 2023) ===")
    logger.info(f"{'Quintile':<20} {'Mean Pre-Tax':>14} {'Mean Post-Tax':>14} {'Eff. Tax Rate':>14}")
    logger.info("-" * 66)
    for _, row in quintile_df.iterrows():
        q = row['quintile']
        pre = row.get('mean_pretax_income', 0)
        post = row.get('mean_posttax_income', 0)
        etr = row.get('effective_fed_tax_rate', 0)
        logger.info(f"  {q:<20} ${pre:>12,.0f}  ${post:>12,.0f}  {etr:>12.1f}%")
    
    # ------------------------------------------------------------------
    # STEP 4: Income shares (PSZ framework)
    # ------------------------------------------------------------------
    logger.info("\nSTEP 4: Computing income shares (Piketty-Saez-Zucman framework)...")
    shares = compute_income_shares(person_df)
    
    for inc_type, share_dict in shares.items():
        logger.info(f"\n  {inc_type.upper()} shares:")
        logger.info(f"    Bottom 50%: {share_dict['bottom_50_share']:.1f}%")
        logger.info(f"    Middle 40%: {share_dict['middle_40_share']:.1f}%")
        logger.info(f"    Top 10%:    {share_dict['top_10_share']:.1f}%")
        logger.info(f"    Top 1%:     {share_dict['top_1_share']:.1f}%")
    
    # ------------------------------------------------------------------
    # STEP 5: Transfer receipt by quintile
    # ------------------------------------------------------------------
    logger.info("\nSTEP 5: Transfer receipt rates (% of persons receiving)...")
    logger.info(f"{'Quintile':<20} {'SS':>8} {'SSI':>8} {'Welfare':>8} {'UI':>8} {'Means-Tested $':>15}")
    logger.info("-" * 75)
    for _, row in quintile_df.iterrows():
        q = row['quintile']
        ss = row.get('pct_receiving_SS_VAL', 0)
        ssi = row.get('pct_receiving_SSI_VAL', 0)
        paw = row.get('pct_receiving_PAW_VAL', 0)
        uc = row.get('pct_receiving_UC_VAL', 0)
        mt = row.get('mean_means_tested', 0)
        logger.info(f"  {q:<20} {ss:>7.1f}% {ssi:>7.1f}% {paw:>7.1f}% {uc:>7.1f}% ${mt:>13,.0f}")
    
    # ------------------------------------------------------------------
    # STEP 6: State-level analysis for SDID
    # ------------------------------------------------------------------
    logger.info("\nSTEP 6: Computing state-level statistics for SDID analysis...")
    state_df = compute_state_level_stats(person_df)
    
    if state_df is not None:
        logger.info(f"  States with data: {len(state_df)}")
        logger.info(f"  Top 5 by bottom-50% mean income:")
        top_states = state_df.nlargest(5, 'bottom_50_mean_income')
        for _, row in top_states.iterrows():
            logger.info(f"    FIPS {int(row['state_fips']):02d}: ${row['bottom_50_mean_income']:,.0f}")
        
        logger.info(f"  Bottom 5 by bottom-50% mean income:")
        bot_states = state_df.nsmallest(5, 'bottom_50_mean_income')
        for _, row in bot_states.iterrows():
            logger.info(f"    FIPS {int(row['state_fips']):02d}: ${row['bottom_50_mean_income']:,.0f}")
    
    # ------------------------------------------------------------------
    # STEP 7: Save results
    # ------------------------------------------------------------------
    logger.info("\nSTEP 7: Saving results...")
    
    # Save quintile statistics
    quintile_path = TABLES / "cps_asec_quintile_stats.json"
    quintile_dict = quintile_df.to_dict(orient='records')
    with open(quintile_path, 'w') as f:
        json.dump(quintile_dict, f, indent=2, default=str)
    logger.info(f"  ✓ Quintile stats → {quintile_path}")
    
    # Save income shares
    shares_path = TABLES / "cps_asec_income_shares.json"
    with open(shares_path, 'w') as f:
        json.dump(shares, f, indent=2, default=str)
    logger.info(f"  ✓ Income shares → {shares_path}")
    
    # Save state-level data
    if state_df is not None:
        state_path = TABLES / "cps_asec_state_stats.csv"
        state_df.to_csv(state_path, index=False)
        logger.info(f"  ✓ State stats → {state_path}")
    
    # Save full person-level microdata (CSV, for later QTE analysis)
    micro_cols = ['PH_SEQ', 'P_SEQ', 'MARSUPWT', 'GESTFIPS', 'A_AGE', 'A_SEX',
                  'A_HGA', 'PRDTRACE', 'PEHSPNON',
                  'market_income', 'social_insurance', 'means_tested',
                  'capital_income', 'pretax_income', 'federal_taxes',
                  'tax_credits', 'posttax_income', 'total_income',
                  'PEARNVAL', 'WSAL_VAL', 'DIV_VAL', 'INT_VAL', 'CAP_VAL',
                  'SS_VAL', 'SSI_VAL', 'PAW_VAL', 'UC_VAL', 'VET_VAL',
                  'EIT_CRED', 'CTC_CRD', 'FEDTAX_AC', 'FICA',
                  'SPM_RESOURCES', 'SPM_POVTHRESHOLD', 'SPM_POOR',
                  'SPM_SNAPSUB', 'SPM_WICVAL', 'SPM_SCHLUNCH']
    
    available_cols = [c for c in micro_cols if c in person_df.columns]
    micro_path = EXTERNAL / "cps_asec_2024_microdata.csv"
    person_df[available_cols].to_csv(micro_path, index=False)
    logger.info(f"  ✓ Microdata ({len(available_cols)} cols) → {micro_path}")
    
    # Save to database
    logger.info("\n  Saving summary series to database...")
    session = get_session()
    
    # Store quintile-level series
    for _, row in quintile_df.iterrows():
        q_label = str(row['quintile']).replace(' ', '_').replace('(', '').replace(')', '').replace('%', 'pct')
        for metric in ['mean_pretax_income', 'mean_posttax_income', 'mean_market_income',
                        'mean_means_tested', 'effective_fed_tax_rate']:
            if metric not in row or pd.isna(row[metric]):
                continue
            series_id = f"CPS_ASEC_{q_label}_{metric}".upper()
            
            # Upsert series
            existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
            if not existing:
                series = EconomicSeries(
                    series_id=series_id,
                    source="CPS_ASEC",
                    title=f"CPS ASEC 2024 - {row['quintile']} - {metric}",
                    units="Dollars" if 'income' in metric or 'tested' in metric else "Percent",
                    frequency="Annual",
                )
                session.add(series)
            
            # Store observation
            from datetime import date as dt_date
            obs = Observation(
                series_id=series_id,
                date=dt_date(2023, 12, 31),  # Income reference year
                value=float(row[metric]),
            )
            session.merge(obs)
    
    session.commit()
    logger.info("  ✓ Database updated")
    
    # ------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 70)
    logger.info("CPS ASEC 2024 ACQUISITION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"  Total persons (15+): {len(person_df):,}")
    logger.info(f"  Weighted population: {person_df['MARSUPWT'].sum():,.0f}")
    logger.info(f"  States covered: {person_df['GESTFIPS'].nunique() if 'GESTFIPS' in person_df.columns else 'N/A'}")
    logger.info(f"  Columns: {len(person_df.columns)}")
    logger.info("")
    logger.info("  Files saved:")
    logger.info(f"    {quintile_path}")
    logger.info(f"    {shares_path}")
    if state_df is not None:
        logger.info(f"    {state_path}")
    logger.info(f"    {micro_path}")
    logger.info("")
    logger.info("  KEY FINDING for paper:")
    
    # Print bottom-50% vs top-10% comparison
    b50 = quintile_df[quintile_df['quintile'] == 'Bottom 50%'].iloc[0] if 'Bottom 50%' in quintile_df['quintile'].values else None
    t10 = quintile_df[quintile_df['quintile'] == 'Top 10%'].iloc[0] if 'Top 10%' in quintile_df['quintile'].values else None
    
    if b50 is not None and t10 is not None:
        logger.info(f"    Bottom 50% mean pre-tax income: ${b50.get('mean_pretax_income', 0):,.0f}")
        logger.info(f"    Top 10% mean pre-tax income:    ${t10.get('mean_pretax_income', 0):,.0f}")
        ratio = t10.get('mean_pretax_income', 1) / max(b50.get('mean_pretax_income', 1), 1)
        logger.info(f"    Ratio (top 10% / bottom 50%):   {ratio:.1f}x")
    
    if 'pretax_income' in shares:
        ps = shares['pretax_income']
        logger.info(f"    Bottom 50% income share: {ps['bottom_50_share']:.1f}%")
        logger.info(f"    Top 10% income share:    {ps['top_10_share']:.1f}%")
        logger.info(f"    Top 1% income share:     {ps['top_1_share']:.1f}%")
    
    return person_df, quintile_df, shares, state_df


if __name__ == "__main__":
    results = main()
