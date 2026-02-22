"""
=============================================================================
Collect granular federal spending data and build real-terms deflator
=============================================================================
1. Treasury MTS Table 9: Outlays by Budget Function (annual FY totals)
2. Treasury MTS Table 5: Outlays by Agency (annual FY totals)
3. BEA NIPA via FRED: Government spending by function (annual)
4. CBO Discretionary: Defense vs Nondefense
5. Build CPI deflator for real-terms conversion
=============================================================================
"""
import sys, time, json
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
import requests
from datetime import date, datetime
from fredapi import Fred
from loguru import logger

from src.utils.config import setup_logging
from src.database.models import get_session, EconomicSeries, Observation

setup_logging()
session = get_session()
fred = Fred(api_key='43272fac437c873feb1ace8519a979fc')

# ============================================================================
# 1. TREASURY MTS TABLE 9: Outlays by Budget Function
# ============================================================================

def collect_treasury_budget_functions():
    """Collect annual budget function outlays from Treasury MTS Table 9."""
    logger.info("=== Collecting Treasury MTS Table 9: Outlays by Budget Function ===")
    
    url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_9"
    
    # Get September (fiscal year end) data for each year
    all_records = []
    page = 1
    while True:
        params = {
            "filter": "record_calendar_month:eq:09,record_fiscal_year:gte:2000,data_type_cd:eq:T",
            "page[size]": 500,
            "page[number]": page,
            "sort": "record_fiscal_year",
        }
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            logger.error(f"  HTTP {resp.status_code}")
            break
        data = resp.json()
        records = data.get("data", [])
        if not records:
            break
        all_records.extend(records)
        total_pages = data.get("meta", {}).get("total-pages", 1)
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.3)
    
    logger.info(f"  Retrieved {len(all_records)} records")
    
    # Parse into series
    # Budget functions we care about (outlay categories)
    budget_functions = {}
    for rec in all_records:
        desc = rec.get("classification_desc", "")
        year = int(rec.get("record_fiscal_year", 0))
        amt_str = rec.get("current_fytd_rcpt_outly_amt", "0")
        try:
            amt = float(amt_str) / 1e6  # Convert to millions
        except:
            continue
        
        if not desc or year < 2000:
            continue
        
        # Only top-level budget functions (skip sub-items)
        seq_level = rec.get("sequence_level_nbr", "")
        if seq_level not in ["1", "2"]:  # Top-level only
            continue
            
        if desc not in budget_functions:
            budget_functions[desc] = {}
        budget_functions[desc][year] = amt
    
    obs_count = 0
    for func_name, year_data in sorted(budget_functions.items()):
        if len(year_data) < 3:
            continue
            
        clean_name = func_name.replace(' ', '_').replace(',', '').replace("'", '').replace('-', '_')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')[:50]
        series_id = f"TREAS_BF_{clean_name}"
        
        existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
        if not existing:
            session.add(EconomicSeries(
                series_id=series_id, source='Treasury_MTS',
                title=f"Budget Function: {func_name}",
                units='Millions of Dollars', frequency='Annual',
                last_updated=datetime.utcnow()
            ))
        
        for year, val in year_data.items():
            obs_date = date(year, 9, 30)
            existing_obs = session.query(Observation).filter_by(
                series_id=series_id, date=obs_date
            ).first()
            if existing_obs:
                existing_obs.value = val
            else:
                session.add(Observation(series_id=series_id, date=obs_date, value=val))
            obs_count += 1
    
    session.commit()
    logger.info(f"  Loaded {obs_count} observations across {len(budget_functions)} budget functions")
    return obs_count


# ============================================================================
# 2. TREASURY MTS TABLE 5: Outlays by Agency
# ============================================================================

