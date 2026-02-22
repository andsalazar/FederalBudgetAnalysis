"""
=============================================================================
MASTER ANALYSIS SCRIPT
Federal Budget & Taxpayer Welfare — Hypothesis Testing
=============================================================================

Pre-registered hypothesis:
  H1:  The bottom 50% of taxpayers are worse off in 2025 due to federal
       economic policy.

Sub-hypotheses:
  H1a: Social program spending cuts reduce safety-net transfers.
  H1b: Tax burden shifted toward lower-income brackets.
  H1c: Tariffs act as a regressive tax, raising prices on essentials.
  H1d: Rising deficits/interest payments crowd out social spending &
       enrich bondholders.
  H1e: Corporate tax cuts & deregulation primarily benefit shareholders,
       widening wealth inequality.

Methodology:
  - Interrupted Time Series (ITS) around 2025 policy dates
  - Year-over-year (YoY) comparisons for annual CBO data
  - Structural break tests (Chow test)
  - Budget composition analysis (CBO fiscal tables)
  - All with pre-registered significance threshold α = 0.05
=============================================================================
"""

import sys, os, warnings
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from datetime import date
from loguru import logger

from src.utils.config import load_config, get_output_path, setup_logging
from src.database.models import get_session, EconomicSeries, Observation
from src.analysis.policy_impact import (
    load_series, load_multiple_series,
    interrupted_time_series, chow_test, test_stationarity,
    compute_real_values, percent_change_around_event,
)

setup_logging()
config = load_config()
OUTPUT = get_output_path()
FIGURES = get_output_path("figures")

# Ensure output dirs exist
os.makedirs(FIGURES, exist_ok=True)
os.makedirs(OUTPUT / "tables", exist_ok=True)

# ============================================================================
# HELPER: pull series, gracefully handle missing
# ============================================================================
session = get_session()

def get_series(sid, start='2000-01-01'):
    """Load a series from DB; return empty Series if missing."""
    s = load_series(sid, start_date=start)
    if s.empty:
        logger.warning(f"  Series {sid} not found or empty")
    return s

def get_latest(sid):
    """Return the latest observation value for a series."""
    obs = session.query(Observation).filter_by(series_id=sid).order_by(Observation.date.desc()).first()
    return (obs.value, obs.date) if obs else (None, None)

def get_yoy_change(sid, year_a=2024, year_b=2025):
    """Get year-over-year change between fiscal year end dates for CBO annual data."""
    obs_a = session.query(Observation).filter(
        Observation.series_id == sid,
        Observation.date >= date(year_a, 1, 1),
        Observation.date <= date(year_a, 12, 31)
    ).first()
    obs_b = session.query(Observation).filter(
        Observation.series_id == sid,
        Observation.date >= date(year_b, 1, 1),
        Observation.date <= date(year_b, 12, 31)
    ).first()
    if obs_a and obs_b:
        pct = ((obs_b.value - obs_a.value) / abs(obs_a.value)) * 100
        return {'year_a': year_a, 'val_a': obs_a.value,
                'year_b': year_b, 'val_b': obs_b.value,
                'change': obs_b.value - obs_a.value, 'pct_change': pct}
    return None

def section_header(title):
    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")


# ============================================================================
# H1a: SOCIAL PROGRAM SPENDING — Are transfers being cut?
# ============================================================================

