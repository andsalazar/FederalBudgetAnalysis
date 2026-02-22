"""
=============================================================================
SCOTUS TARIFF REVOCATION + 15% REPLACEMENT TARIFF: WELFARE SCENARIO ANALYSIS
=============================================================================

Models the distributional welfare effects of two simultaneous developments:

  1. Supreme Court (Learning Resources, Inc. v. Trump, No. 24-1287, Feb. 20,
     2026, 6-3) holds IEEPA does not authorize tariffs → IEEPA collections
     (~$133B+, AP) refunded to importers via debt, increasing net interest
     payments that flow disproportionately to top-decile bondholders.
     Under price stickiness, consumers see NO relief — the tariff wedge
     shifts from Treasury to corporate margins.

  2. Administration announces 15% universal tariff — initially via Section 122
     EO (150-day limit), with Congressional legislation needed for permanence.

Framework: Uses this paper's established incidence parameters:
  - CEX 2023 quintile spending shares for tariff burden allocation
  - CPS ASEC 2024 person-income quintiles for B50 definition
  - 1.4× DWL multiplier (Amiti et al. 2019)
  - Spending-cut channel unchanged (same CBO baseline gap)
  - Interest-rate assumptions from Treasury yield curve

Key assumptions clearly flagged for transparency.

References:
  - Amiti, Redding & Weinstein (2019) — tariff pass-through
  - Fajgelbaum et al. (2020) — distributional effects
  - CBO (Jan 2025) — baseline projections
  - Federal Reserve 2023 SCF — bond/equity ownership distribution
  - Peltzman (2000) — asymmetric price adjustment
  - Gopinath, Itskhoki & Rigobon (2010) — pass-through timing
=============================================================================
"""

import sys
import os
import json
import warnings

sys.path.insert(0, '.')
warnings.filterwarnings('ignore')

import numpy as np
from loguru import logger
from pathlib import Path

TABLES = Path("output/tables")
TABLES.mkdir(parents=True, exist_ok=True)


# ============================================================================
# PAPER'S ESTABLISHED PARAMETERS
# ============================================================================

# B50 population (CPS person-income quintiles: Q1+Q2+0.5*Q3)
B50_POP = 136_571_242
TOTAL_POP = 273_144_712
B50_MEAN_PRETAX_INCOME = 12_526  # $ per person (CPS ASEC 2024)

# CPS quintile populations (each ~20% of persons)
QUINTILE_POP = {
    'Q1': 54_627_029,
    'Q2': 54_627_275,
    'Q3': 54_633_875,
    'Q4': 54_629_132,
    'Q5': 54_627_400,
}

# Quintile mean pretax incomes (CPS ASEC 2024, person-level)
QUINTILE_MEAN_INCOME = {
    'Q1': 396,
    'Q2': 15_826,
    'Q3': 35_619,
    'Q4': 51_972,
    'Q5': 129_167,
}

# CEX 2023 tariff-weighted spending shares by quintile (from b50_tariff_share)
# These are the shares of tariff-weighted consumer spending by quintile
CEX_TARIFF_SHARES = {
    'Q1': 0.10398,
    'Q2': 0.13948,
    'Q3': 0.17805,
    'Q4': 0.23124,
    'Q5': 0.34726,
}

# B50 share via CEX calibration
B50_CEX_TARIFF_SHARE = 0.5172  # 51.7% (Q1+Q2+Q3+0.414*Q4)

# CPS person-quintile B50 tariff share (Q1+Q2+0.5*Q3)
B50_CPS_TARIFF_SHARE = (CEX_TARIFF_SHARES['Q1'] + CEX_TARIFF_SHARES['Q2'] +
                        0.5 * CEX_TARIFF_SHARES['Q3'])

# Paper's established spending-cut burden by quintile ($B)
SPENDING_CUTS_BY_QUINTILE = {
    'Q1': -64.65,
    'Q2': -50.45,
    'Q3': -32.66,
    'Q4': -23.88,
    'Q5': -12.36,
}

# DWL multiplier from Amiti et al. (2019)
DWL_FACTOR = 1.4

