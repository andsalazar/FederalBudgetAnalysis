"""
Parse and load CBO data into the project database.
  1. CBO Historical Budget Data (Excel) — revenues, outlays, deficit, mandatory/discretionary 
  2. CBO Annual Economic Projections (CSV) — GDP, income, prices, employment
"""
import sys
sys.path.insert(0, '.')

import pandas as pd
import numpy as np
from datetime import date, datetime
from src.database.models import get_session, EconomicSeries, Observation, init_database
from src.utils.config import get_data_path, setup_logging
from loguru import logger

setup_logging()

RAW = get_data_path("raw")
XLSX = RAW / "51134-2026-02-Historical-Budget-Data.xlsx"
CSV = RAW / "Annual_CY_February2026.csv"

session = get_session()

# ============================================================================
# 1. CBO HISTORICAL BUDGET EXCEL
# ============================================================================

def parse_cbo_sheet(sheet_name, skip_rows=6):
    """Parse a CBO budget sheet — headers start around row 6-7."""
    df = pd.read_excel(XLSX, sheet_name=sheet_name, header=None)
    
    # Find the header row (first row with "Fiscal Year" or numeric years)
    header_row = None
    for i in range(len(df)):
        row_vals = df.iloc[i].astype(str)
        if any('fiscal year' in v.lower() for v in row_vals) or any('1962' in str(v) for v in df.iloc[i]):
            header_row = i
            break
    
    if header_row is None:
        # Try looking for row with mostly numeric years
        for i in range(len(df)):
            num_count = sum(1 for v in df.iloc[i] if isinstance(v, (int, float)) and 1960 <= v <= 2030)
            if num_count > 5:
                header_row = i
                break
    
    if header_row is None:
        header_row = skip_rows
    
    # The row before or at header_row has category names, data follows
    # For CBO budget sheets: rows are categories, columns are years
    # OR: first column is year, other columns are categories
    
    # Read with detected header
    df2 = pd.read_excel(XLSX, sheet_name=sheet_name, header=header_row)
    return df2

def load_budget_table1():
    """Sheet 1: Revenues, Outlays, Surplus/Deficit, Debt — nominal dollars (billions)."""
    logger.info("Parsing CBO Table 1: Revenues, Outlays, Surplus, Debt...")
    df = pd.read_excel(XLSX, sheet_name='1. Rev, Outlays, Surplus, Debt', header=None)
    
    # Find the data start
    data_start = None
    for i in range(len(df)):
        first_val = df.iloc[i, 0]
        if isinstance(first_val, (int, float)) and 1960 <= first_val <= 2030:
            data_start = i
            break
        if str(first_val).strip() == '1962':
            data_start = i
            break
    
    if data_start is None:
        # Look for "Fiscal Year" header
        for i in range(len(df)):
            if 'fiscal' in str(df.iloc[i, 0]).lower() or 'year' in str(df.iloc[i, 0]).lower():
                data_start = i + 1
                break
    
    if data_start is None:
        logger.error("Could not find data start in Table 1")
        return 0
    
    # Get the header row (one before data)
    header_idx = data_start - 1
    headers = df.iloc[header_idx].tolist()
    
    # Clean headers
    clean_headers = []
    for h in headers:
        h = str(h).strip()
        if h == 'nan' or h == '':
            h = 'Unknown'
        clean_headers.append(h)
    
    logger.info(f"  Headers found: {clean_headers[:10]}")
    
    # Read data rows
    data_df = df.iloc[data_start:].copy()
    data_df.columns = clean_headers
    
    # The first column should be fiscal year
    year_col = clean_headers[0]
    
    # Filter to numeric years only
    data_df = data_df[pd.to_numeric(data_df[year_col], errors='coerce').notna()].copy()
    data_df[year_col] = data_df[year_col].astype(int)
    
    # Map columns to series IDs
    series_map = {}
    for col in clean_headers[1:]:
        col_lower = col.lower()
        if 'revenue' in col_lower or 'receipt' in col_lower:
            series_map[col] = ('CBO_REVENUES', 'CBO: Federal Revenues', 'Billions of Dollars')
        elif 'outlay' in col_lower:
            series_map[col] = ('CBO_OUTLAYS', 'CBO: Federal Outlays', 'Billions of Dollars')
        elif 'surplus' in col_lower or 'deficit' in col_lower:
            series_map[col] = ('CBO_DEFICIT', 'CBO: Federal Deficit (-) or Surplus', 'Billions of Dollars')
        elif 'debt' in col_lower:
            series_map[col] = ('CBO_DEBT_HELD', 'CBO: Debt Held by the Public', 'Billions of Dollars')
    
    records = 0
    for col, (series_id, title, units) in series_map.items():
        # Create series metadata
        existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
        if not existing:
            session.add(EconomicSeries(
                series_id=series_id, source='CBO', title=title,
                units=units, frequency='Annual', last_updated=datetime.utcnow()
            ))
        
        for _, row in data_df.iterrows():
            year = int(row[year_col])
            val = row[col]
            if pd.isna(val):
                continue
            try:
                val = float(val)
            except (ValueError, TypeError):
                continue
            
            obs_date = date(year, 9, 30)  # Fiscal year end
            existing_obs = session.query(Observation).filter_by(
                series_id=series_id, date=obs_date
            ).first()
            if existing_obs:
                existing_obs.value = val
            else:
                session.add(Observation(series_id=series_id, date=obs_date, value=val))
            records += 1
    
    session.commit()
    logger.info(f"  Loaded {records} observations from Table 1")
    return records

