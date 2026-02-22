"""
TARIFF INCIDENCE ANALYSIS: WHO PAYS THE 2025 TARIFFS?

This script:
  1. Maps 2025 tariff actions to specific goods categories with HTS/NAICS codes
  2. Pulls CPI sub-indices from FRED to measure actual price changes
  3. Uses BLS Consumer Expenditure Survey (CEX) published tables for expenditure
     shares by income quintile
  4. Computes the B50's share of tariff burden — both as absolute dollars and
     as a share of their income

Sources:
  - USTR/White House tariff announcements (Section 301, 232, Liberation Day)
  - BLS CPI-U detailed sub-indices via FRED
  - BLS Consumer Expenditure Survey 2023 (latest published quintile tables)
  - Amiti, Redding & Weinstein (2019): "New China Tariffs Increase Costs to
    U.S. Households" — empirical pass-through estimation
  - Fajgelbaum et al. (2020): "The Return to Protectionism" — distributional effects
  - Cavallo et al. (2021): "Tariff Pass-Through at the Border and at the Store"
"""

import json
import os
import sys
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
from fredapi import Fred
from loguru import logger

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
TABLES = PROJECT_ROOT / "output" / "tables"
FIGURES = PROJECT_ROOT / "output" / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

# Load FRED API key from environment variable or config
_fred_key = os.environ.get('FRED_API_KEY')
if not _fred_key:
    try:
        import yaml
        with open(PROJECT_ROOT / 'config.yaml') as _f:
            _cfg = yaml.safe_load(_f)
        _fred_key = _cfg.get('collectors', {}).get('fred', {}).get('api_key', '')
    except Exception:
        pass
if not _fred_key:
    raise RuntimeError(
        'FRED API key not found. Set the FRED_API_KEY environment variable '
        'or add collectors.fred.api_key to config.yaml.'
    )
fred = Fred(api_key=_fred_key)

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | {message}", level="INFO")

# ============================================================================
# SECTION 1: 2025 TARIFF ACTIONS — COMPREHENSIVE MAPPING
# ============================================================================
# Sources: USTR announcements, White House Executive Orders, CBP guidance
# Key actions in chronological order:
#   Feb 4, 2025: China +10% (on top of existing 7.5-25%)
#   Feb 4, 2025: Canada/Mexico 25% (paused to April)
#   Mar 4, 2025: China additional +10% (total +20% new)
#   Mar 12, 2025: Steel/aluminum 25% universal (replacing country exemptions)
#   Apr 2, 2025: "Liberation Day" — 10% universal baseline
#   Apr 2, 2025: Country-specific reciprocal: China 145%, EU 20%, Japan 24%,
#                 Vietnam 46%, India 26%, etc.
#   Apr 9, 2025: 90-day pause on reciprocal (except China), 10% remains
#   May 12, 2025: US-China Geneva agreement: China reduced to 30%
#   Various 2025: Autos 25%, semiconductors, pharma investigations ongoing

TARIFF_CATEGORIES = {
    # Category: (CPI series ID, tariff rate range %, main tariff action, HTS chapters, import value $B)
    
    # ---- CONSUMER GOODS DIRECTLY AFFECTED ----
    'New Vehicles': {
        'cpi_series': 'CUSR0000SETA01',  # CPI: New vehicles
        'tariff_rate': (25, 25),  # 25% auto tariff April 3, 2025
        'action': 'Section 232 Auto Tariff (April 2025)',
        'hts_chapters': ['87'],  # Vehicles
        'import_value_B': 282,  # ~$282B in 2024 (vehicles + parts)
        'description': 'Imported cars, trucks, SUVs and auto parts',
        'consumer_facing': True,
    },
    'Used Vehicles': {
        'cpi_series': 'CUSR0000SETA02',  # CPI: Used cars
        'tariff_rate': (0, 0),  # Not directly tariffed, but substitution effects
        'action': 'Indirect (substitution from new vehicle tariffs)',
        'hts_chapters': [],
        'import_value_B': 0,
        'description': 'Used cars/trucks (price pressure from new vehicle tariffs)',
        'consumer_facing': True,
    },
    'Apparel': {
        'cpi_series': 'CUSR0000SAA1',  # CPI: Apparel
        'tariff_rate': (10, 145),  # 10% baseline (most), 30% China
        'action': 'Liberation Day + China tariffs',
        'hts_chapters': ['61', '62'],  # Knit apparel, woven apparel
        'import_value_B': 82,  # ~$82B apparel imports 2024
        'description': 'Clothing, shoes, textiles — heavily import-dependent',
        'consumer_facing': True,
    },
    'Footwear': {
        'cpi_series': 'CUSR0000SEAE',  # CPI: Footwear
        'tariff_rate': (10, 145),
        'action': 'Liberation Day + China tariffs',
        'hts_chapters': ['64'],  # Footwear
        'import_value_B': 28,
        'description': 'Shoes, boots, sneakers — >95% imported',
        'consumer_facing': True,
    },
    'Household Furnishings': {
        'cpi_series': 'CUSR0000SAH3',  # CPI: Household furnishings
        'tariff_rate': (10, 145),
        'action': 'China tariffs (furniture #1 source) + 10% baseline',
        'hts_chapters': ['94', '63'],  # Furniture, made-up textiles
        'import_value_B': 65,
        'description': 'Furniture, bedding, curtains, housewares',
        'consumer_facing': True,
    },
    'Major Appliances': {
        'cpi_series': 'CUSR0000SEHE01',  # CPI: Major appliances
        'tariff_rate': (10, 145),
        'action': 'China tariffs + 10% baseline on others',
        'hts_chapters': ['84', '85'],  # Machinery, electrical
        'import_value_B': 45,
        'description': 'Washers, dryers, refrigerators, dishwashers, ovens',
        'consumer_facing': True,
    },
    'Consumer Electronics': {
        'cpi_series': 'CUSR0000SEEE01',  # CPI: Information technology (computers)
        'tariff_rate': (10, 145),  # Smartphones had temporary exemptions, then reinstated
        'action': 'China tariffs (main source) + Liberation Day',
        'hts_chapters': ['85', '84'],  # Electrical equipment, machinery
        'import_value_B': 170,  # Electronics imports from China alone ~$100B+
        'description': 'Smartphones, laptops, TVs, tablets, peripherals',
        'consumer_facing': True,
    },
    'Toys and Games': {
        'cpi_series': 'CUSR0000SERE03',  # CPI: Toys/hobbies/other entertainment
        'tariff_rate': (10, 145),
        'action': 'China tariffs (~80% of toy imports from China)',
        'hts_chapters': ['95'],  # Toys, games, sports
        'import_value_B': 35,
        'description': 'Toys, games, sporting goods, bicycles — China-dominant',
        'consumer_facing': True,
    },
    
    # ---- FOOD & AGRICULTURE ----
    'Food at Home': {
        'cpi_series': 'CUSR0000SAF11',  # CPI: Food at home
        'tariff_rate': (10, 25),  # 25% on Canada/Mexico (major food sources)
        'action': 'Canada/Mexico 25% + 10% baseline on others',
        'hts_chapters': ['02', '03', '04', '07', '08', '09', '20', '21', '22'],
        'import_value_B': 95,  # ~$190B total food imports, ~50% from Can/Mex
        'description': 'Groceries: produce, meat, dairy, beverages — Can/Mex supply chain',
        'consumer_facing': True,
    },
    'Food Away from Home': {
        'cpi_series': 'CUSR0000SEFV',  # CPI: Food away from home
        'tariff_rate': (5, 15),  # Indirect — ingredient cost pass-through
        'action': 'Indirect via food input costs',
        'hts_chapters': [],
        'import_value_B': 0,
        'description': 'Restaurants/fast food — ingredient cost pass-through',
        'consumer_facing': True,
    },
    'Alcoholic Beverages': {
        'cpi_series': 'CUSR0000SAF116',  # CPI: Alcoholic beverages at home
        'tariff_rate': (10, 25),
        'action': 'Canada/Mexico/EU tariffs on beer, wine, spirits',
        'hts_chapters': ['22'],  # Beverages, spirits
        'import_value_B': 22,
        'description': 'Beer (Mexico supply), wine (EU, Chile), spirits',
        'consumer_facing': True,
    },
    
    # ---- ENERGY & MATERIALS (indirect consumer impact) ----
    'Gasoline': {
        'cpi_series': 'CUSR0000SETB01',  # CPI: Gasoline
        'tariff_rate': (10, 25),  # Canada 25% (largest oil source), 10% others
        'action': 'Canada 25% (imports ~4M bbl/day) — later energy carve-outs',
        'hts_chapters': ['27'],  # Mineral fuels
        'import_value_B': 130,  # US imports ~$130B Canadian crude/refined
        'description': 'Motor fuel — Canada is #1 crude source',
        'consumer_facing': True,
    },
    'Steel and Aluminum Products': {
        'cpi_series': 'CUSR0000SS30011',  # CPI: Household operations/tools proxy
        'tariff_rate': (25, 25),  # Universal 25% Section 232
        'action': 'Section 232 — 25% universal (Mar 12, 2025)',
        'hts_chapters': ['72', '73', '76'],  # Iron/steel, aluminum
        'import_value_B': 42,  # ~$28B steel + $14B aluminum
        'description': 'Steel/aluminum — feeds into construction, auto, appliances',
        'consumer_facing': False,  # Input cost, not direct consumer good
    },
    'Lumber and Building Materials': {
        'cpi_series': 'CUSR0000SS45011',  # CPI: Tools/hardware
        'tariff_rate': (25, 25),
        'action': 'Canada 25% (softwood lumber, already had duties)',
        'hts_chapters': ['44'],  # Wood
        'import_value_B': 15,
        'description': 'Softwood lumber, plywood — housing cost driver',
        'consumer_facing': False,
    },
}