def analyze_H1a():
    section_header("H1a: Social Program Spending & Safety-Net Transfers")
    results = {}

    # 1. CBO Budget: Mandatory spending composition
    print("\n--- CBO Mandatory Outlays (nominal $B) ---")
    mandatory_series = [
        ('CBO_MAND_Social_Security', 'Social Security'),
        ('CBO_MAND_Medicaid', 'Medicaid'),
        ('CBO_MAND_Income_securityᵇ', 'Income Security (SNAP, EITC, etc.)'),
        ('CBO_MAND_Veterans_programs', "Veterans' Programs"),
        ('CBO_MAND_Total', 'Total Mandatory'),
    ]

    for sid, label in mandatory_series:
        yoy = get_yoy_change(sid, 2023, 2024)
        if yoy:
            print(f"  {label:<40} FY{yoy['year_a']}: ${yoy['val_a']:>8.1f}B → "
                  f"FY{yoy['year_b']}: ${yoy['val_b']:>8.1f}B  ({yoy['pct_change']:+.1f}%)")
            results[f'cbo_{sid}_yoy'] = yoy

    # 2. Mandatory as % GDP
    print("\n--- Mandatory Outlays as % of GDP ---")
    gdp_series = [
        ('CBO_MAND_GDP_Social_Security', 'Social Security'),
        ('CBO_MAND_GDP_Medicaid', 'Medicaid'),
        ('CBO_MAND_GDP_Income_securityᵇ', 'Income Security'),
        ('CBO_MAND_GDP_Total', 'Total Mandatory'),
    ]
    for sid, label in gdp_series:
        yoy = get_yoy_change(sid, 2023, 2024)
        if yoy:
            print(f"  {label:<40} {yoy['val_a']:>5.1f}% → {yoy['val_b']:>5.1f}%  ({yoy['pct_change']:+.1f}%)")

    # 3. FRED quarterly social benefits
    print("\n--- FRED: Federal Social Benefits (quarterly, $B ann. rate) ---")
    fred_social = [
        ('W823RC1Q027SBEA', 'Federal Social Benefits'),
        ('TRP6001A027NBEA', 'Gov Social Benefits to Persons'),
        ('W729RC1Q027SBEA', 'Federal Grants-in-Aid to S&L'),
    ]
    for sid, label in fred_social:
        s = get_series(sid, '2022-01-01')
        if not s.empty:
            latest_val, latest_date = s.iloc[-1], s.index[-1]
            # Compare latest to same quarter last year
            try:
                prev_year = s.loc[s.index.year == latest_date.year - 1]
                if not prev_year.empty:
                    prev_val = prev_year.iloc[-1]
                    pct = ((latest_val - prev_val) / abs(prev_val)) * 100
                    print(f"  {label:<40} Latest: ${latest_val:>10,.0f}  YoY: {pct:+.1f}%")
                else:
                    print(f"  {label:<40} Latest: ${latest_val:>10,.0f}  (no prior year)")
            except:
                print(f"  {label:<40} Latest: ${latest_val:>10,.0f}")

    # 4. ITS on social benefits around inauguration
    print("\n--- ITS: Federal Social Benefits around 2025-01-20 ---")
    s = get_series('W823RC1Q027SBEA', '2020-01-01')
    if not s.empty and len(s) > 10:
        try:
            its = interrupted_time_series(s, '2025-01-20')
            print(f"  Intervention effect:  {its['intervention_effect']:>12,.1f}")
            print(f"  Trend change:         {its['trend_change']:>12.3f}")
            print(f"  R²:                   {its['r_squared']:>12.4f}")
            print(f"  Intervention p-value: {its['pvalues'].get('intervention', 'N/A')}")
            print(f"  Trend change p-value: {its['pvalues'].get('time_after', 'N/A')}")
            results['its_social_benefits'] = {
                'effect': its['intervention_effect'],
                'trend': its['trend_change'],
                'p_intervention': its['pvalues'].get('intervention'),
                'p_trend': its['pvalues'].get('time_after'),
                'r2': its['r_squared'],
            }
        except Exception as e:
            print(f"  ITS failed: {e}")

    return results


# ============================================================================
# H1b: TAX BURDEN DISTRIBUTION
# ============================================================================

