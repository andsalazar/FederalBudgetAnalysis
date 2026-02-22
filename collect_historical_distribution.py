"""
=============================================================================
COLLECT HISTORICAL INCOME DISTRIBUTION & DISTRIBUTIONAL DATA (2000–2024)
=============================================================================

Three data sources:
  1. Census Historical Income Tables (H-1, H-3) — quintile income shares,
     median HH income, Gini coefficients, 1967–present
  2. CPS ASEC API — quintile distributional summaries for benchmark years
     (income shares, transfer dependency, tax burden for B50)
  3. CBO Budget Series — extended FY2000–2025 trend data (already in DB,
     but we compute derived series for the 25-year analysis)

All dollar amounts converted to real 2024 dollars using CPI deflator.

Output:
  - data/processed/census_income_quintiles.csv
  - data/processed/cps_asec_historical_quintiles.csv
  - data/processed/cbo_25year_trends.csv
  - Updates to SQLite database
=============================================================================
"""

import sys, os, json, time, warnings, csv, io
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import requests
from datetime import date, datetime
from pathlib import Path
from loguru import logger

from src.utils.config import load_config, get_output_path, PROJECT_ROOT
from src.database.models import get_session, EconomicSeries, Observation

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | {message}", level="INFO")

PROCESSED = PROJECT_ROOT / "data" / "processed"
TABLES = get_output_path("tables")
PROCESSED.mkdir(parents=True, exist_ok=True)

session = get_session()

# Load deflators
with open(TABLES / "cpi_deflators.json") as f:
    DEFLATORS = json.load(f)
FY_DEFLATOR = {int(k): v for k, v in DEFLATORS['fiscal_year'].items()}
CY_DEFLATOR = {int(k): v for k, v in DEFLATORS['calendar_year'].items()}

def real_cy(nominal, cy):
    return nominal * CY_DEFLATOR.get(cy, 1.0)

def real_fy(nominal, fy):
    return nominal * FY_DEFLATOR.get(fy, 1.0)


# ============================================================================
# SECTION 1: CENSUS HISTORICAL INCOME TABLES
# ============================================================================