# Federal Reserve 2023 SCF: bond ownership concentration
TOP_DECILE_BOND_SHARE = 0.67  # 67% of bonds and fixed-income securities
TOP_10PCT_EQUITY_SHARE = 0.93  # 93% of equities

# Current FY2025 parameters
FY2025_NET_INTEREST = 980  # $B
FY2025_CUSTOMS_ACTUAL = 195  # $B
CBO_BASELINE_CUSTOMS = 95  # $B  (pre-executive-tariff baseline)
ABOVE_BASELINE_CUSTOMS = 100  # $B


# ============================================================================
# SCENARIO PARAMETERS
# ============================================================================

# --- Scenario 1: SCOTUS revocation + debt-financed refund ---
# Learning Resources, Inc. v. Trump, No. 24-1287 (S. Ct. Feb. 20, 2026)
# AP reports Treasury collected >$133B under IEEPA authority as of Dec 2025
REFUND_AMOUNT_B = 133  # $B — IEEPA-specific collections (AP, Price, Feb 21, 2026)
# Interest rate on new debt issuance (10-year Treasury ~4.5%, Feb 2026)
NEW_DEBT_INTEREST_RATE = 0.045
# Refund reduces current-year customs to baseline level
POST_REVOCATION_CUSTOMS_B = CBO_BASELINE_CUSTOMS  # $95B

# --- Scenario 2: 15% universal legislative tariff ---
# U.S. total goods imports 2024: ~$3,100B (Census Bureau)
# Source: Census Bureau Foreign Trade, 2024 annual goods imports = $3,267B
# (https://www.census.gov/foreign-trade/statistics/highlights/annual.html)
TOTAL_GOODS_IMPORTS_B = 3_100  # Conservative round number

# 15% universal tariff — but need to account for:
# (a) Pre-existing tariffs (MFN average ~2.5%, Section 301 ~7.5% on China)
# (b) FTA imports (USMCA, etc.) that may be exempt or subject to different rates
# (c) Trade elasticity — higher tariffs reduce import volumes
# We model three scenarios: low/central/high effective revenue

LEGISLATIVE_TARIFF_RATE = 0.15  # 15% universal

# FTA-exempt imports: ~45% of US goods imports are from USMCA/FTA partners
# If legislation overrides FTAs: full base applies
# If FTAs honored: ~55% of imports subject = ~$1,700B base
# Trade elasticity: import demand elasticity ≈ -1.5 (Broda & Weinstein 2006)
# 15% tariff → ~12% volume reduction (mid-range, elasticity × rate / (1+rate))

# Central scenario: 15% on full import base with ~10% trade reduction
IMPORT_ELASTICITY = -1.0  # Conservative (Fajgelbaum et al. 2020 estimate -1 to -2)
TRADE_VOLUME_REDUCTION = abs(IMPORT_ELASTICITY) * LEGISLATIVE_TARIFF_RATE / (1 + LEGISLATIVE_TARIFF_RATE)

# Revenue scenarios
def compute_tariff_revenue(import_base_B, tariff_rate, trade_reduction_pct):
    """
    Compute tariff revenue accounting for trade volume effects.
    Revenue = rate × (base × (1 - trade_reduction))
    """
    adjusted_base = import_base_B * (1 - trade_reduction_pct)
    return tariff_rate * adjusted_base


# ============================================================================
# SCENARIO MODELING
# ============================================================================