def load_budget_table_generic(sheet_name, series_prefix, description_prefix, units='Billions of Dollars'):
    """Generic loader for CBO budget sheets (revenues by source, outlays by category, etc.)."""
    logger.info(f"Parsing CBO: {sheet_name}...")
    df = pd.read_excel(XLSX, sheet_name=sheet_name, header=None)
    
    # Find data start (first row with a year like 1962)
    data_start = None
    for i in range(len(df)):
        first_val = df.iloc[i, 0]
        try:
            if isinstance(first_val, (int, float)) and 1960 <= float(first_val) <= 2030:
                data_start = i
                break
        except:
            pass
    
    if data_start is None:
        logger.warning(f"  Could not find data start in {sheet_name}")
        return 0
    
    # Header row
    header_idx = data_start - 1
    headers = [str(h).strip() for h in df.iloc[header_idx].tolist()]
    
    data_df = df.iloc[data_start:].copy()
    data_df.columns = headers
    year_col = headers[0]
    
    data_df = data_df[pd.to_numeric(data_df[year_col], errors='coerce').notna()].copy()
    data_df[year_col] = data_df[year_col].astype(int)
    
    records = 0
    for col in headers[1:]:
        if col == 'nan' or col == 'Unknown' or not col.strip():
            continue
        
        # Create a clean series ID
        clean_name = col.replace(' ', '_').replace('/', '_').replace(',', '').replace("'", '')
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')[:40]
        series_id = f"{series_prefix}_{clean_name}"
        title = f"{description_prefix}: {col}"
        
        existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
        if not existing:
            session.add(EconomicSeries(
                series_id=series_id, source='CBO', title=title,
                units=units, frequency='Annual', last_updated=datetime.utcnow()
            ))
        
        for _, row in data_df.iterrows():
            year = int(row[year_col])
            val = row[col]
            if pd.isna(val):
                continue
            try:
                val = float(str(val).replace(',', ''))
            except (ValueError, TypeError):
                continue
            
            obs_date = date(year, 9, 30)
            existing_obs = session.query(Observation).filter_by(
                series_id=series_id, date=obs_date
            ).first()
            if existing_obs:
                existing_obs.value = val
            else:
                session.add(Observation(series_id=series_id, date=obs_date, value=val))
            records += 1
    
    session.commit()
    logger.info(f"  Loaded {records} observations from {sheet_name}")
    return records


# ============================================================================
# 2. CBO ANNUAL ECONOMIC PROJECTIONS CSV
# ============================================================================