def analyze_H1b():
    section_header("H1b: Tax Burden Distribution")
    results = {}

    # 1. CBO Revenue composition
    print("\n--- CBO Revenue by Source ($B) ---")
    rev_series = [
        ('CBO_REV_Individual_income_taxes', 'Individual Income Taxes'),
        ('CBO_REV_Corporate_income_taxes', 'Corporate Income Taxes'),
        ('CBO_REV_Payroll_taxes', 'Payroll Taxes (regressive)'),
        ('CBO_REV_Excise_taxes', 'Excise Taxes (regressive)'),
        ('CBO_REV_Customs_duties', 'Customs Duties (tariff revenue)'),
        ('CBO_REV_Total', 'Total Revenue'),
    ]
    for sid, label in rev_series:
        yoy = get_yoy_change(sid, 2023, 2024)
        if yoy:
            print(f"  {label:<40} FY{yoy['year_a']}: ${yoy['val_a']:>8.1f}B → "
                  f"FY{yoy['year_b']}: ${yoy['val_b']:>8.1f}B  ({yoy['pct_change']:+.1f}%)")
            results[f'rev_{sid}'] = yoy

    # 2. Revenue shares (% of GDP) — regressive vs progressive
    print("\n--- Revenue as % of GDP ---")
    gdp_rev = [
        ('CBO_REV_GDP_Individual_income_taxes', 'Individual Income Tax'),
        ('CBO_REV_GDP_Corporate_income_taxes', 'Corporate Income Tax'),
        ('CBO_REV_GDP_Payroll_taxes', 'Payroll Tax'),
        ('CBO_REV_GDP_Customs_duties', 'Customs Duties'),
    ]
    for sid, label in gdp_rev:
        yoy = get_yoy_change(sid, 2023, 2024)
        if yoy:
            print(f"  {label:<40} {yoy['val_a']:>5.1f}% → {yoy['val_b']:>5.1f}%  ({yoy['pct_change']:+.1f}%)")

    # 3. Regressive share
    print("\n--- Regressive Revenue Composition ---")
    total_yoy = get_yoy_change('CBO_REV_Total', 2023, 2024)
    payroll_yoy = get_yoy_change('CBO_REV_Payroll_taxes', 2023, 2024)
    excise_yoy = get_yoy_change('CBO_REV_Excise_taxes', 2023, 2024)
    customs_yoy = get_yoy_change('CBO_REV_Customs_duties', 2023, 2024)
    if all([total_yoy, payroll_yoy, excise_yoy, customs_yoy]):
        for year_key in ['year_a', 'year_b']:
            yr = total_yoy[year_key]
            val_key = 'val_a' if year_key == 'year_a' else 'val_b'
            regressive = payroll_yoy[val_key] + excise_yoy[val_key] + customs_yoy[val_key]
            share = (regressive / total_yoy[val_key]) * 100
            print(f"  FY{yr}: Regressive taxes = ${regressive:.1f}B ({share:.1f}% of total)")
            results[f'regressive_share_{yr}'] = share

    # 4. FRED: Gini coefficient trend
    print("\n--- Income Inequality (Gini) ---")
    gini = get_series('GINIALLRF', '2000-01-01')
    if not gini.empty:
        print(f"  Latest Gini: {gini.iloc[-1]:.4f} ({gini.index[-1].strftime('%Y-%m-%d')})")
        min_val = gini.min()
        max_val = gini.max()
        print(f"  Range (since 2000): {min_val:.4f} – {max_val:.4f}")
        results['gini_latest'] = gini.iloc[-1]

    return results


# ============================================================================
# H1c: TARIFFS AS REGRESSIVE TAX
# ============================================================================