def collect_census_income_distribution():
    """
    Download Census Historical Income Tables for household income distribution.
    
    Census publishes these as Excel files. We parse them to get:
    - Quintile income upper limits (H-1)
    - Quintile shares of aggregate income (H-2)  
    - Mean income by quintile (H-3)
    - Gini index (H-4)
    
    Source: https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html
    
    Since these Excel files have complex headers, we use FRED for the key
    distributional series which are cleaner:
    - MEHOINUSA672N: Real Median Household Income
    - GINIALLRF: Gini Index for Households
    - PINC*: Income percentile data
    
    For quintile shares, we use Census Table H-2 data which is well-documented.
    """
    logger.info("=" * 70)
    logger.info("SECTION 1: CENSUS HISTORICAL INCOME DISTRIBUTION")
    logger.info("=" * 70)
    
    # --- 1a. FRED series for key distributional metrics ---
    from fredapi import Fred
    fred = Fred(api_key='43272fac437c873feb1ace8519a979fc')
    
    fred_dist_series = {
        # Household income distribution
        'MEHOINUSA672N': 'Real Median Household Income (2023 CPI-U-RS dollars)',
        'MEPAINUSA672N': 'Real Median Personal Income',
        'GINIALLRF':     'Gini Index for Households',
        
        # Income shares — FRED has World Inequality Database shares
        'WFRBST01134':   'Share of Total Net Worth: Top 1%',
        'WFRBSN40188':   'Share of Total Net Worth: Bottom 50%',
        'WFRBLB50107':   'Share of Total Net Worth: 50th-90th Percentile',
        
        # Poverty
        'PPAAUS00000A156NCEN': 'Poverty Rate: All Ages',
        
        # Transfer dependency
        'W823RC1Q027SBEA': 'Federal Social Benefits (quarterly)',
        'B087RC1Q027SBEA': 'Government Social Benefits to Persons',
        
        # Income percentile thresholds (from CBO/Census)
        'LES1252881600Q': 'Employed full-time: median weekly earnings',
    }
    
    collected = {}
    for sid, label in fred_dist_series.items():
        try:
            data = fred.get_series(sid, observation_start='1999-01-01')
            if data is not None and len(data) > 0:
                data = data.dropna()
                
                # Store in database
                existing = session.query(EconomicSeries).filter_by(series_id=sid).first()
                if not existing:
                    try:
                        info = fred.get_series_info(sid)
                        units = info.get('units', 'Index')
                    except:
                        units = 'Index'
                    session.add(EconomicSeries(
                        series_id=sid, source='FRED',
                        title=label, units=units,
                        frequency='Annual' if len(data) < 30 else 'Quarterly',
                        last_updated=datetime.utcnow()
                    ))
                
                new_obs = 0
                for dt, val in data.items():
                    obs_date = dt.date()
                    existing_obs = session.query(Observation).filter_by(
                        series_id=sid, date=obs_date
                    ).first()
                    if not existing_obs:
                        session.add(Observation(
                            series_id=sid, date=obs_date, value=float(val)
                        ))
                        new_obs += 1
                    elif existing_obs.value != float(val):
                        existing_obs.value = float(val)
                        new_obs += 1
                
                collected[sid] = len(data)
                logger.info(f"  {sid}: {label} — {len(data)} obs ({new_obs} new)")
                time.sleep(0.5)
        except Exception as e:
            logger.warning(f"  {sid}: {e}")
    
    session.commit()
    
    # --- 1b. Construct quintile income shares from Census H-2 table ---
    # Census publishes these; we'll use the FRED World Inequality Database
    # series plus published Census data
    
    # Historical quintile shares (from Census H-2 table, manually compiled
    # from published data for key years — this is the standard reference)
    # Source: Census Bureau, Current Population Survey, Annual Social and 
    # Economic Supplement, Table H-2
    # Shares of Aggregate Household Income by Quintile
    
    quintile_shares = {
        # Year: (Lowest 20%, Second 20%, Third 20%, Fourth 20%, Highest 20%, Top 5%)
        2000: (3.6, 8.9, 14.8, 23.0, 49.8, 22.1),
        2001: (3.5, 8.7, 14.6, 23.0, 50.1, 22.4),
        2002: (3.5, 8.8, 14.8, 23.3, 49.7, 21.7),
        2003: (3.4, 8.7, 14.8, 23.4, 49.8, 21.4),
        2004: (3.4, 8.7, 14.7, 23.2, 50.1, 21.8),
        2005: (3.4, 8.6, 14.6, 23.0, 50.4, 22.2),
        2006: (3.4, 8.6, 14.5, 22.9, 50.5, 22.3),
        2007: (3.4, 8.7, 14.8, 23.4, 49.7, 21.2),
        2008: (3.4, 8.6, 14.7, 23.3, 50.0, 21.5),
        2009: (3.4, 8.6, 14.6, 23.2, 50.3, 21.7),
        2010: (3.3, 8.5, 14.6, 23.4, 50.3, 21.3),
        2011: (3.2, 8.4, 14.3, 23.0, 51.1, 22.3),
        2012: (3.2, 8.3, 14.4, 23.0, 51.0, 22.3),
        2013: (3.2, 8.4, 14.4, 23.0, 51.0, 22.2),
        2014: (3.1, 8.2, 14.3, 23.2, 51.2, 21.9),
        2015: (3.1, 8.2, 14.3, 23.2, 51.1, 22.1),
        2016: (3.1, 8.3, 14.2, 22.9, 51.5, 22.6),
        2017: (3.1, 8.2, 14.3, 23.0, 51.5, 22.3),
        2018: (3.1, 8.3, 14.1, 22.6, 52.0, 23.1),
        2019: (3.1, 8.3, 14.1, 22.7, 51.9, 23.0),
        2020: (3.0, 8.1, 14.0, 22.6, 52.2, 23.0),
        2021: (3.0, 8.1, 14.0, 22.7, 52.3, 23.5),
        2022: (3.0, 8.0, 14.0, 22.7, 52.3, 23.4),
        2023: (3.0, 8.0, 14.0, 22.6, 52.4, 23.5),
    }
    
    # Build DataFrame
    rows = []
    for year, shares in sorted(quintile_shares.items()):
        rows.append({
            'year': year,
            'q1_share': shares[0],  # Bottom 20%
            'q2_share': shares[1],  # Second 20%
            'q3_share': shares[2],  # Middle 20%
            'q4_share': shares[3],  # Fourth 20%
            'q5_share': shares[4],  # Top 20%
            'top5_share': shares[5],  # Top 5%
            'bottom50_share': shares[0] + shares[1] + shares[2] / 2,  # ~B50
            'top10_share': shares[4] - (shares[4] - shares[5]) * 0.5,  # rough T10
        })
    
    df_quintile = pd.DataFrame(rows)
    df_quintile.to_csv(PROCESSED / "census_income_quintiles.csv", index=False)
    logger.info(f"  Saved census_income_quintiles.csv ({len(df_quintile)} years)")
    
    # Store in database
    for _, row in df_quintile.iterrows():
        yr = int(row['year'])
        for col in ['q1_share', 'q2_share', 'q3_share', 'q4_share', 'q5_share', 
                     'top5_share', 'bottom50_share']:
            sid = f"CENSUS_HH_{col.upper()}"
            existing = session.query(EconomicSeries).filter_by(series_id=sid).first()
            if not existing:
                session.add(EconomicSeries(
                    series_id=sid, source='Census',
                    title=f"Household Income Share: {col}",
                    units='Percent', frequency='Annual',
                    last_updated=datetime.utcnow()
                ))
            obs_date = date(yr, 12, 31)
            existing_obs = session.query(Observation).filter_by(
                series_id=sid, date=obs_date
            ).first()
            if not existing_obs:
                session.add(Observation(series_id=sid, date=obs_date, value=float(row[col])))
            else:
                existing_obs.value = float(row[col])
    
    session.commit()
    logger.info("  Quintile shares stored in database")
    
    return collected, df_quintile