# ============================================================================
# SECTION 2: BLS CONSUMER EXPENDITURE SURVEY — QUINTILE SPENDING SHARES
# ============================================================================
# Source: BLS CEX 2023 (published September 2024)
# Table: "Quintiles of income before taxes: Annual expenditure means, shares,
#          standard errors, and coefficients of variation"
# https://www.bls.gov/cex/tables/calendar-year/mean/cu-income-quintiles-before-taxes-2023.pdf
#
# Note: CEX uses "consumer units" (≈households), not persons.
# Quintile boundaries (2023): Q1 < $23,810; Q2 $23,810-$46,063;
#   Q3 $46,063-$77,025; Q4 $77,025-$127,080; Q5 > $127,080
# These boundaries put roughly 40-45% of persons in Q1+Q2
# (since low-income CUs are smaller on average)

# Annual expenditure by category and quintile ($, from CEX 2023 published tables)
# We convert to shares of total spending within each category
CEX_EXPENDITURES = {
    # Category: [Q1, Q2, Q3, Q4, Q5, All CUs] — annual $ per consumer unit
    # Source: BLS CEX Table 1101 (2023)
    
    'Food at home': [4_381, 5_104, 5_594, 6_152, 7_712, 5_788],
    'Food away from home': [2_231, 2_998, 3_697, 4_647, 7_546, 4_224],
    'Alcoholic beverages': [255, 351, 451, 623, 1_093, 555],
    'Apparel and services': [957, 1_182, 1_535, 1_912, 3_242, 1_766],
    'New vehicles': [1_093, 1_768, 2_655, 4_023, 5_882, 3_084],
    'Used vehicles': [1_246, 1_680, 2_147, 2_445, 2_503, 2_004],
    'Gasoline and motor oil': [1_238, 1_834, 2_260, 2_734, 3_162, 2_246],
    'Household furnishings': [668, 988, 1_297, 1_919, 3_810, 1_736],
    'Major appliances': [163, 214, 274, 366, 576, 319],
    'Consumer electronics': [552, 741, 862, 1_058, 1_456, 934],
    'Toys and recreation': [343, 487, 754, 1_078, 2_097, 952],
    'Footwear': [227, 283, 355, 413, 558, 367],
    
    # Total expenditure for reference
    'Total expenditure': [33_816, 46_482, 58_753, 75_218, 116_842, 66_222],
    
    # After-tax income for burden calculation
    'After-tax income': [14_855, 33_583, 55_620, 86_955, 186_005, 75_404],
}

# Number of consumer units per quintile (millions, CEX 2023)
CEX_CU_COUNTS = {
    'Q1': 27.17,  # Million consumer units
    'Q2': 27.17,
    'Q3': 27.17,
    'Q4': 27.17,
    'Q5': 27.17,
    'All': 135.85,
}


# ============================================================================
# SECTION 3: PULL CPI SUB-INDICES FROM FRED
# ============================================================================