def analyze_H1c():
    section_header("H1c: Tariffs as Regressive Tax — Consumer Price Impact")
    results = {}

    # 1. CPI sub-components — essentials vs luxuries
    print("\n--- CPI Category Trends (% change around tariffs) ---")
    tariff_date = '2025-02-04'  # First China tariff
    cpi_series = [
        ('CPIAUCSL', 'CPI: All Items'),
        ('CUSR0000SAF11', 'CPI: Food at Home'),
        ('CPIAPPSL', 'CPI: Apparel'),
        ('CUSR0000SAH1', 'CPI: Shelter'),
        ('CUSR0000SETB01', 'CPI: Gasoline'),
        ('CPIMEDSL', 'CPI: Medical Care'),
        ('CPIEDUSL', 'CPI: Education'),
    ]
    for sid, label in cpi_series:
        s = get_series(sid, '2023-01-01')
        if not s.empty and len(s) >= 12:
            try:
                result = percent_change_around_event(s, tariff_date, window_years=1)
                if 'error' not in result:
                    print(f"  {label:<35} Pre-tariff avg: {result['pre_mean']:>8.1f}  "
                          f"Post-tariff avg: {result['post_mean']:>8.1f}  Δ: {result['pct_change']:+.2f}%")
                    results[f'cpi_{sid}'] = result
                else:
                    # Use simple latest vs year-ago
                    latest = s.iloc[-1]
                    one_yr_ago = s.iloc[max(0, len(s) - 13)]
                    pct = ((latest - one_yr_ago) / abs(one_yr_ago)) * 100
                    print(f"  {label:<35} YoY: {pct:+.2f}% (latest: {latest:.1f})")
            except Exception as e:
                print(f"  {label:<35} Error: {e}")

    # 2. Import prices
    print("\n--- Import Prices & Trade Balance ---")
    for sid, label in [('IR', 'Import Price Index'), ('BOPGSTB', 'Trade Balance ($B)')]:
        s = get_series(sid, '2023-01-01')
        if not s.empty:
            latest = s.iloc[-1]
            prev = s.iloc[max(0, len(s) - 13)] if len(s) > 12 else s.iloc[0]
            pct = ((latest - prev) / abs(prev)) * 100 if prev != 0 else 0
            print(f"  {label:<35} Latest: {latest:>10.1f}  YoY: {pct:+.2f}%")

    # 3. ITS on CPI around reciprocal tariff date (April 2, 2025)
    print("\n--- ITS: CPI around Reciprocal Tariffs (2025-04-02) ---")
    cpi = get_series('CPIAUCSL', '2020-01-01')
    if not cpi.empty and len(cpi) > 20:
        try:
            its = interrupted_time_series(cpi, '2025-04-02')
            print(f"  Intervention effect:  {its['intervention_effect']:>12.3f}")
            print(f"  Trend change:         {its['trend_change']:>12.5f}")
            print(f"  R²:                   {its['r_squared']:>12.4f}")
            print(f"  Intervention p-value: {its['pvalues'].get('intervention', 'N/A')}")
            results['its_cpi'] = {
                'effect': its['intervention_effect'],
                'p_val': its['pvalues'].get('intervention'),
                'r2': its['r_squared'],
            }
        except Exception as e:
            print(f"  ITS failed: {e}")

    # 4. CBO: Customs revenue spike
    print("\n--- CBO: Customs Duty Revenue (tariff proceeds) ---")
    for yr in range(2020, 2025):
        yoy = get_yoy_change('CBO_REV_Customs_duties', yr, yr + 1)
        if yoy:
            print(f"  FY{yr}→{yr+1}: ${yoy['val_a']:.1f}B → ${yoy['val_b']:.1f}B ({yoy['pct_change']:+.1f}%)")

    return results


# ============================================================================
# H1d: DEFICIT & DEBT SERVICE — Crowding out & bondholder enrichment
# ============================================================================

def analyze_H1d():
    section_header("H1d: Deficit, Debt Service & Bondholder Enrichment")
    results = {}

    # 1. CBO Budget totals
    print("\n--- Federal Deficit & Interest Payments ---")
    for sid, label in [
        ('CBO_REVENUES', 'Total Revenues'),
        ('CBO_OUTLAYS', 'Total Outlays'),
        ('CBO_DEBT_HELD', 'Debt Held by Public'),
        ('CBO_OUT_Net_interest', 'Net Interest Payments'),
    ]:
        yoy = get_yoy_change(sid, 2023, 2024)
        if yoy:
            print(f"  {label:<30} FY{yoy['year_a']}: ${yoy['val_a']:>8.1f}B → "
                  f"FY{yoy['year_b']}: ${yoy['val_b']:>8.1f}B  ({yoy['pct_change']:+.1f}%)")
            results[f'{sid}_yoy'] = yoy

    # 2. Interest as % GDP (trend)
    print("\n--- Net Interest as % of GDP (trend, CBO) ---")
    for yr in range(2019, 2025):
        yoy = get_yoy_change('CBO_OUT_GDP_Net_interest', yr, yr + 1)
        if yoy:
            print(f"  FY{yr}→{yr+1}: {yoy['val_a']:.1f}% → {yoy['val_b']:.1f}%")

    # 3. Interest vs Social program spending comparison
    print("\n--- Interest vs Mandatory Social Spending (latest FY) ---")
    interest_latest = get_yoy_change('CBO_OUT_Net_interest', 2022, 2024)
    social_sec = get_yoy_change('CBO_MAND_Social_Security', 2022, 2024)
    medicaid = get_yoy_change('CBO_MAND_Medicaid', 2022, 2024)
    income_sec = get_yoy_change('CBO_MAND_Income_securityᵇ', 2022, 2024)

    if all([interest_latest, social_sec, medicaid, income_sec]):
        int_val = interest_latest['val_b']
        ss_val = social_sec['val_b']
        med_val = medicaid['val_b']
        inc_val = income_sec['val_b']
        print(f"  Net Interest:    ${int_val:>8.1f}B")
        print(f"  Social Security: ${ss_val:>8.1f}B")
        print(f"  Medicaid:        ${med_val:>8.1f}B")
        print(f"  Income Security: ${inc_val:>8.1f}B")
        print(f"  Interest / (Medicaid + Income Sec): {int_val / (med_val + inc_val) * 100:.1f}%")
        results['interest_vs_safety_net'] = int_val / (med_val + inc_val)

    # 4. FRED: Treasury yields (higher = more paid to bondholders)
    print("\n--- Treasury Yields ---")
    for sid, label in [('DGS10', '10-Year'), ('DGS2', '2-Year'), ('DGS30', '30-Year')]:
        s = get_series(sid, '2024-01-01')
        if not s.empty:
            latest = s.iloc[-1]
            yr_ago = s.iloc[0] if len(s) > 0 else None
            if yr_ago:
                print(f"  {label} Treasury: {latest:.2f}% (Jan 2024: {yr_ago:.2f}%, Δ: {latest - yr_ago:+.2f}pp)")

    # 5. ITS on deficit
    print("\n--- ITS: Federal Deficit around 2025-01-20 ---")
    deficit = get_series('FYFSD', '2010-01-01')
    if not deficit.empty and len(deficit) > 5:
        try:
            its = interrupted_time_series(deficit, '2025-01-20')
            print(f"  Intervention effect:  {its['intervention_effect']:>12,.1f}")
            print(f"  Trend change:         {its['trend_change']:>12.3f}")
            print(f"  Intervention p-value: {its['pvalues'].get('intervention', 'N/A')}")
            results['its_deficit'] = {
                'effect': its['intervention_effect'],
                'p_val': its['pvalues'].get('intervention'),
            }
        except Exception as e:
            print(f"  ITS failed: {e}")

    return results