def load_annual_projections():
    """Load CBO annual economic projections (GDP, income, CPI, employment, etc.)."""
    logger.info("Parsing CBO Annual Economic Projections CSV...")
    df = pd.read_csv(CSV)
    
    # Key columns for our hypothesis
    key_cols = {
        'gdp': ('CBO_GDP', 'CBO: Nominal GDP', 'Billions of Dollars'),
        'real_gdp': ('CBO_REAL_GDP', 'CBO: Real GDP', 'Billions of 2017 Dollars'),
        'personal_income': ('CBO_PERSONAL_INCOME', 'CBO: Personal Income', 'Billions of Dollars'),
        'compensation': ('CBO_COMPENSATION', 'CBO: Compensation of Employees', 'Billions of Dollars'),
        'wages_and_salaries': ('CBO_WAGES', 'CBO: Wages and Salaries', 'Billions of Dollars'),
        'corp_profits_adj': ('CBO_CORP_PROFITS', 'CBO: Corporate Profits (Adjusted)', 'Billions of Dollars'),
        'pce': ('CBO_PCE', 'CBO: Personal Consumption Expenditures', 'Billions of Dollars'),
        'cpiu': ('CBO_CPI', 'CBO: Consumer Price Index (CPI-U)', 'Index'),
        'core_cpiu': ('CBO_CORE_CPI', 'CBO: Core CPI-U', 'Index'),
        'unemployment_rate': ('CBO_UNRATE', 'CBO: Unemployment Rate', 'Percent'),
        'treasury_note_rate_10yr': ('CBO_10Y_RATE', 'CBO: 10-Year Treasury Note Rate', 'Percent'),
        'fed_funds_rate': ('CBO_FED_FUNDS', 'CBO: Federal Funds Rate', 'Percent'),
        'imports': ('CBO_IMPORTS', 'CBO: Imports', 'Billions of Dollars'),
        'exports': ('CBO_EXPORTS', 'CBO: Exports', 'Billions of Dollars'),
        'federal_government_c_gi': ('CBO_FED_SPENDING', 'CBO: Federal Government C & GI', 'Billions of Dollars'),
        'interest_inc_pers': ('CBO_INTEREST_INCOME', 'CBO: Personal Interest Income', 'Billions of Dollars'),
        'dividend_inc_pers': ('CBO_DIVIDEND_INCOME', 'CBO: Personal Dividend Income', 'Billions of Dollars'),
        'output_gap': ('CBO_OUTPUT_GAP', 'CBO: Output Gap', 'Percent of Potential GDP'),
    }
    
    records = 0
    for col, (series_id, title, units) in key_cols.items():
        if col not in df.columns:
            logger.warning(f"  Column '{col}' not found in CSV, skipping")
            continue
        
        existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
        if not existing:
            session.add(EconomicSeries(
                series_id=series_id, source='CBO', title=title,
                units=units, frequency='Annual', last_updated=datetime.utcnow()
            ))
        
        for _, row in df.iterrows():
            year = int(row['date'])
            val = row[col]
            if pd.isna(val):
                continue
            
            obs_date = date(year, 12, 31)  # Calendar year
            existing_obs = session.query(Observation).filter_by(
                series_id=series_id, date=obs_date
            ).first()
            if existing_obs:
                existing_obs.value = float(val)
            else:
                session.add(Observation(series_id=series_id, date=obs_date, value=float(val)))
            records += 1
    
    session.commit()
    logger.info(f"  Loaded {records} observations from Annual CY CSV")
    return records


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    total = 0
    
    # Budget tables
    total += load_budget_table1()
    
    budget_sheets = [
        ('2. Revenues', 'CBO_REV', 'CBO Revenue'),
        ('2a. Revenues as Share of GDP', 'CBO_REV_GDP', 'CBO Revenue (% GDP)', 'Percent of GDP'),
        ('3. Outlays', 'CBO_OUT', 'CBO Outlays'),
        ('3a. Outlays as Share of GDP', 'CBO_OUT_GDP', 'CBO Outlays (% GDP)', 'Percent of GDP'),
        ('5. Mandatory Outlays', 'CBO_MAND', 'CBO Mandatory Outlays'),
        ('5a. Mandatory Outlays (GDP)', 'CBO_MAND_GDP', 'CBO Mandatory Outlays (% GDP)', 'Percent of GDP'),
    ]
    
    for args in budget_sheets:
        try:
            total += load_budget_table_generic(*args)
        except Exception as e:
            logger.error(f"  Error loading {args[0]}: {e}")
    
    # Economic projections
    total += load_annual_projections()
    
    print(f"\n{'='*60}")
    print(f"CBO DATA IMPORT COMPLETE: {total:,} total observations loaded")
    print(f"{'='*60}")
    
    # Summary of CBO series
    cbo_series = session.query(EconomicSeries).filter_by(source='CBO').all()
    print(f"\nCBO series in database: {len(cbo_series)}")
    for s in cbo_series:
        count = session.query(Observation).filter_by(series_id=s.series_id).count()
        print(f"  {s.series_id:<35} {count:>5} obs | {s.title[:60]}")
    
    session.close()