def model_refund_scenario():
    """
    Model the fiscal impact of debt-financed tariff refunds.
    
    The executive tariffs collected ~$100B above baseline. If SCOTUS orders
    refunds, this money has already been spent in a deficit context, so refunds
    must be debt-financed. This creates additional interest obligations that
    flow to bondholders (concentrated in top decile).
    
    Net effect on B50:
    - RELIEF: Executive tariff consumer burden eliminated ($50.4B B50 burden removed)
    - COST: Spending cuts remain (unchanged $131.4B)
    - COST: Additional debt service from refund financing
    - COST: Loss of tariff revenue → wider deficit → more future interest
    """
    logger.info("=" * 70)
    logger.info("SCENARIO 1: SCOTUS TARIFF REVOCATION + DEBT-FINANCED REFUND")
    logger.info("=" * 70)
    
    # --- Immediate relief: executive tariff consumer burden eliminated ---
    # The $100B above-baseline tariff revenue × 1.4 DWL = $140B consumer burden is removed
    tariff_burden_removed_total = ABOVE_BASELINE_CUSTOMS * DWL_FACTOR  # $140B
    
    # B50's share of that relief (CPS person-quintile)
    b50_tariff_relief = tariff_burden_removed_total * B50_CPS_TARIFF_SHARE
    
    # Per-quintile relief
    relief_by_quintile = {}
    for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
        relief_by_quintile[q] = tariff_burden_removed_total * CEX_TARIFF_SHARES[q]
    
    logger.info(f"\n  TARIFF CONSUMER BURDEN REMOVED:")
    logger.info(f"    Total consumer burden eliminated: ${tariff_burden_removed_total:.1f}B")
    logger.info(f"    B50 relief (CPS Q1+Q2+0.5×Q3): ${b50_tariff_relief:.1f}B")
    for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
        per_p = (relief_by_quintile[q] * 1e9) / QUINTILE_POP[q]
        logger.info(f"    {q}: +${relief_by_quintile[q]:.1f}B (${per_p:.0f}/person)")
    
    # --- Cost: Debt-financed refund increases interest payments ---
    # Refund = $100B → new debt → annual interest cost
    annual_interest_on_refund = REFUND_AMOUNT_B * NEW_DEBT_INTEREST_RATE
    
    # Interest flows primarily to top decile (67% bonds per SCF)
    # B50 effectively bears none of the interest income (they hold negligible bonds)
    # But B50 bears a share of the *fiscal cost* via future spending cuts / revenue needs
    # For this exercise: interest is a fiscal transfer TO bondholders
    
    logger.info(f"\n  DEBT-FINANCED REFUND COSTS:")
    logger.info(f"    Refund amount: ${REFUND_AMOUNT_B}B (debt-financed)")
    logger.info(f"    Annual interest on new debt: ${annual_interest_on_refund:.1f}B ({NEW_DEBT_INTEREST_RATE*100:.1f}%)")
    logger.info(f"    Of which flows to top decile: ${annual_interest_on_refund * TOP_DECILE_BOND_SHARE:.1f}B ({TOP_DECILE_BOND_SHARE*100:.0f}%)")
    
    # --- Cost: Revenue shortfall widens deficit ---
    # Without replacement tariff, customs drop to $95B (baseline)
    # Revenue gap vs FY2025 actual: $100B/year
    # This either requires spending cuts (hits B50) or more borrowing (hits future B50)
    revenue_gap = ABOVE_BASELINE_CUSTOMS  # $100B/year ongoing
    
    logger.info(f"\n  STRUCTURAL REVENUE GAP:")
    logger.info(f"    Annual customs revenue loss: ${revenue_gap}B")
    logger.info(f"    This gap must be offset by: spending cuts, other revenue, or deficit")
    
    # --- Net B50 impact under revocation-only ---
    # Spending cuts: unchanged at $131.4B
    b50_spending_cuts = abs(sum(SPENDING_CUTS_BY_QUINTILE[q] for q in ['Q1', 'Q2'])
                           + 0.5 * SPENDING_CUTS_BY_QUINTILE['Q3'])
    
    # Tariff burden: eliminated ($0)
    b50_tariff_burden_post = 0
    
    # Net interest impact on B50: minimal direct effect 
    # (B50 holds negligible bonds; interest goes to top decile)
    # But future fiscal adjustment will eventually hit B50
    
    b50_combined_post = b50_spending_cuts + b50_tariff_burden_post
    b50_per_person_post = (b50_combined_post * 1e9) / B50_POP
    b50_pct_income_post = (b50_per_person_post / B50_MEAN_PRETAX_INCOME) * 100
    
    logger.info(f"\n  NET B50 IMPACT (REVOCATION ONLY, NO REPLACEMENT):")
    logger.info(f"    Spending cuts (unchanged): ${b50_spending_cuts:.1f}B")
    logger.info(f"    Tariff burden (eliminated): $0.0B")
    logger.info(f"    Combined: ${b50_combined_post:.1f}B")
    logger.info(f"    Per person: ${b50_per_person_post:.0f}")
    logger.info(f"    As % of pretax income: {b50_pct_income_post:.1f}%")
    
    # Comparison with status quo
    b50_status_quo = 181.8
    b50_per_person_sq = 1331
    b50_pct_sq = 10.6
    
    logger.info(f"\n  COMPARISON WITH FY2025 STATUS QUO:")
    logger.info(f"    Status quo B50 burden: ${b50_status_quo}B (${b50_per_person_sq}/person, {b50_pct_sq}%)")
    logger.info(f"    Post-revocation:       ${b50_combined_post:.1f}B (${b50_per_person_post:.0f}/person, {b50_pct_income_post:.1f}%)")
    logger.info(f"    B50 relief:            ${b50_status_quo - b50_combined_post:.1f}B (${b50_per_person_sq - b50_per_person_post:.0f}/person)")
    
    return {
        'tariff_burden_removed_total_B': tariff_burden_removed_total,
        'b50_tariff_relief_B': b50_tariff_relief,
        'refund_amount_B': REFUND_AMOUNT_B,
        'annual_interest_on_refund_B': annual_interest_on_refund,
        'interest_to_top_decile_B': annual_interest_on_refund * TOP_DECILE_BOND_SHARE,
        'revenue_gap_B': revenue_gap,
        'b50_spending_cuts_B': b50_spending_cuts,
        'b50_combined_post_revocation_B': b50_combined_post,
        'b50_per_person_post': b50_per_person_post,
        'b50_pct_income_post': b50_pct_income_post,
        'relief_by_quintile_B': relief_by_quintile,
    }