# ============================================================================
# H1e: CORPORATE / SHAREHOLDER BENEFITS
# ============================================================================

def analyze_H1e():
    section_header("H1e: Corporate & Shareholder Benefits")
    results = {}

    # 1. CBO: Corporate tax revenue trend
    print("\n--- CBO: Corporate vs Individual Tax Revenue ---")
    for yr in range(2020, 2025):
        corp = get_yoy_change('CBO_REV_Corporate_income_taxes', yr, yr + 1)
        indiv = get_yoy_change('CBO_REV_Individual_income_taxes', yr, yr + 1)
        if corp and indiv:
            ratio = corp['val_b'] / indiv['val_b'] * 100
            print(f"  FY{yr+1}: Corp ${corp['val_b']:.0f}B / Indiv ${indiv['val_b']:.0f}B "
                  f"(ratio: {ratio:.1f}%)")
            results[f'corp_indiv_ratio_{yr+1}'] = ratio

    # 2. FRED: Corporate profits vs wages
    print("\n--- Corporate Profits vs Wages ---")
    for sid, label in [
        ('CP', 'Corporate Profits After Tax'),
        ('CPATAX', 'Corp Profits (with adj.)'),
        ('SP500', 'S&P 500 Index'),
    ]:
        s = get_series(sid, '2023-01-01')
        if not s.empty:
            latest = s.iloc[-1]
            first = s.iloc[0]
            pct = ((latest - first) / abs(first)) * 100
            print(f"  {label:<35} Jan 2023: {first:>10,.1f} → Latest: {latest:>10,.1f} ({pct:+.1f}%)")

    # 3. CBO projections: wages vs profits vs dividends
    print("\n--- CBO Economic: Wages vs Profits vs Dividends ---")
    for sid, label in [
        ('CBO_WAGES', 'Wages & Salaries'),
        ('CBO_CORP_PROFITS', 'Corporate Profits'),
        ('CBO_DIVIDEND_INCOME', 'Dividend Income'),
        ('CBO_INTEREST_INCOME', 'Interest Income'),
    ]:
        yoy = get_yoy_change(sid, 2023, 2024)
        if yoy:
            print(f"  {label:<25} {yoy['year_a']}: ${yoy['val_a']:>8.1f}B → "
                  f"{yoy['year_b']}: ${yoy['val_b']:>8.1f}B  ({yoy['pct_change']:+.1f}%)")

    # 4. Market value of equities
    print("\n--- Market Value of Corporate Equities ---")
    s = get_series('NCBCMDPMVCE', '2020-01-01')
    if not s.empty:
        print(f"  Latest: ${s.iloc[-1]:,.0f}B ({s.index[-1].strftime('%Y-%m-%d')})")
        if len(s) > 4:
            pct = ((s.iloc[-1] - s.iloc[0]) / abs(s.iloc[0])) * 100
            print(f"  Change since {s.index[0].strftime('%Y')}: {pct:+.1f}%")

    return results