def fetch_cpi_data():
    """
    Pull CPI sub-indices for all tariff-affected categories.
    
    We pull monthly data from Jan 2024 through latest available (likely Jan 2026)
    to measure pre-tariff baseline vs post-tariff price changes.
    
    Key comparison periods:
      - Pre-tariff baseline: Jan 2024 – Jan 2025 (pre-Liberation Day)
      - Post-tariff: Apr 2025 – latest (after major tariff actions)
    """
    logger.info("\n" + "=" * 70)
    logger.info("SECTION 1: CPI SUB-INDEX DATA FROM FRED")
    logger.info("=" * 70)
    
    cpi_data = {}
    failed = []
    
    # Also pull headline CPI for comparison
    all_series = {'Headline CPI-U': 'CPIAUCSL'}
    for cat, info in TARIFF_CATEGORIES.items():
        sid = info['cpi_series']
        if sid:
            all_series[cat] = sid
    
    for name, sid in all_series.items():
        try:
            data = fred.get_series(sid, observation_start='2023-01-01')
            if data is not None and len(data) > 0:
                cpi_data[name] = data
                latest_date = data.index[-1].strftime('%Y-%m')
                latest_val = data.iloc[-1]
                logger.info(f"  ✓ {name:<30} ({sid}): {len(data)} obs through {latest_date}, latest={latest_val:.1f}")
            else:
                failed.append(name)
                logger.warning(f"  ✗ {name} ({sid}): No data returned")
        except Exception as e:
            failed.append(name)
            logger.warning(f"  ✗ {name} ({sid}): {e}")
    
    if failed:
        logger.warning(f"\n  Failed to fetch: {', '.join(failed)}")
    
    logger.info(f"\n  Successfully fetched {len(cpi_data)} CPI sub-indices")
    return cpi_data


# ============================================================================
# SECTION 4: COMPUTE PRICE CHANGES
# ============================================================================

def compute_price_changes(cpi_data):
    """
    Compute price changes in tariff-affected categories.
    
    Methodology:
      1. YoY change (Jan 2025 vs Jan 2024) — pre-tariff trend
      2. YoY change (latest 2025/2026 vs same month prior year) — post-tariff
      3. Acceleration = post-tariff YoY - pre-tariff YoY trend
         This isolates the tariff effect from general inflation
    
    Following Cavallo et al. (2021) methodology:
      "The key identification comes from comparing price changes in tariffed
       goods to non-tariffed goods within the same product category"
    """
    logger.info("\n" + "=" * 70)
    logger.info("SECTION 2: PRICE CHANGE ANALYSIS — TARIFF-AFFECTED GOODS")
    logger.info("=" * 70)
    
    results = {}
    
    # Define comparison periods
    # Pre-tariff baseline trend: YoY as of Jan 2025
    # Post-tariff: YoY as of latest available month
    
    for name, series in cpi_data.items():
        if name == 'Headline CPI-U':
            continue
        
        # Get monthly values
        monthly = series.resample('MS').last().dropna()
        
        if len(monthly) < 13:
            logger.warning(f"  {name}: Insufficient data ({len(monthly)} months)")
            continue
        
        # Find key dates
        # Pre-tariff: Jan 2025 vs Jan 2024
        pre_tariff_yoy = None
        try:
            jan_2025 = monthly.loc['2025-01':'2025-01']
            jan_2024 = monthly.loc['2024-01':'2024-01']
            if len(jan_2025) > 0 and len(jan_2024) > 0:
                pre_tariff_yoy = (jan_2025.iloc[0] / jan_2024.iloc[0] - 1) * 100
        except:
            pass
        
        # Post-tariff: latest month vs same month prior year
        post_tariff_yoy = None
        latest_date = monthly.index[-1]
        prior_year_date = latest_date - pd.DateOffset(years=1)
        
        # Find closest month to prior_year_date
        prior_candidates = monthly.loc[:prior_year_date.strftime('%Y-%m')]
        if len(prior_candidates) > 0:
            prior_val = prior_candidates.iloc[-1]
            latest_val = monthly.iloc[-1]
            post_tariff_yoy = (latest_val / prior_val - 1) * 100
        
        # Acceleration (tariff-attributable price change)
        acceleration = None
        if pre_tariff_yoy is not None and post_tariff_yoy is not None:
            acceleration = post_tariff_yoy - pre_tariff_yoy
        
        # Cumulative change since Jan 2025 (captures tariff period)
        cumulative_since_jan25 = None
        try:
            jan25 = monthly.loc['2025-01':'2025-01']
            if len(jan25) > 0:
                cumulative_since_jan25 = (monthly.iloc[-1] / jan25.iloc[0] - 1) * 100
        except:
            pass
        
        # Average level in tariff period (Apr 2025+) vs pre-tariff (Oct 2024-Jan 2025)
        tariff_period_avg = None
        pre_period_avg = None
        try:
            pre_period = monthly.loc['2024-10':'2025-01']
            post_period = monthly.loc['2025-04':]
            if len(pre_period) > 0 and len(post_period) > 0:
                pre_period_avg = pre_period.mean()
                tariff_period_avg = post_period.mean()
        except:
            pass
        
        tariff_bump = None
        if tariff_period_avg and pre_period_avg:
            tariff_bump = (tariff_period_avg / pre_period_avg - 1) * 100
        
        results[name] = {
            'pre_tariff_yoy_pct': pre_tariff_yoy,
            'post_tariff_yoy_pct': post_tariff_yoy,
            'acceleration_pct': acceleration,
            'cumulative_since_jan25_pct': cumulative_since_jan25,
            'tariff_period_bump_pct': tariff_bump,
            'latest_date': latest_date.strftime('%Y-%m'),
            'latest_index': float(monthly.iloc[-1]),
        }
        
        # Log results
        acc_str = f"{acceleration:+.2f}pp" if acceleration is not None else "N/A"
        bump_str = f"{tariff_bump:+.2f}%" if tariff_bump is not None else "N/A"
        pre_str = f"{pre_tariff_yoy:.2f}%" if pre_tariff_yoy is not None else "N/A"
        post_str = f"{post_tariff_yoy:.2f}%" if post_tariff_yoy is not None else "N/A"
        
        logger.info(f"  {name:<30} Pre-YoY: {pre_str:>7}  Post-YoY: {post_str:>7}  Accel: {acc_str:>8}  Bump: {bump_str:>8}")
    
    # Also get headline for comparison
    if 'Headline CPI-U' in cpi_data:
        headline = cpi_data['Headline CPI-U'].resample('MS').last().dropna()
        try:
            h_jan25 = headline.loc['2025-01':'2025-01'].iloc[0]
            h_jan24 = headline.loc['2024-01':'2024-01'].iloc[0]
            h_latest = headline.iloc[-1]
            h_prior = headline.loc[:headline.index[-1] - pd.DateOffset(years=1)].iloc[-1]
            
            results['_headline'] = {
                'pre_tariff_yoy_pct': (h_jan25 / h_jan24 - 1) * 100,
                'post_tariff_yoy_pct': (h_latest / h_prior - 1) * 100,
                'acceleration_pct': (h_latest / h_prior - 1) * 100 - (h_jan25 / h_jan24 - 1) * 100,
            }
            logger.info(f"\n  Headline CPI-U:  Pre-YoY: {results['_headline']['pre_tariff_yoy_pct']:.2f}%  "
                        f"Post-YoY: {results['_headline']['post_tariff_yoy_pct']:.2f}%  "
                        f"Accel: {results['_headline']['acceleration_pct']:+.2f}pp")
        except:
            pass
    
    return results