def collect_treasury_agency_outlays():
    """Collect annual agency-level outlays from Treasury MTS Table 5."""
    logger.info("=== Collecting Treasury MTS Table 5: Outlays by Agency ===")
    
    url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_5"
    
    all_records = []
    page = 1
    while True:
        params = {
            "filter": "record_calendar_month:eq:09,record_fiscal_year:gte:2015",
            "page[size]": 500,
            "page[number]": page,
            "sort": "record_fiscal_year",
        }
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            logger.error(f"  HTTP {resp.status_code}")
            break
        data = resp.json()
        records = data.get("data", [])
        if not records:
            break
        all_records.extend(records)
        total_pages = data.get("meta", {}).get("total-pages", 1)
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.3)
    
    logger.info(f"  Retrieved {len(all_records)} records")
    
    agencies = {}
    for rec in all_records:
        desc = rec.get("classification_desc", "")
        year = int(rec.get("record_fiscal_year", 0))
        
        # Get the outlay amount — try different field names
        amt_str = rec.get("current_fytd_rcpt_outly_amt",
                     rec.get("current_month_app_rcpt_amt", "0"))
        try:
            # Gross outlays
            gross = float(rec.get("current_fytd_gross_outly_amt",
                           rec.get("fytd_gross_outly_amt", amt_str)))
            amt = gross / 1e6  # millions
        except:
            try:
                amt = float(amt_str) / 1e6
            except:
                continue
        
        seq_level = rec.get("sequence_level_nbr", "")
        if seq_level not in ["1"]:  # Agency level only
            continue
        
        if not desc or year < 2015:
            continue
        
        if desc not in agencies:
            agencies[desc] = {}
        agencies[desc][year] = amt
    
    obs_count = 0
    for agency_name, year_data in sorted(agencies.items()):
        if len(year_data) < 2:
            continue
        
        clean_name = agency_name.replace(' ', '_').replace(',', '').replace("'", '')
        clean_name = clean_name.replace('-', '_').replace('(', '').replace(')', '')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')[:50]
        series_id = f"TREAS_AG_{clean_name}"
        
        existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
        if not existing:
            session.add(EconomicSeries(
                series_id=series_id, source='Treasury_MTS',
                title=f"Agency Outlays: {agency_name}",
                units='Millions of Dollars', frequency='Annual',
                last_updated=datetime.utcnow()
            ))
        
        for year, val in year_data.items():
            obs_date = date(year, 9, 30)
            existing_obs = session.query(Observation).filter_by(
                series_id=series_id, date=obs_date
            ).first()
            if existing_obs:
                existing_obs.value = val
            else:
                session.add(Observation(series_id=series_id, date=obs_date, value=val))
            obs_count += 1
    
    session.commit()
    logger.info(f"  Loaded {obs_count} observations across {len(agencies)} agencies")
    return obs_count


# ============================================================================
# 3. BEA NIPA VIA FRED: Government Spending by Function
# ============================================================================

def collect_bea_function_spending():
    """Collect BEA NIPA government spending by function from FRED."""
    logger.info("=== Collecting BEA NIPA Spending by Function ===")
    
    bea_series = {
        'G160021A027NBEA': 'General Public Service',
        'G160071A027NBEA': 'National Defense',
        'G160081A027NBEA': 'Public Order and Safety',
        'G160131A027NBEA': 'Economic Affairs',
        'G160181A027NBEA': 'Transportation',
        'G160241A027NBEA': 'Space',
        'G160261A027NBEA': 'Housing and Community Services',
        'G160271A027NBEA': 'Health',
    }
    
    # Also get the quarterly defense/nondefense breakdown
    quarterly_series = {
        'A997RC1Q027SBEA': 'Federal: National Defense Consumption',
        'A542RC1Q027SBEA': 'Federal: Nondefense Consumption',
        'FDEFX': 'Federal Defense Consumption Expenditures',
    }
    
    obs_count = 0
    
    for sid, label in {**bea_series, **quarterly_series}.items():
        try:
            info = fred.get_series_info(sid)
            data = fred.get_series(sid, observation_start='2000-01-01')
            
            existing = session.query(EconomicSeries).filter_by(series_id=sid).first()
            if not existing:
                session.add(EconomicSeries(
                    series_id=sid, source='BEA/FRED',
                    title=f"BEA: {label}",
                    units=info.get('units', 'Billions of Dollars'),
                    frequency=info.get('frequency', 'Annual'),
                    last_updated=datetime.utcnow()
                ))
            
            for dt, val in data.items():
                if pd.isna(val):
                    continue
                obs_date = dt.date()
                existing_obs = session.query(Observation).filter_by(
                    series_id=sid, date=obs_date
                ).first()
                if existing_obs:
                    existing_obs.value = float(val)
                else:
                    session.add(Observation(series_id=sid, date=obs_date, value=float(val)))
                obs_count += 1
            
            logger.info(f"  {sid}: {label} — {len(data)} obs")
            time.sleep(0.6)
        except Exception as e:
            logger.warning(f"  {sid}: Error — {e}")
    
    session.commit()
    logger.info(f"  Total BEA: {obs_count} observations")
    return obs_count