def model_legislative_tariff():
    """
    Model the distributional impact of a 15% universal legislative tariff.
    
    Key differences from executive tariffs:
    - Legal basis: Congressional statute (immune to SCOTUS challenge)
    - Rate: 15% universal (vs. variable 10-145% executive rates)
    - Scope: All goods imports (no country-specific exceptions)
    - Revenue: Substantially higher base × lower rate
    
    Three revenue scenarios based on trade elasticity uncertainty.
    """
    logger.info("\n" + "=" * 70)
    logger.info("SCENARIO 2: 15% UNIVERSAL LEGISLATIVE TARIFF")
    logger.info("=" * 70)
    
    # --- Revenue estimation ---
    scenarios = {
        'Low': {
            'label': 'Low (FTA-exempt, high elasticity)',
            'import_base_B': TOTAL_GOODS_IMPORTS_B * 0.55,  # Only non-FTA imports
            'trade_reduction': 0.15,  # Higher trade response
        },
        'Central': {
            'label': 'Central (full base, moderate elasticity)',
            'import_base_B': TOTAL_GOODS_IMPORTS_B,
            'trade_reduction': TRADE_VOLUME_REDUCTION,
        },
        'High': {
            'label': 'High (full base, low elasticity)',
            'import_base_B': TOTAL_GOODS_IMPORTS_B,
            'trade_reduction': 0.05,  # Minimal trade diversion
        },
    }
    
    logger.info(f"\n  IMPORT BASE: ${TOTAL_GOODS_IMPORTS_B:,}B (Census Bureau 2024)")
    logger.info(f"  Tariff rate: {LEGISLATIVE_TARIFF_RATE*100:.0f}% universal")
    logger.info(f"  Import demand elasticity: {IMPORT_ELASTICITY}")
    logger.info(f"  Central trade reduction: {TRADE_VOLUME_REDUCTION*100:.1f}%")
    
    results = {}
    for name, params in scenarios.items():
        revenue = compute_tariff_revenue(
            params['import_base_B'], LEGISLATIVE_TARIFF_RATE, params['trade_reduction']
        )
        above_baseline = revenue - CBO_BASELINE_CUSTOMS
        consumer_burden = revenue * DWL_FACTOR  # DWL-inclusive
        
        # B50 burden allocation (CPS person-quintile)
        b50_tariff_burden = consumer_burden * B50_CPS_TARIFF_SHARE
        
        # Per-quintile
        quintile_burden = {}
        for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
            quintile_burden[q] = consumer_burden * CEX_TARIFF_SHARES[q]
        
        results[name] = {
            'label': params['label'],
            'import_base_B': params['import_base_B'],
            'trade_reduction_pct': params['trade_reduction'],
            'tariff_revenue_B': revenue,
            'above_baseline_B': above_baseline,
            'consumer_burden_B': consumer_burden,
            'b50_tariff_burden_B': b50_tariff_burden,
            'quintile_burden_B': quintile_burden,
        }
        
        logger.info(f"\n  {params['label'].upper()}:")
        logger.info(f"    Import base: ${params['import_base_B']:.0f}B")
        logger.info(f"    Trade reduction: {params['trade_reduction']*100:.1f}%")
        logger.info(f"    Tariff revenue: ${revenue:.1f}B")
        logger.info(f"    Above CBO baseline: ${above_baseline:.1f}B")
        logger.info(f"    Consumer burden (×{DWL_FACTOR}): ${consumer_burden:.1f}B")
        logger.info(f"    B50 tariff burden: ${b50_tariff_burden:.1f}B")
    
    return results