# ============================================================================
# BUDGET FLOW: Where did the money go?
# ============================================================================

def analyze_budget_flow():
    section_header("BUDGET FLOW ANALYSIS: Where Did the Money Go?")
    results = {}

    # CBO outlay composition (latest 5 fiscal years)
    print("\n--- Federal Outlay Composition ($B, FY2020–FY2024) ---")
    components = [
        ('CBO_OUT_Discretionary', 'Discretionary'),
        ('CBO_MAND_Social_Security', 'Social Security'),
        ('CBO_MAND_Medicaid', 'Medicaid'),
        ('CBO_MAND_Income_securityᵇ', 'Income Security'),
        ('CBO_MAND_Veterans_programs', 'Veterans'),
        ('CBO_OUT_Net_interest', 'Net Interest'),
    ]

    print(f"  {'Category':<25}", end='')
    for yr in range(2020, 2025):
        print(f"  FY{yr:>5}", end='')
    print(f"  {'Δ20→24':>8}")
    print(f"  {'-'*25}" + f"  {'-----':>6}" * 5 + f"  {'--------':>8}")

    for sid, label in components:
        print(f"  {label:<25}", end='')
        vals = []
        for yr in range(2020, 2025):
            obs = session.query(Observation).filter(
                Observation.series_id == sid,
                Observation.date >= date(yr, 1, 1),
                Observation.date <= date(yr, 12, 31)
            ).first()
            if obs:
                vals.append(obs.value)
                print(f"  ${obs.value:>5.0f}", end='')
            else:
                vals.append(None)
                print(f"  {'N/A':>6}", end='')
        if vals[0] and vals[-1]:
            delta = vals[-1] - vals[0]
            print(f"  {delta:>+8.0f}")
            results[f'flow_{sid}'] = {'FY2020': vals[0], 'FY2024': vals[-1], 'change': delta}
        else:
            print()

    # Who gained most?
    print("\n--- Biggest $ Increases (FY2020 → FY2024) ---")
    changes = []
    for sid, label in components:
        obs20 = session.query(Observation).filter(
            Observation.series_id == sid,
            Observation.date >= date(2020, 1, 1),
            Observation.date <= date(2020, 12, 31)
        ).first()
        obs24 = session.query(Observation).filter(
            Observation.series_id == sid,
            Observation.date >= date(2024, 1, 1),
            Observation.date <= date(2024, 12, 31)
        ).first()
        if obs20 and obs24:
            changes.append((label, obs24.value - obs20.value, obs20.value, obs24.value))
    
    changes.sort(key=lambda x: x[1], reverse=True)
    for label, delta, v20, v24 in changes:
        pct = (delta / abs(v20)) * 100 if v20 else 0
        print(f"  {label:<25} {delta:>+8.0f}B ({pct:>+.0f}%)")

    # Revenue vs Outlays gap
    print("\n--- Revenue vs Outlays Gap ---")
    for yr in range(2020, 2025):
        rev = session.query(Observation).filter(
            Observation.series_id == 'CBO_REVENUES',
            Observation.date >= date(yr, 1, 1),
            Observation.date <= date(yr, 12, 31)
        ).first()
        out = session.query(Observation).filter(
            Observation.series_id == 'CBO_OUTLAYS',
            Observation.date >= date(yr, 1, 1),
            Observation.date <= date(yr, 12, 31)
        ).first()
        if rev and out:
            gap = rev.value - out.value
            print(f"  FY{yr}: Revenue ${rev.value:.0f}B - Outlays ${out.value:.0f}B = ${gap:.0f}B")

    return results


# ============================================================================
# SYNTHESIS: Evidence summary
# ============================================================================