# ============================================================================
# 4. CBO DISCRETIONARY DEFENSE VS NONDEFENSE
# ============================================================================

def load_cbo_discretionary():
    """Load CBO discretionary spending breakdown (defense vs nondefense)."""
    logger.info("=== Loading CBO Discretionary: Defense vs Nondefense ===")
    
    XLSX = 'data/raw/51134-2026-02-Historical-Budget-Data.xlsx'
    df = pd.read_excel(XLSX, sheet_name='4. Discretionary Outlays', header=None)
    
    # Find data start
    data_start = None
    for i in range(len(df)):
        try:
            if int(df.iloc[i, 0]) >= 1962:
                data_start = i
                break
        except:
            pass
    
    if data_start is None:
        logger.error("Could not find data start")
        return 0
    
    obs_count = 0
    series_map = {
        1: ('CBO_DISC_DEFENSE', 'CBO: Discretionary Defense Outlays'),
        2: ('CBO_DISC_NONDEFENSE', 'CBO: Discretionary Nondefense Outlays'),
        3: ('CBO_DISC_TOTAL', 'CBO: Total Discretionary Outlays'),
    }
    
    for col_idx, (series_id, title) in series_map.items():
        existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
        if not existing:
            session.add(EconomicSeries(
                series_id=series_id, source='CBO',
                title=title, units='Billions of Dollars',
                frequency='Annual', last_updated=datetime.utcnow()
            ))
        
        for i in range(data_start, len(df)):
            try:
                year = int(df.iloc[i, 0])
                val = float(df.iloc[i, col_idx])
            except:
                continue
            
            obs_date = date(year, 9, 30)
            existing_obs = session.query(Observation).filter_by(
                series_id=series_id, date=obs_date
            ).first()
            if existing_obs:
                existing_obs.value = val
            else:
                session.add(Observation(series_id=series_id, date=obs_date, value=val))
            obs_count += 1
    
    # Also load % GDP version
    df_gdp = pd.read_excel(XLSX, sheet_name='4a. Discretionary Outlays (GDP)', header=None)
    data_start_gdp = None
    for i in range(len(df_gdp)):
        try:
            if int(df_gdp.iloc[i, 0]) >= 1962:
                data_start_gdp = i
                break
        except:
            pass
    
    if data_start_gdp:
        gdp_map = {
            1: ('CBO_DISC_DEF_GDP', 'CBO: Defense Discretionary (% GDP)'),
            2: ('CBO_DISC_NONDEF_GDP', 'CBO: Nondefense Discretionary (% GDP)'),
        }
        for col_idx, (series_id, title) in gdp_map.items():
            existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
            if not existing:
                session.add(EconomicSeries(
                    series_id=series_id, source='CBO',
                    title=title, units='Percent of GDP',
                    frequency='Annual', last_updated=datetime.utcnow()
                ))
            
            for i in range(data_start_gdp, len(df_gdp)):
                try:
                    year = int(df_gdp.iloc[i, 0])
                    val = float(df_gdp.iloc[i, col_idx])
                except:
                    continue
                obs_date = date(year, 9, 30)
                existing_obs = session.query(Observation).filter_by(
                    series_id=series_id, date=obs_date
                ).first()
                if existing_obs:
                    existing_obs.value = val
                else:
                    session.add(Observation(series_id=series_id, date=obs_date, value=val))
                obs_count += 1
    
    session.commit()
    logger.info(f"  Loaded {obs_count} discretionary observations")
    return obs_count