def model_combined_scenario():
    """
    Model the combined impact: SCOTUS revocation + 15% legislative replacement.
    
    Timeline:
    1. SCOTUS revokes executive tariffs → immediate consumer relief
    2. Government issues $100B in debt to finance refunds
    3. Congress passes 15% universal tariff → new consumer burden
    4. Spending cuts remain (unchanged from FY2025 CBO gap)
    
    Net effect: different tariff structure, different revenue, different distribution.
    """
    logger.info("\n" + "=" * 70)
    logger.info("COMBINED SCENARIO: REVOCATION + 15% LEGISLATIVE REPLACEMENT")
    logger.info("=" * 70)
    
    refund = model_refund_scenario()
    legislative = model_legislative_tariff()
    
    # --- Combined analysis for each revenue scenario ---
    logger.info("\n" + "=" * 70)
    logger.info("COMBINED WELFARE ANALYSIS (ALL SCENARIOS)")
    logger.info("=" * 70)
    
    b50_spending_cuts = refund['b50_spending_cuts_B']
    
    combined_results = {}
    for name, leg_result in legislative.items():
        b50_new_tariff = leg_result['b50_tariff_burden_B']
        b50_combined = b50_spending_cuts + b50_new_tariff
        per_person = (b50_combined * 1e9) / B50_POP
        pct_income = (per_person / B50_MEAN_PRETAX_INCOME) * 100
        
        # Revenue comparison
        new_revenue = leg_result['tariff_revenue_B']
        revenue_vs_fy25 = new_revenue - FY2025_CUSTOMS_ACTUAL
        
        # Fiscal position: refund cost + new revenue vs old revenue
        annual_interest_cost = refund['annual_interest_on_refund_B']
        net_fiscal_annual = new_revenue - FY2025_CUSTOMS_ACTUAL - annual_interest_cost
        
        # Quintile-level analysis
        quintile_results = {}
        for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
            spend_cut = abs(SPENDING_CUTS_BY_QUINTILE[q])
            new_tariff = leg_result['quintile_burden_B'][q]
            total = spend_cut + new_tariff
            pop = QUINTILE_POP[q]
            pp = (total * 1e9) / pop
            pct = (pp / QUINTILE_MEAN_INCOME[q]) * 100 if QUINTILE_MEAN_INCOME[q] > 0 else float('inf')
            quintile_results[q] = {
                'spending_cut_B': spend_cut,
                'tariff_burden_B': new_tariff,
                'total_B': total,
                'per_person': pp,
                'pct_income': pct,
            }
        
        combined_results[name] = {
            'scenario': leg_result['label'],
            'tariff_revenue_B': new_revenue,
            'consumer_burden_B': leg_result['consumer_burden_B'],
            'revenue_vs_fy25_B': revenue_vs_fy25,
            'annual_interest_cost_B': annual_interest_cost,
            'net_fiscal_change_B': net_fiscal_annual,
            'b50_spending_cuts_B': b50_spending_cuts,
            'b50_tariff_burden_B': b50_new_tariff,
            'b50_combined_B': b50_combined,
            'b50_per_person': per_person,
            'b50_pct_income': pct_income,
            'quintile_detail': quintile_results,
        }
        
        logger.info(f"\n  --- {leg_result['label'].upper()} ---")
        logger.info(f"  Tariff revenue: ${new_revenue:.1f}B (vs. ${FY2025_CUSTOMS_ACTUAL}B FY2025)")
        logger.info(f"  Consumer burden: ${leg_result['consumer_burden_B']:.1f}B")
        logger.info(f"  Revenue change vs FY2025: {'+'if revenue_vs_fy25>0 else ''}{revenue_vs_fy25:.1f}B")
        logger.info(f"  Annual refund interest cost: ${annual_interest_cost:.1f}B")
        logger.info(f"  Net fiscal change (annual): {'+'if net_fiscal_annual>0 else ''}{net_fiscal_annual:.1f}B")
        
        logger.info(f"\n  B50 BURDEN:")
        logger.info(f"    Spending cuts (unchanged): ${b50_spending_cuts:.1f}B")
        logger.info(f"    New tariff burden: ${b50_new_tariff:.1f}B")
        logger.info(f"    Combined: ${b50_combined:.1f}B")
        logger.info(f"    Per person: ${per_person:.0f}")
        logger.info(f"    % of pretax income: {pct_income:.1f}%")
        
        logger.info(f"\n  QUINTILE DETAIL:")
        for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
            r = quintile_results[q]
            logger.info(f"    {q}: SpendCut ${r['spending_cut_B']:.1f}B + "
                       f"Tariff ${r['tariff_burden_B']:.1f}B = "
                       f"${r['total_B']:.1f}B (${r['per_person']:.0f}/person, "
                       f"{r['pct_income']:.1f}% of income)")
    
    # --- Status quo comparison ---
    logger.info("\n" + "=" * 70)
    logger.info("STATUS QUO vs SCENARIO COMPARISON")
    logger.info("=" * 70)
    
    status_quo = {
        'tariff_revenue_B': 195,
        'consumer_burden_B': 140,
        'b50_combined_B': 181.8,
        'b50_per_person': 1331,
        'b50_pct_income': 10.6,
    }
    
    logger.info(f"\n  {'Metric':<35} {'Status Quo':>12} {'Low':>12} {'Central':>12} {'High':>12}")
    logger.info(f"  {'-'*35} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")
    
    metrics = [
        ('Tariff revenue ($B)', 'tariff_revenue_B', '${:.0f}B'),
        ('Consumer burden ($B)', 'consumer_burden_B', '${:.0f}B'),
        ('B50 combined burden ($B)', 'b50_combined_B', '${:.1f}B'),
        ('B50 per person ($)', 'b50_per_person', '${:,.0f}'),
        ('B50 % pretax income', 'b50_pct_income', '{:.1f}%'),
    ]
    
    for label, key, fmt in metrics:
        sq_val = status_quo[key]
        vals = [combined_results[s][key] for s in ['Low', 'Central', 'High']]
        sq_str = fmt.format(sq_val)
        val_strs = [fmt.format(v) for v in vals]
        logger.info(f"  {label:<35} {sq_str:>12} {val_strs[0]:>12} {val_strs[1]:>12} {val_strs[2]:>12}")
    
    return {
        'refund_scenario': refund,
        'legislative_scenarios': legislative,
        'combined': combined_results,
        'status_quo': status_quo,
    }