# ============================================================================
# SECTION 2: CPS ASEC BENCHMARK YEARS — Distributional Summaries
# ============================================================================

def collect_cps_asec_benchmarks():
    """
    Collect CPS ASEC distributional summaries for benchmark years.
    
    For each year, we fetch person-level income + transfer data and compute:
    - Quintile boundaries
    - Quintile mean incomes
    - Transfer dependency by quintile (transfers as % of total income)
    - Bottom 50% income share
    - Tax burden estimates by quintile
    
    Years: 2001–2024 (every 3 years + current)
    The CPS ASEC asks about income in the PRIOR calendar year.
    So 2024 ASEC → CY2023 income, 2020 ASEC → CY2019, etc.
    """
    logger.info("=" * 70)
    logger.info("SECTION 2: CPS ASEC BENCHMARK YEAR DISTRIBUTIONAL SUMMARIES")
    logger.info("=" * 70)
    
    # Key benchmark years (ASEC survey years → income reference year)
    # Survey year → income year: 2024→2023, 2021→2020, 2018→2017, 
    # 2015→2014, 2012→2011, 2009→2008, 2006→2005, 2003→2002, 2001→2000
    benchmark_years = [2003, 2006, 2009, 2012, 2015, 2018, 2021, 2024]
    
    # All years use /cps/asec/mar endpoint with for=state:* parameter
    
    all_results = []
    
    for survey_year in benchmark_years:
        income_year = survey_year - 1
        logger.info(f"\n  --- CPS ASEC {survey_year} (income year CY{income_year}) ---")
        
        try:
            result = _fetch_cps_universal(survey_year, income_year)
            
            if result:
                all_results.append(result)
                logger.info(f"    B50 income share: {result['bottom50_income_share']:.1f}%")
                logger.info(f"    B50 transfer dependency: {result['bottom50_transfer_pct']:.1f}%")
                logger.info(f"    Gini (computed): {result['gini_computed']:.4f}")
        except Exception as e:
            logger.warning(f"    Failed for {survey_year}: {e}")
        
        time.sleep(1)  # Rate limit
    
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv(PROCESSED / "cps_asec_historical_quintiles.csv", index=False)
        logger.info(f"\n  Saved cps_asec_historical_quintiles.csv ({len(df)} benchmark years)")
        
        # Store summary in database
        for _, row in df.iterrows():
            yr = int(row['income_year'])
            for metric in ['bottom50_income_share', 'bottom50_transfer_pct', 'gini_computed',
                          'q1_mean_income', 'q2_mean_income', 'q3_mean_income',
                          'q4_mean_income', 'q5_mean_income', 'median_income']:
                if metric in row and pd.notna(row[metric]):
                    sid = f"CPS_HIST_{metric.upper()}"
                    existing = session.query(EconomicSeries).filter_by(series_id=sid).first()
                    if not existing:
                        session.add(EconomicSeries(
                            series_id=sid, source='CPS_ASEC',
                            title=f"CPS ASEC Historical: {metric}",
                            units='Percent' if 'share' in metric or 'pct' in metric or 'gini' in metric else 'Dollars',
                            frequency='Benchmark',
                            last_updated=datetime.utcnow()
                        ))
                    obs_date = date(yr, 12, 31)
                    existing_obs = session.query(Observation).filter_by(
                        series_id=sid, date=obs_date
                    ).first()
                    val = float(row[metric])
                    if not existing_obs:
                        session.add(Observation(series_id=sid, date=obs_date, value=val))
                    else:
                        existing_obs.value = val
        
        session.commit()
        return df
    
    return pd.DataFrame()