def synthesize(all_results):
    section_header("SYNTHESIS: Hypothesis Assessment")
    
    print("""
  Master Hypothesis: "The bottom 50% of taxpayers are worse off in 2025
                      due to federal economic policy."

  Evidence Assessment by Sub-Hypothesis:
  ─────────────────────────────────────────────────────────────────────
    """)

    # H1a assessment
    print("  H1a (Social program cuts reduce safety net):")
    if 'H1a' in all_results:
        its = all_results['H1a'].get('its_social_benefits', {})
        if its:
            p = its.get('p_intervention', 1.0)
            effect = its.get('effect', 0)
            sig = "SIGNIFICANT" if p and p < 0.05 else "NOT SIGNIFICANT"
            direction = "DECLINE" if effect and effect < 0 else "INCREASE" if effect and effect > 0 else "UNCLEAR"
            print(f"    ITS intervention effect: {effect:+,.1f}  (p={p:.4f}) — {sig}")
            print(f"    Direction: {direction}")
        else:
            print("    ITS: Insufficient post-intervention data for significance test")
    print()

    # H1b assessment
    print("  H1b (Tax burden shifted to lower brackets):")
    if 'H1b' in all_results:
        ra = all_results['H1b'].get('regressive_share_2024')
        rb = all_results['H1b'].get('regressive_share_2023')
        if ra and rb:
            print(f"    Regressive tax share: {rb:.1f}% (FY2023) → {ra:.1f}% (FY2024)")
            if ra > rb:
                print(f"    Direction: REGRESSIVE SHIFT (+{ra - rb:.1f}pp)")
            else:
                print(f"    Direction: Progressive shift ({ra - rb:+.1f}pp)")
    print()

    # H1c assessment
    print("  H1c (Tariffs raise prices on essentials):")
    if 'H1c' in all_results:
        cpi_all = all_results['H1c'].get('cpi_CPIAUCSL', {})
        cpi_food = all_results['H1c'].get('cpi_CUSR0000SAF11', {})
        if cpi_all and cpi_food:
            food_pct = cpi_food.get('pct_change', 0)
            all_pct = cpi_all.get('pct_change', 0)
            print(f"    CPI All Items:     {all_pct:+.2f}%")
            print(f"    CPI Food at Home:  {food_pct:+.2f}%")
            if food_pct > all_pct:
                print(f"    Food prices rising FASTER than overall — regressive impact confirmed")
    print()

    # H1d assessment
    print("  H1d (Deficit/interest payments crowd out & enrich bondholders):")
    if 'H1d' in all_results:
        ratio = all_results['H1d'].get('interest_vs_safety_net')
        if ratio:
            print(f"    Interest / (Medicaid + Income Security): {ratio * 100:.1f}%")
            if ratio > 0.5:
                print(f"    Interest payments now exceed half of safety-net spending")
    print()

    # H1e assessment
    print("  H1e (Corporate/shareholder benefits widen inequality):")
    if 'H1e' in all_results:
        for yr in range(2021, 2025):
            r = all_results['H1e'].get(f'corp_indiv_ratio_{yr}')
            if r:
                print(f"    FY{yr} Corp/Indiv tax ratio: {r:.1f}%")
    print()

    print("  ─────────────────────────────────────────────────────────────────────")
    print("  NOTE: This is a preliminary descriptive analysis. Causal claims")
    print("  require further econometric work (diff-in-diff, synthetic controls).")
    print("  2025 data is still accumulating; revisit when full FY2025 is available.")
    print("  ─────────────────────────────────────────────────────────────────────")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "█" * 72)
    print("  FEDERAL BUDGET & TAXPAYER WELFARE — HYPOTHESIS TESTING")
    print("  Pre-registered analysis run: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'))
    print("█" * 72)

    all_results = {}
    all_results['H1a'] = analyze_H1a()
    all_results['H1b'] = analyze_H1b()
    all_results['H1c'] = analyze_H1c()
    all_results['H1d'] = analyze_H1d()
    all_results['H1e'] = analyze_H1e()
    all_results['flow'] = analyze_budget_flow()
    
    synthesize(all_results)

    # Save raw results
    import json

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return super().default(obj)

    results_path = OUTPUT / "tables" / "hypothesis_results.json"
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2, cls=NumpyEncoder, default=str)
    print(f"\n  Results saved to {results_path}")

    session.close()
    print("\nDone.")