def model_crra_welfare(combined_results):
    """
    CRRA welfare analysis (σ = 2) comparing status quo vs scenario.
    Following the paper's established methodology from Section 8.1.
    """
    logger.info("\n" + "=" * 70)
    logger.info("CRRA WELFARE ANALYSIS (σ = 2)")
    logger.info("=" * 70)
    
    sigma = 2
    
    # Status quo per-person losses by quintile (from counterfactual analysis)
    sq_losses = {
        'Q1': 1440, 'Q2': 1308, 'Q3': 1162, 'Q4': 1129, 'Q5': 893,
    }
    
    # Welfare weight: w(c) = c^(-σ), normalized to Q3
    # Using mean pretax income as consumption proxy
    welfare_weights = {}
    q3_income = QUINTILE_MEAN_INCOME['Q3']
    for q, inc in QUINTILE_MEAN_INCOME.items():
        if inc > 0:
            welfare_weights[q] = (q3_income / max(inc, 1)) ** sigma
        else:
            welfare_weights[q] = float('inf')
    
    logger.info(f"\n  Welfare weights (normalized to Q3 = 1.0):")
    for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
        logger.info(f"    {q}: {welfare_weights[q]:.2f}")
    
    # Central scenario comparison
    central = combined_results['Central']
    scenario_losses = {
        q: central['quintile_detail'][q]['per_person']
        for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
    }
    
    # Welfare-weighted total loss
    sq_welfare = sum(sq_losses[q] * welfare_weights[q] * QUINTILE_POP[q]
                     for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
    sc_welfare = sum(scenario_losses[q] * welfare_weights[q] * QUINTILE_POP[q]
                     for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
    
    welfare_change_pct = ((sc_welfare - sq_welfare) / abs(sq_welfare)) * 100
    
    logger.info(f"\n  Welfare-weighted total loss:")
    logger.info(f"    Status quo:        {sq_welfare:>20,.0f}")
    logger.info(f"    Central scenario:  {sc_welfare:>20,.0f}")
    logger.info(f"    Change:            {welfare_change_pct:>+.1f}%")
    
    if sc_welfare < sq_welfare:
        logger.info(f"    → Scenario REDUCES welfare loss (B50 better off)")
    else:
        logger.info(f"    → Scenario INCREASES welfare loss (B50 worse off)")
    
    return {
        'sigma': sigma,
        'sq_welfare_weighted_loss': sq_welfare,
        'scenario_welfare_weighted_loss': sc_welfare,
        'welfare_change_pct': welfare_change_pct,
        'sq_losses': sq_losses,
        'scenario_losses': scenario_losses,
        'welfare_weights': welfare_weights,
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    logger.info("=" * 70)
    logger.info("SCOTUS TARIFF REVOCATION + 15% LEGISLATIVE TARIFF SCENARIO")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Date: February 2026")
    logger.info("Context: Supreme Court revoked executive tariffs; Trump")
    logger.info("administration announced 15% universal tariff via legislation.")
    logger.info("")
    logger.info("Assumptions (all clearly flagged):")
    logger.info(f"  Total US goods imports: ${TOTAL_GOODS_IMPORTS_B:,}B (Census 2024)")
    logger.info(f"  Legislative tariff rate: {LEGISLATIVE_TARIFF_RATE*100:.0f}%")
    logger.info(f"  Import demand elasticity: {IMPORT_ELASTICITY}")
    logger.info(f"  DWL factor: {DWL_FACTOR}× (Amiti et al. 2019)")
    logger.info(f"  Refund amount: ${REFUND_AMOUNT_B}B (above-baseline executive tariffs)")
    logger.info(f"  New debt interest rate: {NEW_DEBT_INTEREST_RATE*100:.1f}%")
    logger.info(f"  B50 population: {B50_POP:,} (CPS Q1+Q2+0.5×Q3)")
    logger.info(f"  B50 mean pretax income: ${B50_MEAN_PRETAX_INCOME:,}")
    logger.info("")
    
    all_results = model_combined_scenario()
    welfare = model_crra_welfare(all_results['combined'])
    all_results['welfare_analysis'] = welfare
    
    # Save results
    output = {
        'metadata': {
            'date': '2026-02-21',
            'description': 'SCOTUS tariff revocation + 15% legislative tariff scenario analysis',
            'assumptions': {
                'total_goods_imports_B': TOTAL_GOODS_IMPORTS_B,
                'legislative_tariff_rate': LEGISLATIVE_TARIFF_RATE,
                'import_demand_elasticity': IMPORT_ELASTICITY,
                'dwl_factor': DWL_FACTOR,
                'refund_amount_B': REFUND_AMOUNT_B,
                'new_debt_interest_rate': NEW_DEBT_INTEREST_RATE,
                'b50_population': B50_POP,
                'b50_mean_pretax_income': B50_MEAN_PRETAX_INCOME,
                'b50_cps_tariff_share': B50_CPS_TARIFF_SHARE,
                'trade_volume_reduction_central': TRADE_VOLUME_REDUCTION,
            },
        },
        'refund_scenario': {
            k: v for k, v in all_results['refund_scenario'].items()
            if k != 'relief_by_quintile_B'
        },
        'refund_quintile_relief_B': all_results['refund_scenario']['relief_by_quintile_B'],
        'legislative_scenarios': {
            name: {k: v for k, v in scen.items() if k != 'quintile_burden_B'}
            for name, scen in all_results['legislative_scenarios'].items()
        },
        'combined_scenarios': {},
        'welfare_analysis': {
            'sigma': welfare['sigma'],
            'sq_welfare_weighted_loss': welfare['sq_welfare_weighted_loss'],
            'scenario_welfare_weighted_loss': welfare['scenario_welfare_weighted_loss'],
            'welfare_change_pct': welfare['welfare_change_pct'],
        },
        'status_quo_comparison': all_results['status_quo'],
    }
    
    # Add combined scenarios with quintile detail
    for name, comb in all_results['combined'].items():
        output['combined_scenarios'][name] = {
            'scenario': comb['scenario'],
            'tariff_revenue_B': comb['tariff_revenue_B'],
            'consumer_burden_B': comb['consumer_burden_B'],
            'revenue_vs_fy25_B': comb['revenue_vs_fy25_B'],
            'annual_interest_cost_B': comb['annual_interest_cost_B'],
            'net_fiscal_change_B': comb['net_fiscal_change_B'],
            'b50_spending_cuts_B': comb['b50_spending_cuts_B'],
            'b50_tariff_burden_B': comb['b50_tariff_burden_B'],
            'b50_combined_B': comb['b50_combined_B'],
            'b50_per_person': comb['b50_per_person'],
            'b50_pct_income': comb['b50_pct_income'],
            'quintile_detail': comb['quintile_detail'],
        }
    
    out_path = TABLES / "scotus_tariff_scenario.json"
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    logger.info(f"\n  ✓ Results saved to {out_path}")
    
    # --- Summary ---
    logger.info("\n" + "=" * 70)
    logger.info("KEY FINDINGS")
    logger.info("=" * 70)
    
    central = all_results['combined']['Central']
    logger.info(f"""
  Under the combined scenario (SCOTUS revocation + 15% legislative tariff):

  1. TARIFF REFUND: $100B in debt-financed refunds generates ${all_results['refund_scenario']['annual_interest_on_refund_B']:.1f}B/yr
     in additional interest payments, predominantly benefiting top-decile
     bondholders (who hold {TOP_DECILE_BOND_SHARE*100:.0f}% of bonds).

  2. CONSUMER BURDEN: A 15% universal tariff on ${TOTAL_GOODS_IMPORTS_B:,}B in imports
     generates ${central['tariff_revenue_B']:.0f}B in revenue (central estimate),
     with ${central['consumer_burden_B']:.0f}B in DWL-inclusive consumer burden.

  3. B50 IMPACT: Combined burden (spending cuts + new tariff) = ${central['b50_combined_B']:.1f}B
     (${central['b50_per_person']:,.0f}/person, {central['b50_pct_income']:.1f}% of pretax income).
     
  4. COMPARISON: Status quo B50 burden = $181.8B ($1,331/person, 10.6%).
     Change: {'+'if central['b50_combined_B']-181.8>0 else ''}{central['b50_combined_B']-181.8:.1f}B
     ({'+'if central['b50_per_person']-1331>0 else ''}{central['b50_per_person']-1331:,.0f}/person).

  5. WELFARE: CRRA (σ=2) welfare-weighted loss changes by {welfare['welfare_change_pct']:+.1f}%
     vs. status quo.
     
  6. FISCAL POSITION: Net annual fiscal change (new tariff revenue − old revenue
     − refund interest): {'+'if central['net_fiscal_change_B']>0 else ''}{central['net_fiscal_change_B']:.1f}B/yr.
""")
    
    return all_results


if __name__ == "__main__":
    main()