def _fetch_cps_universal(survey_year, income_year):
    """Fetch CPS ASEC data for any year via /cps/asec/mar endpoint."""
    base_url = f"https://api.census.gov/data/{survey_year}/cps/asec/mar"
    
    # Core variables available across all years
    # Try full set first, then fall back to minimal
    full_vars = "PTOTVAL,PEARNVAL,SS_VAL,SSI_VAL,PAW_VAL,UC_VAL"
    min_vars = "PTOTVAL,PEARNVAL,SS_VAL,SSI_VAL"
    weight_var = "MARSUPWT"
    
    for var_set in [full_vars, min_vars]:
        url = f"{base_url}?get={var_set},{weight_var}&for=state:*"
        try:
            resp = requests.get(url, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 1:
                    break
        except Exception:
            continue
    else:
        # Last resort: just income + weight
        url = f"{base_url}?get=PTOTVAL,{weight_var}&for=state:*"
        resp = requests.get(url, timeout=60)
        if resp.status_code != 200:
            logger.warning(f"    HTTP {resp.status_code} for {survey_year}")
            return None
        data = resp.json()
        if len(data) <= 1:
            logger.warning(f"    No data for {survey_year}")
            return None
    
    headers = data[0]
    rows = data[1:]
    
    df = pd.DataFrame(rows, columns=headers)
    
    # Convert to numeric
    for col in df.columns:
        if col != 'state':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter valid records
    df = df[df[weight_var] > 0].copy()
    df = df[df['PTOTVAL'].notna()].copy()
    
    transfer_cols = [c for c in ['SS_VAL', 'SSI_VAL', 'PAW_VAL', 'UC_VAL'] if c in df.columns]
    
    logger.info(f"    Fetched {len(df)} records, columns: {list(df.columns)}")
    
    return _compute_distribution(df, 'PTOTVAL', weight_var, transfer_cols,
                                  survey_year, income_year)


def _compute_distribution(df, income_col, weight_col, transfer_cols, survey_year, income_year):
    """Compute weighted distributional statistics from CPS ASEC data."""
    
    weights = df[weight_col].values
    incomes = df[income_col].values
    
    # Weighted quantiles
    total_weight = weights.sum()
    sort_idx = np.argsort(incomes)
    sorted_inc = incomes[sort_idx]
    sorted_wt = weights[sort_idx]
    cum_wt = np.cumsum(sorted_wt) / total_weight
    
    # Quintile boundaries
    boundaries = {}
    for pct, label in [(0.20, 'p20'), (0.40, 'p40'), (0.50, 'p50'), 
                        (0.60, 'p60'), (0.80, 'p80'), (0.90, 'p90'), 
                        (0.95, 'p95'), (0.99, 'p99')]:
        idx = np.searchsorted(cum_wt, pct)
        if idx < len(sorted_inc):
            boundaries[label] = float(sorted_inc[idx])
    
    # Weighted mean by quintile
    q_means = {}
    total_income = (incomes * weights).sum()
    
    quintile_masks = {
        'q1': cum_wt <= 0.20,
        'q2': (cum_wt > 0.20) & (cum_wt <= 0.40),
        'q3': (cum_wt > 0.40) & (cum_wt <= 0.60),
        'q4': (cum_wt > 0.60) & (cum_wt <= 0.80),
        'q5': cum_wt > 0.80,
    }
    
    # Need to map back to original indices
    inv_sort = np.argsort(sort_idx)
    cum_wt_orig = cum_wt[inv_sort]
    
    quintile_shares = {}
    quintile_means = {}
    for q, (lo, hi) in [('q1', (0, 0.20)), ('q2', (0.20, 0.40)), 
                          ('q3', (0.40, 0.60)), ('q4', (0.60, 0.80)), ('q5', (0.80, 1.0))]:
        mask = (cum_wt_orig > lo) & (cum_wt_orig <= hi)
        if lo == 0:
            mask = cum_wt_orig <= hi
        q_inc = (incomes[mask] * weights[mask]).sum()
        q_wt = weights[mask].sum()
        quintile_shares[q] = (q_inc / total_income * 100) if total_income > 0 else 0
        quintile_means[q] = (q_inc / q_wt) if q_wt > 0 else 0
    
    # Bottom 50% share
    b50_mask = cum_wt_orig <= 0.50
    b50_income = (incomes[b50_mask] * weights[b50_mask]).sum()
    b50_share = (b50_income / total_income * 100) if total_income > 0 else 0
    
    # Transfer dependency for bottom 50%
    transfers = np.zeros(len(df))
    for tc in transfer_cols:
        if tc in df.columns:
            vals = df[tc].fillna(0).values
            transfers += np.maximum(vals, 0)  # Only positive transfers
    
    b50_transfers = (transfers[b50_mask] * weights[b50_mask]).sum()
    b50_total_inc = (incomes[b50_mask] * weights[b50_mask]).sum()
    b50_transfer_pct = (b50_transfers / b50_total_inc * 100) if b50_total_inc > 0 else 0
    
    # Gini coefficient (weighted)
    # Using the standard formula for weighted data
    n = len(incomes)
    if n > 1:
        idx_sort = np.argsort(incomes)
        y_sorted = incomes[idx_sort]
        w_sorted = weights[idx_sort]
        w_sum = w_sorted.sum()
        yw_cumsum = np.cumsum(y_sorted * w_sorted)
        yw_total = yw_cumsum[-1]
        w_cumsum = np.cumsum(w_sorted)
        
        # Gini = 1 - 2 * (area under Lorenz curve)
        gini = 1 - 2 * np.sum(w_sorted * yw_cumsum) / (w_sum * yw_total) + 1/n
        gini = max(0, min(1, gini))
    else:
        gini = 0
    
    median_income = boundaries.get('p50', 0)
    
    result = {
        'survey_year': survey_year,
        'income_year': income_year,
        'n_records': len(df),
        'total_pop_weight': total_weight,
        'median_income': median_income,
        'median_income_real2024': real_cy(median_income, income_year),
        'bottom50_income_share': b50_share,
        'bottom50_transfer_pct': b50_transfer_pct,
        'gini_computed': gini,
        'q1_share': quintile_shares.get('q1', 0),
        'q2_share': quintile_shares.get('q2', 0),
        'q3_share': quintile_shares.get('q3', 0),
        'q4_share': quintile_shares.get('q4', 0),
        'q5_share': quintile_shares.get('q5', 0),
        'q1_mean_income': quintile_means.get('q1', 0),
        'q2_mean_income': quintile_means.get('q2', 0),
        'q3_mean_income': quintile_means.get('q3', 0),
        'q4_mean_income': quintile_means.get('q4', 0),
        'q5_mean_income': quintile_means.get('q5', 0),
        'p20': boundaries.get('p20', 0),
        'p50': boundaries.get('p50', 0),
        'p80': boundaries.get('p80', 0),
        'p90': boundaries.get('p90', 0),
        'p95': boundaries.get('p95', 0),
    }
    
    return result


# ============================================================================
# SECTION 3: CBO 25-YEAR BUDGET TRENDS (FY2000–FY2025)
# ============================================================================

def build_cbo_25year_trends():
    """
    Extract CBO budget data for FY2000–2025 and build trend dataset.
    
    All in real 2024 dollars using CPI deflator.
    
    Series:
    - Outlays: Total, Mandatory (SS, Medicaid, Income Security), 
      Discretionary (Defense, Nondefense), Net Interest
    - Revenue: Total, Individual, Corporate, Payroll, Customs
    - Deficit, Debt
    - All as % of GDP
    """
    logger.info("=" * 70)
    logger.info("SECTION 3: CBO 25-YEAR BUDGET TRENDS (FY2000–2025)")
    logger.info("=" * 70)
    
    # Series to extract
    cbo_series = {
        # Outlays (nominal $B)
        'CBO_OUTLAYS':                    'Total Outlays',
        'CBO_MAND_Total':                 'Mandatory Total',
        'CBO_MAND_Social_Security':       'Social Security',
        'CBO_MAND_Medicaid':              'Medicaid',
        'CBO_MAND_Income_securityᵇ':      'Income Security',
        'CBO_MAND_Medicare':              'Medicare',
        'CBO_DISC_Total':                 'Discretionary Total',
        'CBO_OUT_Net_interest':           'Net Interest',
        
        # Revenue (nominal $B)
        'CBO_REVENUES':                   'Total Revenue',
        'CBO_REV_Individual_income_taxes': 'Individual Income Tax',
        'CBO_REV_Corporate_income_taxes':  'Corporate Income Tax',
        'CBO_REV_Payroll_taxes':           'Payroll Taxes',
        'CBO_REV_Customs_duties':          'Customs Duties',
        'CBO_REV_Excise_taxes':            'Excise Taxes',
        
        # Deficit
        'CBO_DEFICIT':                     'Deficit (−) or Surplus',
        
        # Debt
        'CBO_DEBT_HELD':                   'Debt Held by Public',
        
        # % of GDP series
        'CBO_OUT_GDP_Net_interest':        'Net Interest (% GDP)',
        'CBO_REV_GDP_Customs_duties':      'Customs (% GDP)',
        'CBO_REV_GDP_Individual_income_taxes': 'Individual Income Tax (% GDP)',
        'CBO_REV_GDP_Corporate_income_taxes':  'Corporate Income Tax (% GDP)',
        'CBO_MAND_GDP_Total':              'Mandatory (% GDP)',
    }
    
    rows = []
    for fy in range(2000, 2026):
        row = {'fiscal_year': fy}
        
        for sid, label in cbo_series.items():
            # Query database for this FY
            obs = session.query(Observation).filter(
                Observation.series_id == sid,
                Observation.date >= date(fy, 1, 1),
                Observation.date <= date(fy, 12, 31)
            ).first()
            
            if obs:
                val = obs.value
                if 'GDP' not in sid and sid not in ['CBO_DEFICIT']:
                    # Nominal value — also compute real
                    row[f'{sid}_nominal'] = val
                    row[f'{sid}_real2024'] = real_fy(val, fy)
                else:
                    row[sid] = val
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Print summary
    logger.info(f"\n  FY2000–FY2025 CBO Budget Trends ({len(df)} years)")
    logger.info(f"  Columns: {len(df.columns)}")
    
    # Key trend highlights
    for sid, label in [('CBO_OUTLAYS', 'Total Outlays'), 
                        ('CBO_OUT_Net_interest', 'Net Interest'),
                        ('CBO_REV_Customs_duties', 'Customs Duties'),
                        ('CBO_MAND_Income_securityᵇ', 'Income Security')]:
        real_col = f'{sid}_real2024'
        if real_col in df.columns:
            v2000 = df.loc[df['fiscal_year']==2000, real_col].values
            v2025 = df.loc[df['fiscal_year']==2025, real_col].values
            if len(v2000) > 0 and len(v2025) > 0:
                v0, v25 = v2000[0], v2025[0]
                pct = ((v25 - v0) / abs(v0)) * 100 if v0 != 0 else 0
                logger.info(f"  {label:<25} FY2000: ${v0:>8.1f}B → FY2025: ${v25:>8.1f}B ({pct:+.0f}% real)")
    
    df.to_csv(PROCESSED / "cbo_25year_trends.csv", index=False)
    logger.info(f"\n  Saved cbo_25year_trends.csv")
    
    return df


# ============================================================================
# SECTION 4: DERIVED SERIES — Safety-net intensity, regressive revenue share
# ============================================================================

def compute_derived_25year_series():
    """
    Compute derived analytical series for FY2000–2025:
    
    1. Safety-net share: (Income Security + Medicaid) / Total Outlays
    2. Interest crowding ratio: Net Interest / (Income Security + Medicaid)
    3. Regressive revenue share: (Payroll + Excise + Customs) / Total Revenue
    4. Progressive revenue share: (Individual + Corporate) / Total Revenue
    5. Defense vs. safety-net ratio
    """
    logger.info("=" * 70)
    logger.info("SECTION 4: DERIVED 25-YEAR ANALYTICAL SERIES")
    logger.info("=" * 70)
    
    derived = []
    
    for fy in range(2000, 2026):
        def get_val(sid):
            obs = session.query(Observation).filter(
                Observation.series_id == sid,
                Observation.date >= date(fy, 1, 1),
                Observation.date <= date(fy, 12, 31)
            ).first()
            return obs.value if obs else None
        
        outlays = get_val('CBO_OUTLAYS')
        interest = get_val('CBO_OUT_Net_interest')
        income_sec = get_val('CBO_MAND_Income_securityᵇ')
        medicaid = get_val('CBO_MAND_Medicaid')
        social_sec = get_val('CBO_MAND_Social_Security')
        total_rev = get_val('CBO_REVENUES')
        payroll = get_val('CBO_REV_Payroll_taxes')
        excise = get_val('CBO_REV_Excise_taxes')
        customs = get_val('CBO_REV_Customs_duties')
        individual = get_val('CBO_REV_Individual_income_taxes')
        corporate = get_val('CBO_REV_Corporate_income_taxes')
        
        row = {'fiscal_year': fy}
        
        if all([outlays, income_sec, medicaid]):
            safety_net = income_sec + medicaid
            row['safety_net_nominal'] = safety_net
            row['safety_net_real2024'] = real_fy(safety_net, fy)
            row['safety_net_share_of_outlays'] = (safety_net / outlays * 100)
        
        if all([interest, income_sec, medicaid]):
            row['interest_crowding_ratio'] = interest / (income_sec + medicaid)
            row['interest_real2024'] = real_fy(interest, fy)
        
        if all([total_rev, payroll, excise, customs]):
            regressive = payroll + excise + customs
            row['regressive_rev_share'] = (regressive / total_rev * 100)
            row['customs_share_of_rev'] = (customs / total_rev * 100)
        
        if all([total_rev, individual, corporate]):
            progressive = individual + corporate
            row['progressive_rev_share'] = (progressive / total_rev * 100)
        
        if all([outlays]):
            row['total_outlays_real2024'] = real_fy(outlays, fy)
        
        if all([total_rev]):
            row['total_rev_real2024'] = real_fy(total_rev, fy)
        
        if customs:
            row['customs_real2024'] = real_fy(customs, fy)
        
        derived.append(row)
    
    df = pd.DataFrame(derived)
    
    # Print key findings
    for col, label in [
        ('safety_net_share_of_outlays', 'Safety-net / Total Outlays'),
        ('interest_crowding_ratio', 'Interest / Safety-net'),
        ('regressive_rev_share', 'Regressive Revenue Share'),
        ('customs_share_of_rev', 'Customs / Total Revenue'),
    ]:
        if col in df.columns:
            v00 = df.loc[df['fiscal_year']==2000, col].values
            v25 = df.loc[df['fiscal_year']==2025, col].values
            if len(v00) > 0 and len(v25) > 0:
                logger.info(f"  {label:<35} FY2000: {v00[0]:>6.1f}  FY2025: {v25[0]:>6.1f}")
    
    df.to_csv(PROCESSED / "derived_25year_series.csv", index=False)
    logger.info(f"\n  Saved derived_25year_series.csv")
    
    return df


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 75)
    logger.info("  HISTORICAL DATA COLLECTION FOR 25-YEAR ANALYSIS (FY2000–FY2025)")
    logger.info("=" * 75)
    
    # 1. Census income distribution + FRED distributional series
    fred_collected, census_quintiles = collect_census_income_distribution()
    
    # 2. CPS ASEC benchmark years
    cps_benchmarks = collect_cps_asec_benchmarks()
    
    # 3. CBO 25-year trends
    cbo_trends = build_cbo_25year_trends()
    
    # 4. Derived analytical series
    derived = compute_derived_25year_series()
    
    logger.info("\n" + "=" * 75)
    logger.info("  COLLECTION COMPLETE")
    logger.info("=" * 75)
    logger.info(f"  Census quintile years: {len(census_quintiles)}")
    logger.info(f"  CPS ASEC benchmarks:   {len(cps_benchmarks)}")
    logger.info(f"  CBO trend years:       {len(cbo_trends)}")
    logger.info(f"  Derived series years:  {len(derived)}")
    logger.info(f"\n  Output files in: {PROCESSED}")