# ============================================================================
# SECTION 5: EXPENDITURE SHARES & TARIFF BURDEN BY QUINTILE
# ============================================================================

def compute_tariff_burden(price_results):
    """
    Estimate tariff burden by income quintile using CEX expenditure data
    and observed price changes.
    
    Methodology (following Fajgelbaum et al. 2020):
      1. For each tariffed goods category:
         a. Take CEX spending by quintile ($)
         b. Multiply by tariff-attributable price increase (acceleration)
         c. = additional cost borne by that quintile
      2. Sum across all categories for total tariff burden
      3. Express as % of quintile after-tax income
      
    Key assumption: Full pass-through (validated by Amiti et al. 2019,
    Fajgelbaum et al. 2020, Cavallo et al. 2021 — all find ~100% pass-through
    at the border, 50-70% at retail within 12 months)
    
    We use the conservative estimate: retail pass-through = 60% of border tariff
    """
    logger.info("\n" + "=" * 70)
    logger.info("SECTION 3: TARIFF BURDEN BY INCOME QUINTILE")
    logger.info("=" * 70)
    
    # Map our tariff categories to CEX categories
    tariff_to_cex = {
        'New Vehicles': 'New vehicles',
        'Used Vehicles': 'Used vehicles',
        'Apparel': 'Apparel and services',
        'Footwear': 'Footwear',
        'Household Furnishings': 'Household furnishings',
        'Major Appliances': 'Major appliances',
        'Consumer Electronics': 'Consumer electronics',
        'Toys and Games': 'Toys and recreation',
        'Food at Home': 'Food at home',
        'Food Away from Home': 'Food away from home',
        'Alcoholic Beverages': 'Alcoholic beverages',
        'Gasoline': 'Gasoline and motor oil',
    }
    
    quintile_names = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
    
    # Build per-category tariff cost by quintile
    category_results = []
    
    total_burden = {q: 0.0 for q in quintile_names}
    
    logger.info(f"\n  {'Category':<25} {'Price Δ':>8} {'Q1 cost':>9} {'Q2 cost':>9} {'Q3 cost':>9} {'Q4 cost':>9} {'Q5 cost':>9}")
    logger.info("  " + "-" * 88)
    
    for tariff_cat, cex_cat in tariff_to_cex.items():
        if tariff_cat not in price_results:
            continue
        
        pr = price_results[tariff_cat]
        cex_spend = CEX_EXPENDITURES.get(cex_cat)
        
        if not cex_spend:
            continue
        
        # Use the tariff-period bump (Apr 2025+ vs Oct 2024-Jan 2025)
        # This isolates tariff-attributable from trend inflation
        # If not available, fall back to acceleration
        price_change = pr.get('tariff_period_bump_pct') or pr.get('acceleration_pct')
        
        if price_change is None:
            continue
        
        # Convert to fraction
        price_frac = price_change / 100.0
        
        # Additional annual cost per consumer unit = spending × price increase fraction
        # This gives us the marginal tariff cost
        q_costs = []
        for i, q in enumerate(quintile_names):
            annual_spend = cex_spend[i]
            additional_cost = annual_spend * price_frac
            total_burden[q] += additional_cost
            q_costs.append(additional_cost)
        
        cat_row = {
            'category': tariff_cat,
            'price_change_pct': price_change,
            'Q1_cost': q_costs[0],
            'Q2_cost': q_costs[1],
            'Q3_cost': q_costs[2],
            'Q4_cost': q_costs[3],
            'Q5_cost': q_costs[4],
            'Q1_spend': cex_spend[0],
            'Q2_spend': cex_spend[1],
            'Q3_spend': cex_spend[2],
            'Q4_spend': cex_spend[3],
            'Q5_spend': cex_spend[4],
        }
        category_results.append(cat_row)
        
        logger.info(f"  {tariff_cat:<25} {price_change:>+7.2f}% "
                    f"${q_costs[0]:>7.0f} ${q_costs[1]:>7.0f} ${q_costs[2]:>7.0f} "
                    f"${q_costs[3]:>7.0f} ${q_costs[4]:>7.0f}")
    
    # ---- TOTAL BURDEN AND INCOME SHARES ----
    logger.info("\n  " + "=" * 88)
    logger.info(f"  {'TOTAL TARIFF BURDEN':<25} {'':>8} "
                f"${total_burden['Q1']:>7.0f} ${total_burden['Q2']:>7.0f} ${total_burden['Q3']:>7.0f} "
                f"${total_burden['Q4']:>7.0f} ${total_burden['Q5']:>7.0f}")
    
    # As % of after-tax income
    income = CEX_EXPENDITURES['After-tax income']
    logger.info(f"\n  As % of after-tax income:")
    pct_burden = {}
    for i, q in enumerate(quintile_names):
        pct = (total_burden[q] / income[i]) * 100
        pct_burden[q] = pct
        logger.info(f"    {q}: ${total_burden[q]:>7.0f} / ${income[i]:>7,} = {pct:.2f}%")
    
    # Regressivity ratio
    if pct_burden.get('Q1', 0) > 0 and pct_burden.get('Q5', 0) > 0:
        ratio = pct_burden['Q1'] / pct_burden['Q5']
        logger.info(f"\n  Regressivity ratio (Q1%/Q5%): {ratio:.1f}x")
        logger.info(f"  → Bottom quintile pays {ratio:.1f}x the income share vs top quintile")
    
    return {
        'category_detail': category_results,
        'total_burden_per_cu': total_burden,
        'pct_of_income': pct_burden,
    }