# ============================================================================
# 5. BUILD CPI DEFLATOR TABLE
# ============================================================================

def build_deflator():
    """
    Build a fiscal-year CPI deflator table for converting nominal → real dollars.
    Base year: 2024 (latest full year).
    Uses CPI-U from FRED (CPIAUCSL, monthly) averaged to fiscal year.
    """
    logger.info("=== Building CPI Deflator (Base = FY2024) ===")
    
    cpi = fred.get_series('CPIAUCSL', observation_start='1960-01-01')
    
    # Fiscal year average CPI (Oct of prior year through Sep)
    fy_cpi = {}
    for fy in range(1963, 2026):
        # FY starts Oct of prior year, ends Sep of FY year
        start = pd.Timestamp(f'{fy-1}-10-01')
        end = pd.Timestamp(f'{fy}-09-30')
        mask = (cpi.index >= start) & (cpi.index <= end)
        fy_data = cpi[mask]
        if len(fy_data) >= 6:  # at least half the year
            fy_cpi[fy] = fy_data.mean()
    
    # Calendar year average CPI
    cy_cpi = {}
    for cy in range(1960, 2026):
        mask = cpi.index.year == cy
        cy_data = cpi[mask]
        if len(cy_data) >= 6:
            cy_cpi[cy] = cy_data.mean()
    
    # Base year CPI
    base_fy = fy_cpi.get(2024, 1)
    base_cy = cy_cpi.get(2024, 1)
    
    # Save deflators
    deflators = {
        'fiscal_year': {str(yr): base_fy / val for yr, val in fy_cpi.items()},
        'calendar_year': {str(yr): base_cy / val for yr, val in cy_cpi.items()},
        'base_year': 2024,
        'base_cpi_fy': base_fy,
        'base_cpi_cy': base_cy,
    }
    
    import json
    from src.utils.config import get_output_path
    deflator_path = get_output_path("tables") / "cpi_deflators.json"
    with open(deflator_path, 'w') as f:
        json.dump(deflators, f, indent=2)
    
    logger.info(f"  FY deflators: {len(fy_cpi)} years")
    logger.info(f"  CY deflators: {len(cy_cpi)} years")
    logger.info(f"  Base: FY2024 CPI = {base_fy:.1f}")
    logger.info(f"  Saved to {deflator_path}")
    
    # Also store deflators in DB for convenience
    for fy, factor in deflators['fiscal_year'].items():
        series_id = 'DEFLATOR_FY'
        existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
        if not existing:
            session.add(EconomicSeries(
                series_id=series_id, source='Computed',
                title='CPI Deflator (FY, base=2024)',
                units='Multiplier', frequency='Annual',
                last_updated=datetime.utcnow()
            ))
        obs_date = date(int(fy), 9, 30)
        existing_obs = session.query(Observation).filter_by(
            series_id=series_id, date=obs_date
        ).first()
        if existing_obs:
            existing_obs.value = factor
        else:
            session.add(Observation(series_id=series_id, date=obs_date, value=factor))
    
    session.commit()
    return deflators


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    total = 0
    total += collect_treasury_budget_functions()
    total += collect_treasury_agency_outlays()
    total += collect_bea_function_spending()
    total += load_cbo_discretionary()
    deflators = build_deflator()
    
    print(f"\n{'='*60}")
    print(f"GRANULAR DATA COLLECTION COMPLETE: {total:,} new observations")
    print(f"CPI deflators built: FY{min(deflators['fiscal_year'].keys())}–FY{max(deflators['fiscal_year'].keys())}")
    print(f"{'='*60}")
    
    # Summary
    for prefix in ['TREAS_BF_', 'TREAS_AG_', 'G160', 'CBO_DISC_']:
        series = session.query(EconomicSeries).filter(
            EconomicSeries.series_id.like(f'{prefix}%')
        ).all()
        if series:
            print(f"\n{prefix}* ({len(series)} series):")
            for s in series[:20]:
                count = session.query(Observation).filter_by(series_id=s.series_id).count()
                print(f"  {s.series_id:<55} {count:>4} obs | {s.title[:55]}")
    
    session.close()