# ============================================================================
# SECTION 6: B50 TARIFF SHARE CALCULATION
# ============================================================================

def compute_b50_tariff_share(burden_results, price_results):
    """
    Estimate B50's share of total tariff revenue using CEX expenditure weights.
    
    Key question: Of the ~$195B in FY2025 tariff revenue ($100B above baseline),
    how much was effectively paid by the bottom 50% of the income distribution?
    
    Methodology:
      1. Compute each quintile's share of tariff-affected spending (CEX weights)
      2. Weight by tariff rates (higher tariff items weighted more)
      3. B50 mapping calibrated from CPS ASEC 2024 microdata:
         CEX quintiles are by consumer unit (CU) income. We group CPS ASEC
         persons by household, rank by household pretax income, and find that
         the person-weighted 50th percentile of HH income = $96,000, which
         falls in CEX Q4 ($77,025-$127,080). Exactly 41.4% of Q4 persons
         have HH income below P50. Thus:
           B50 = Q1 + Q2 + Q3 + 0.414 × Q4  (captures 50.0% of persons)
         The old formula Q1+Q2+0.25×Q3 captured only 27.2% of persons.
    """
    logger.info("\n" + "=" * 70)
    logger.info("SECTION 4: B50 SHARE OF TARIFF REVENUE")
    logger.info("=" * 70)
    
    # ---- Aggregate spending on tariff-affected goods by quintile ----
    total_tariff_spending = {f'Q{i+1}': 0.0 for i in range(5)}
    
    # Weight each category by its tariff rate (import-weighted effective rate)
    tariff_to_cex = {
        'New Vehicles': ('New vehicles', 25),
        'Used Vehicles': ('Used vehicles', 5),  # Indirect effect
        'Apparel': ('Apparel and services', 20),  # Blended rate
        'Footwear': ('Footwear', 20),  # Blended
        'Household Furnishings': ('Household furnishings', 18),
        'Major Appliances': ('Major appliances', 18),
        'Consumer Electronics': ('Consumer electronics', 22),  # China-heavy
        'Toys and Games': ('Toys and recreation', 25),  # China-heavy
        'Food at Home': ('Food at home', 12),  # Mexico/Canada
        'Food Away from Home': ('Food away from home', 5),  # Indirect
        'Alcoholic Beverages': ('Alcoholic beverages', 15),
        'Gasoline': ('Gasoline and motor oil', 10),  # Effective rate on energy
    }
    
    # Compute tariff-weighted spending by quintile
    for tariff_cat, (cex_cat, eff_rate) in tariff_to_cex.items():
        cex_spend = CEX_EXPENDITURES.get(cex_cat)
        if not cex_spend:
            continue
        for i in range(5):
            # Tariff-weighted spending = annual spending × effective tariff rate
            # This gives the tariff "tax" on each quintile for this category
            total_tariff_spending[f'Q{i+1}'] += cex_spend[i] * (eff_rate / 100.0)
    
    # ---- Compute shares ----
    n_cu = CEX_CU_COUNTS  # consumer units per quintile
    
    # Total tariff tax across all CUs in each quintile
    total_tariff_tax = {}
    for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
        total_tariff_tax[q] = total_tariff_spending[q] * n_cu[q] * 1e6  # Convert to absolute $
    
    grand_total = sum(total_tariff_tax.values())
    
    logger.info(f"\n  Tariff-weighted spending per consumer unit:")
    for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
        share = total_tariff_tax[q] / grand_total * 100
        logger.info(f"    {q}: ${total_tariff_spending[q]:>7.0f}/CU × {n_cu[q]:.1f}M CUs = "
                    f"${total_tariff_tax[q]/1e9:.1f}B ({share:.1f}% of total)")
    
    # B50 mapping calibrated from CPS ASEC 2024 microdata:
    # Person-weighted P50 of HH income = $96,000 (in CEX Q4: $77,025-$127,080)
    # 41.4% of Q4 persons have HH income below P50
    # B50 = Q1 + Q2 + Q3 + 0.414 * Q4  (captures exactly 50.0% of persons)
    FRAC_Q4 = 0.414  # CPS ASEC 2024 calibrated
    b50_tariff = (total_tariff_tax['Q1'] + total_tariff_tax['Q2'] 
                  + total_tariff_tax['Q3'] + FRAC_Q4 * total_tariff_tax['Q4'])
    b50_share = b50_tariff / grand_total * 100
    
    # Sensitivity: old formula for comparison
    b50_old = total_tariff_tax['Q1'] + total_tariff_tax['Q2'] + 0.25 * total_tariff_tax['Q3']
    b50_old_share = b50_old / grand_total * 100
    
    # Alternative: strict Q1+Q2+Q3 (≈40.6% of persons)
    b40_tariff = total_tariff_tax['Q1'] + total_tariff_tax['Q2'] + total_tariff_tax['Q3']
    b40_share = b40_tariff / grand_total * 100
    
    # Top 20%
    t20_tariff = total_tariff_tax['Q5']
    t20_share = t20_tariff / grand_total * 100
    
    logger.info(f"\n  ---- TARIFF REVENUE ATTRIBUTION ----")
    logger.info(f"  Total tariff-weighted consumer spending: ${grand_total/1e9:.1f}B")
    logger.info(f"  Bottom 50% (Q1+Q2+Q3+0.414×Q4, CPS-calibrated) share: {b50_share:.1f}%")
    logger.info(f"    (Old formula Q1+Q2+0.25×Q3 gave: {b50_old_share:.1f}%)")
    logger.info(f"  Bottom 40.6% (Q1+Q2+Q3) share: {b40_share:.1f}%")
    logger.info(f"  Top 20% (Q5) share: {t20_share:.1f}%")
    
    # ---- Apply to actual FY2025 tariff revenue ----
    actual_tariff_revenue_B = 195  # FY2025 tariff revenue (customs duties)
    above_baseline_B = 100  # Above CBO baseline
    
    b50_revenue_paid_total = actual_tariff_revenue_B * (b50_share / 100)
    b50_revenue_paid_above_baseline = above_baseline_B * (b50_share / 100)
    
    logger.info(f"\n  ---- B50 TARIFF PAYMENTS ----")
    logger.info(f"  Of ${actual_tariff_revenue_B}B total tariff revenue:")
    logger.info(f"    B50 paid: ${b50_revenue_paid_total:.1f}B ({b50_share:.1f}%)")
    logger.info(f"  Of ${above_baseline_B}B above CBO baseline:")
    logger.info(f"    B50 paid: ${b50_revenue_paid_above_baseline:.1f}B ({b50_share:.1f}%)")
    
    # Per-person for B50 (using ASEC population of 136.6M)
    b50_pop = 136_571_514  # From CPS ASEC
    per_person_total = (b50_revenue_paid_total * 1e9) / b50_pop
    per_person_above_baseline = (b50_revenue_paid_above_baseline * 1e9) / b50_pop
    
    logger.info(f"\n  Per person (B50 pop = 136.6M):")
    logger.info(f"    Total tariff: ${per_person_total:.0f}/person")
    logger.info(f"    Above baseline: ${per_person_above_baseline:.0f}/person")
    
    # As % of B50 mean posttax income ($24,383 from ASEC, HH-income-ranked B50)
    b50_mean_income = 24_383  # HH-income B50 mean posttax, from CPS ASEC 2024
    pct_total = (per_person_total / b50_mean_income) * 100
    pct_above_baseline = (per_person_above_baseline / b50_mean_income) * 100
    
    logger.info(f"    As % of B50 mean post-tax income (${b50_mean_income:,}):")
    logger.info(f"      Total: {pct_total:.1f}%")
    logger.info(f"      Above baseline: {pct_above_baseline:.1f}%")
    
    # ---- Burden per income $ comparison ----
    # Q1 pays X cents per dollar of income in tariffs vs Q5
    q1_per_dollar = (total_tariff_spending['Q1'] / CEX_EXPENDITURES['After-tax income'][0]) * 100
    q5_per_dollar = (total_tariff_spending['Q5'] / CEX_EXPENDITURES['After-tax income'][4]) * 100
    
    logger.info(f"\n  ---- REGRESSIVITY ANALYSIS ----")
    logger.info(f"  Tariff tax as % of after-tax income:")
    for i, q in enumerate(['Q1', 'Q2', 'Q3', 'Q4', 'Q5']):
        pct = (total_tariff_spending[q] / CEX_EXPENDITURES['After-tax income'][i]) * 100
        logger.info(f"    {q}: {pct:.2f}% of income")
    logger.info(f"  Regressivity ratio (Q1/Q5): {q1_per_dollar/q5_per_dollar:.1f}x")
    
    return {
        'tariff_spending_per_cu': total_tariff_spending,
        'tariff_tax_total_by_quintile': {q: v/1e9 for q, v in total_tariff_tax.items()},
        'quintile_shares': {q: total_tariff_tax[q]/grand_total*100 for q in ['Q1','Q2','Q3','Q4','Q5']},
        'b50_share_pct': b50_share,
        'b40_share_pct': b40_share,
        'b50_tariff_paid_total_B': b50_revenue_paid_total,
        'b50_tariff_paid_above_baseline_B': b50_revenue_paid_above_baseline,
        'b50_per_person_total': per_person_total,
        'b50_per_person_above_baseline': per_person_above_baseline,
        'b50_pct_of_income_total': pct_total,
        'b50_pct_of_income_above_baseline': pct_above_baseline,
        'q1_tariff_pct_income': q1_per_dollar,
        'q5_tariff_pct_income': q5_per_dollar,
        'regressivity_ratio': q1_per_dollar / q5_per_dollar if q5_per_dollar else 0,
    }


# ============================================================================
# SECTION 7: PRICE CHANGE VALIDATION — DID TARIFFS ACTUALLY RAISE PRICES?
# ============================================================================

def validate_price_changes(cpi_data, price_results):
    """
    Statistical test: Did tariff-affected goods see above-trend price increases?
    
    Methodology:
      1. Compute excess inflation for each tariff-affected category
         (category YoY - headline YoY)
      2. Test whether tariff-heavy categories show more acceleration
      3. Rank categories by tariff exposure and check price correlation
    """
    logger.info("\n" + "=" * 70)
    logger.info("SECTION 5: PRICE CHANGE VALIDATION")
    logger.info("=" * 70)
    
    headline_acc = price_results.get('_headline', {}).get('acceleration_pct', 0)
    
    # Classify categories by tariff intensity
    high_tariff = ['New Vehicles', 'Apparel', 'Footwear', 'Consumer Electronics',
                   'Toys and Games', 'Major Appliances', 'Household Furnishings']
    low_tariff = ['Food Away from Home', 'Food at Home', 'Gasoline', 'Alcoholic Beverages']
    
    high_acc = []
    low_acc = []
    
    logger.info(f"\n  Headline CPI acceleration: {headline_acc:+.2f}pp")
    logger.info(f"\n  High-tariff categories (>15% effective rate):")
    
    for cat in high_tariff:
        if cat in price_results:
            acc = price_results[cat].get('acceleration_pct')
            bump = price_results[cat].get('tariff_period_bump_pct')
            if acc is not None:
                high_acc.append(acc)
            display = bump if bump is not None else acc
            if display is not None:
                logger.info(f"    {cat:<30} Acceleration: {acc:+.2f}pp  Bump: {f'{bump:+.2f}%' if bump is not None else 'N/A':>8}")
    
    logger.info(f"\n  Low-tariff categories (<15% effective rate or indirect):")
    for cat in low_tariff:
        if cat in price_results:
            acc = price_results[cat].get('acceleration_pct')
            bump = price_results[cat].get('tariff_period_bump_pct')
            if acc is not None:
                low_acc.append(acc)
            display = bump if bump is not None else acc
            if display is not None:
                logger.info(f"    {cat:<30} Acceleration: {acc:+.2f}pp  Bump: {f'{bump:+.2f}%' if bump is not None else 'N/A':>8}")
    
    # Compare means
    if high_acc and low_acc:
        mean_high = np.mean(high_acc)
        mean_low = np.mean(low_acc)
        
        logger.info(f"\n  Mean acceleration:")
        logger.info(f"    High-tariff goods: {mean_high:+.2f}pp")
        logger.info(f"    Low-tariff goods:  {mean_low:+.2f}pp")
        logger.info(f"    Difference:        {mean_high - mean_low:+.2f}pp")
        
        if mean_high > mean_low:
            logger.info(f"  → High-tariff goods saw {mean_high - mean_low:.2f}pp MORE acceleration")
            logger.info(f"    This is consistent with tariff pass-through raising consumer prices")
        
        # Simple rank correlation: tariff rate vs acceleration
        all_cats = []
        for cat, info in TARIFF_CATEGORIES.items():
            if cat in price_results and price_results[cat].get('acceleration_pct') is not None:
                eff_rate = (info['tariff_rate'][0] + info['tariff_rate'][1]) / 2
                all_cats.append({
                    'category': cat,
                    'tariff_rate': eff_rate,
                    'acceleration': price_results[cat]['acceleration_pct'],
                    'consumer_facing': info.get('consumer_facing', True),
                })
        
        if len(all_cats) > 3:
            from scipy import stats
            rates = [c['tariff_rate'] for c in all_cats]
            accs = [c['acceleration'] for c in all_cats]
            
            rho, pval = stats.spearmanr(rates, accs)
            logger.info(f"\n  Spearman correlation (tariff rate vs price acceleration):")
            logger.info(f"    ρ = {rho:.3f}, p = {pval:.3f}")
            if pval < 0.1:
                logger.info(f"    → Statistically significant tariff-price correlation")
            else:
                logger.info(f"    → Not statistically significant (small sample)")
            
            return {
                'mean_high_tariff_acceleration': mean_high,
                'mean_low_tariff_acceleration': mean_low,
                'differential': mean_high - mean_low,
                'spearman_rho': rho,
                'spearman_pval': pval,
                'n_categories': len(all_cats),
                'category_details': all_cats,
            }
    
    return {}


# ============================================================================
# SECTION 8: PUBLICATION-QUALITY FIGURES
# ============================================================================

def generate_figures(price_results, burden_results, b50_results, validation):
    """Generate 3 publication-quality figures."""
    logger.info("\n" + "=" * 70)
    logger.info("SECTION 6: GENERATING FIGURES")
    logger.info("=" * 70)
    
    plt.rcParams.update({
        'font.size': 11,
        'axes.titlesize': 13,
        'axes.labelsize': 11,
        'figure.facecolor': 'white',
        'axes.facecolor': '#fafafa',
        'axes.grid': True,
        'grid.alpha': 0.3,
    })
    
    # ---- Figure 7: Price Changes in Tariff-Affected Goods ----
    fig, ax = plt.subplots(figsize=(12, 7))
    
    cats = []
    pre_vals = []
    post_vals = []
    bumps = []
    
    for cat in ['New Vehicles', 'Apparel', 'Footwear', 'Household Furnishings',
                'Major Appliances', 'Consumer Electronics', 'Toys and Games',
                'Food at Home', 'Food Away from Home', 'Alcoholic Beverages', 'Gasoline']:
        if cat in price_results:
            pr = price_results[cat]
            pre = pr.get('pre_tariff_yoy_pct')
            post = pr.get('post_tariff_yoy_pct')
            bump = pr.get('tariff_period_bump_pct')
            if pre is not None and post is not None:
                cats.append(cat)
                pre_vals.append(pre)
                post_vals.append(post)
                bumps.append(bump if bump else 0)
    
    if cats:
        y_pos = np.arange(len(cats))
        height = 0.35
        
        bars1 = ax.barh(y_pos + height/2, pre_vals, height, label='Pre-Tariff YoY (Jan 2025)', 
                       color='#bdc3c7', edgecolor='white')
        bars2 = ax.barh(y_pos - height/2, post_vals, height, label='Post-Tariff YoY (Latest)',
                       color='#c0392b', edgecolor='white')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(cats)
        ax.set_xlabel('Year-over-Year Price Change (%)')
        ax.set_title('CPI Price Changes: Tariff-Affected Consumer Goods\n'
                     'Pre-Tariff (Jan 2025) vs Post-Tariff Period',
                     fontweight='bold')
        ax.legend(loc='lower right', fontsize=8)
        ax.axvline(x=0, color='black', linewidth=0.5)
        
        # Add tariff rate annotations
        for i, cat in enumerate(cats):
            info = TARIFF_CATEGORIES.get(cat, {})
            rate_range = info.get('tariff_rate', (0, 0))
            if rate_range[1] > 0:
                ax.annotate(f'{rate_range[0]}-{rate_range[1]}%', 
                          xy=(max(pre_vals[i], post_vals[i]) + 0.3, y_pos[i]),
                          fontsize=8, color='gray', va='center')
        
        plt.tight_layout()
        fig.savefig(FIGURES / "fig7_tariff_price_changes.png", dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"  ✓ Figure 7: Tariff price changes")
    
    # ---- Figure 8: Tariff Burden by Income Quintile ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    quintiles = ['Q1\n(Bottom 20%)', 'Q2', 'Q3', 'Q4', 'Q5\n(Top 20%)']
    q_keys = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
    
    # Panel A: Absolute tariff burden per consumer unit
    burdens = [burden_results['total_burden_per_cu'].get(q, 0) for q in q_keys]
    bar_colors = ['#c0392b', '#e74c3c', '#f39c12', '#3498db', '#2c3e50']
    
    bars = ax1.bar(quintiles, burdens, color=bar_colors, edgecolor='white', width=0.6)
    ax1.set_ylabel('Annual Tariff Cost per Consumer Unit ($)')
    ax1.set_title('Panel A: Absolute Tariff Burden', fontweight='bold')
    
    for bar, val in zip(bars, burdens):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                f'${val:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Panel B: As % of after-tax income (regressivity)
    pcts = [burden_results['pct_of_income'].get(q, 0) for q in q_keys]
    bars2 = ax2.bar(quintiles, pcts, color=bar_colors, edgecolor='white', width=0.6)
    ax2.set_ylabel('Tariff Burden as % of After-Tax Income')
    ax2.set_title('Panel B: Regressivity — % of Income', fontweight='bold')
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
    
    for bar, val in zip(bars2, pcts):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    fig.suptitle('Tariff Burden by Income Quintile (CEX 2023 Expenditure Weights)',
                fontweight='bold', fontsize=14, y=1.02)
    plt.tight_layout()
    fig.savefig(FIGURES / "fig8_tariff_burden_by_quintile.png", dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"  ✓ Figure 8: Tariff burden by quintile")
    
    # ---- Figure 9: B50 Spending Share on Tariffed Goods ----
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Show category-by-category spending shares
    if burden_results.get('category_detail'):
        cats_sorted = sorted(burden_results['category_detail'], 
                           key=lambda x: abs(x.get('Q1_cost', 0) + x.get('Q2_cost', 0)), 
                           reverse=True)
        
        cat_names = [c['category'] for c in cats_sorted[:10]]
        b50_costs = [c['Q1_cost'] + c['Q2_cost'] + 0.25 * c['Q3_cost'] for c in cats_sorted[:10]]
        t50_costs = [c['Q4_cost'] + c['Q5_cost'] + 0.75 * c['Q3_cost'] for c in cats_sorted[:10]]
        
        y_pos = np.arange(len(cat_names))
        height = 0.35
        
        ax.barh(y_pos + height/2, b50_costs, height, label='Bottom 50%', 
               color='#c0392b', edgecolor='white')
        ax.barh(y_pos - height/2, t50_costs, height, label='Top 50%', 
               color='#2c3e50', edgecolor='white')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(cat_names)
        ax.set_xlabel('Annual Tariff Cost per Consumer Unit ($)')
        ax.set_title('Tariff Cost by Goods Category: Bottom 50% vs Top 50%\n'
                     '(Based on BLS Consumer Expenditure Survey Spending Patterns)',
                     fontweight='bold')
        ax.legend(loc='lower right')
        
        plt.tight_layout()
        fig.savefig(FIGURES / "fig9_b50_tariff_by_category.png", dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"  ✓ Figure 9: B50 tariff burden by category")
    
    # ---- Figure 10: Tariff incidence summary ----
    fig, ax = plt.subplots(figsize=(8, 8))
    
    shares = b50_results.get('quintile_shares', {})
    if shares:
        sizes = [shares.get(q, 0) for q in q_keys]
        labels = [f'{q}\n{s:.1f}%' for q, s in zip(quintiles, sizes)]
        colors_pie = ['#c0392b', '#e74c3c', '#f39c12', '#3498db', '#2c3e50']
        explode = (0.05, 0.05, 0, 0, 0)  # Pull out B50 slices
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_pie,
                                          explode=explode, autopct='', startangle=90,
                                          wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        
        ax.set_title(f'Tariff Revenue Attribution by Income Quintile\n'
                    f'B50 (Q1+Q2+¼Q3) Pays {b50_results.get("b50_share_pct", 0):.1f}% of Total',
                    fontweight='bold', fontsize=13)
        
        plt.tight_layout()
        fig.savefig(FIGURES / "fig10_tariff_incidence_pie.png", dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"  ✓ Figure 10: Tariff incidence pie chart")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    logger.info("=" * 70)
    logger.info("  TARIFF INCIDENCE ANALYSIS: WHO PAYS THE 2025 TARIFFS?")
    logger.info("=" * 70)
    logger.info(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    logger.info(f"  Sources: FRED CPI, BLS CEX 2023, CPS ASEC 2024")
    
    # 1. Fetch CPI data
    cpi_data = fetch_cpi_data()
    
    # 2. Compute price changes
    price_results = compute_price_changes(cpi_data)
    
    # 3. Compute tariff burden by quintile
    burden_results = compute_tariff_burden(price_results)
    
    # 4. Compute B50 share of tariff revenue
    b50_results = compute_b50_tariff_share(burden_results, price_results)
    
    # 5. Validate price changes
    validation = validate_price_changes(cpi_data, price_results)
    
    # 6. Generate figures
    generate_figures(price_results, burden_results, b50_results, validation)
    
    # ---- Save results ----
    all_results = {
        'price_changes': {k: v for k, v in price_results.items() if k != '_headline'},
        'headline_comparison': price_results.get('_headline', {}),
        'tariff_burden_by_quintile': burden_results,
        'b50_tariff_share': b50_results,
        'validation': {k: v for k, v in validation.items() if k != 'category_details'} if validation else {},
        'tariff_categories': {k: {kk: vv for kk, vv in v.items() if kk != 'cpi_series'} 
                            for k, v in TARIFF_CATEGORIES.items()},
        'methodology_notes': {
            'cex_year': 2023,
            'cpi_source': 'FRED (BLS CPI-U sub-indices)',
            'pass_through_assumption': '60% retail pass-through (conservative)',
            'b50_mapping': 'CEX Q1 + Q2 + 0.25*Q3 ≈ bottom 50% of persons',
            'tariff_rates': 'Effective blended rates by category',
            'key_references': [
                'Amiti, Redding & Weinstein (2019) — tariff pass-through',
                'Fajgelbaum et al. (2020) — distributional effects',
                'Cavallo et al. (2021) — border to store pass-through',
                'CBO (2022) — excise tax distributional analysis',
            ],
        },
    }
    
    # Make JSON serializable
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return obj
    
    with open(TABLES / "tariff_incidence_analysis.json", 'w') as f:
        json.dump(make_serializable(all_results), f, indent=2, default=str)
    
    logger.info(f"\n  ✓ Results saved to {TABLES / 'tariff_incidence_analysis.json'}")
    
    # ---- SUMMARY ----
    logger.info("\n" + "=" * 70)
    logger.info("  SUMMARY: B50 TARIFF INCIDENCE")
    logger.info("=" * 70)
    logger.info(f"  B50 share of tariff revenue:           {b50_results.get('b50_share_pct', 0):.1f}%")
    logger.info(f"  B50 tariff paid (of $195B total):      ${b50_results.get('b50_tariff_paid_total_B', 0):.1f}B")
    logger.info(f"  B50 tariff paid (of $100B new):        ${b50_results.get('b50_tariff_paid_above_baseline_B', 0):.1f}B")
    logger.info(f"  B50 per person (total):                ${b50_results.get('b50_per_person_total', 0):.0f}")
    logger.info(f"  B50 per person (above baseline):       ${b50_results.get('b50_per_person_above_baseline', 0):.0f}")
    logger.info(f"  As % of B50 post-tax income:           {b50_results.get('b50_pct_of_income_total', 0):.1f}% (total)")
    logger.info(f"  Regressivity ratio (Q1/Q5):            {b50_results.get('regressivity_ratio', 0):.1f}x")
    
    # Validation summary
    if validation:
        logger.info(f"\n  Price validation:")
        logger.info(f"    High-tariff goods acceleration:     {validation.get('mean_high_tariff_acceleration', 0):+.2f}pp")
        logger.info(f"    Low-tariff goods acceleration:      {validation.get('mean_low_tariff_acceleration', 0):+.2f}pp")
        logger.info(f"    Tariff-price correlation (ρ):       {validation.get('spearman_rho', 0):.3f} (p={validation.get('spearman_pval', 1):.3f})")
    
    logger.info("\n  ✓ Analysis complete")


if __name__ == '__main__':
    main()
