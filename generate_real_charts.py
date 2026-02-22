"""
=============================================================================
REAL-TERMS CHARTS — Publication-quality figures for federal budget analysis
=============================================================================
All dollar figures in real 2024 dollars (CPI-U deflated).
Charts include propensity tier coloring and tariff windfall visualization.
=============================================================================
"""

import sys, os, json, warnings
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
from datetime import date

from src.utils.config import load_config, get_output_path, setup_logging
from src.database.models import get_session, EconomicSeries, Observation

setup_logging()
config = load_config()
FIGURES = get_output_path("figures")
TABLES = get_output_path("tables")
session = get_session()

# Load deflators
with open(TABLES / "cpi_deflators.json") as f:
    DEFLATORS = json.load(f)
FY_DEFLATOR = {int(k): v for k, v in DEFLATORS['fiscal_year'].items()}

# Colors
TIER_COLORS = {
    'HIGH': '#e63946',   # Red — direct benefit to bottom 50%
    'MID':  '#457b9d',   # Blue — indirect benefit
    'LOW':  '#a8dadc',   # Light teal — minimal direct benefit
}
TIER_LABELS = {
    'HIGH': 'HIGH: Direct benefit to bottom 50%',
    'MID':  'MID: Indirect benefit',
    'LOW':  'LOW: Minimal direct benefit',
}

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.facecolor': 'white',
    'axes.facecolor': '#fafafa',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'figure.dpi': 150,
})


def get_series_df(series_id, start_year=2015, end_year=2025, use_real=True):
    """Load a series and optionally convert to real 2024 dollars."""
    obs = session.query(Observation).filter_by(series_id=series_id)\
        .order_by(Observation.date).all()
    if not obs:
        return pd.Series(dtype=float)
    
    data = {}
    for o in obs:
        yr = o.date.year
        # FY series stored as Sept 30 → fiscal year is the year
        if o.date.month == 9:
            fy = yr
        elif o.date.month > 9:
            fy = yr + 1
        else:
            fy = yr
        
        if start_year <= fy <= end_year:
            val = o.value
            if use_real and fy in FY_DEFLATOR:
                val = val * FY_DEFLATOR[fy]
            data[fy] = val
    
    if not data:
        return pd.Series(dtype=float)
    return pd.Series(data).sort_index()


def billions_fmt(x, p):
    """Format axis as $XB."""
    return f'${x:,.0f}B'


# ============================================================================
# CHART 1: Propensity Tier Stacked Area (Budget Functions)
# ============================================================================

def chart_propensity_stacked_area():
    """Stacked area of spending by propensity tier over time."""
    from run_real_analysis import PROPENSITY_BUDGET_FUNCTION
    
    tier_data = {'HIGH': {}, 'MID': {}, 'LOW': {}}
    
    for sid, (tier, _) in PROPENSITY_BUDGET_FUNCTION.items():
        s = get_series_df(sid, 2015, 2025)
        for yr, val in s.items():
            tier_data[tier][yr] = tier_data[tier].get(yr, 0) + val
    
    years = sorted(set().union(*[d.keys() for d in tier_data.values()]))
    if not years:
        print("  No data for propensity stacked area chart")
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    high_vals = [tier_data['HIGH'].get(y, 0) for y in years]
    mid_vals = [tier_data['MID'].get(y, 0) for y in years]
    low_vals = [tier_data['LOW'].get(y, 0) for y in years]
    
    ax.stackplot(years, high_vals, mid_vals, low_vals,
                 labels=[TIER_LABELS['HIGH'], TIER_LABELS['MID'], TIER_LABELS['LOW']],
                 colors=[TIER_COLORS['HIGH'], TIER_COLORS['MID'], TIER_COLORS['LOW']],
                 alpha=0.85)
    
    ax.set_title('Federal Spending by Bottom-50% Propensity Tier\n(Real 2024 Dollars)', fontweight='bold')
    ax.set_ylabel('Total Outlays (Billions, Real 2024$)')
    ax.set_xlabel('Fiscal Year')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_fmt))
    ax.legend(loc='upper left', framealpha=0.9)
    ax.set_xlim(min(years), max(years))
    
    # Annotate COVID spike
    if 2020 in years:
        total_2020 = sum(tier_data[t].get(2020, 0) for t in tier_data)
        ax.annotate('COVID\nSpending\nSurge', xy=(2020, total_2020),
                     xytext=(2020.5, total_2020 + 200),
                     arrowprops=dict(arrowstyle='->', color='gray'),
                     fontsize=9, color='gray', ha='center')
    
    plt.tight_layout()
    path = FIGURES / "real_propensity_stacked_area.png"
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


# ============================================================================
# CHART 2: HIGH vs LOW Propensity Bar Chart (FY2019 vs FY2025)
# ============================================================================

def chart_propensity_comparison():
    """Side-by-side bar comparing HIGH vs LOW propensity spending growth."""
    from run_real_analysis import PROPENSITY_BUDGET_FUNCTION
    
    tier_years = {}
    for sid, (tier, _) in PROPENSITY_BUDGET_FUNCTION.items():
        for yr in [2019, 2025]:
            s = get_series_df(sid, yr, yr)
            if yr in s.index:
                key = (tier, yr)
                tier_years[key] = tier_years.get(key, 0) + s[yr]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    tiers = ['HIGH', 'MID', 'LOW']
    x = np.arange(len(tiers))
    width = 0.35
    
    vals_19 = [tier_years.get((t, 2019), 0) for t in tiers]
    vals_25 = [tier_years.get((t, 2025), 0) for t in tiers]
    
    bars1 = ax.bar(x - width/2, vals_19, width, label='FY2019', color='#264653', alpha=0.8)
    bars2 = ax.bar(x + width/2, vals_25, width, label='FY2025', color='#e76f51', alpha=0.8)
    
    # Add change annotations
    for i, t in enumerate(tiers):
        delta = vals_25[i] - vals_19[i]
        pct = (delta / abs(vals_19[i]) * 100) if vals_19[i] else 0
        y_pos = max(vals_19[i], vals_25[i]) + 50
        ax.text(i, y_pos, f'{pct:+.0f}%\n({delta:+,.0f}B)', ha='center', va='bottom',
                fontsize=10, fontweight='bold',
                color='green' if delta > 0 else 'red')
    
    ax.set_xticks(x)
    ax.set_xticklabels([f'{t}\n({TIER_LABELS[t].split(":")[1].strip()})'
                        for t in tiers], fontsize=10)
    ax.set_ylabel('Total Outlays (Billions, Real 2024$)')
    ax.set_title('Spending Growth by Bottom-50% Propensity Tier\nFY2019 → FY2025 (Real 2024$)', fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_fmt))
    ax.legend()
    
    plt.tight_layout()
    path = FIGURES / "real_propensity_comparison.png"
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


# ============================================================================
# CHART 3: Net Interest vs Safety-Net Spending (Real)
# ============================================================================

def chart_interest_vs_safety_net():
    """Line chart comparing net interest to HIGH-propensity spending."""
    interest = get_series_df('CBO_OUT_Net_interest', 2000, 2025)
    
    # Safety net: income security + health + education (budget functions)
    safety_ids = ['MTS_BF_Income_Security', 'MTS_BF_Health',
                  'MTS_BF_Education_Training_Employment_and_Social_Services']
    
    safety_data = {}
    for sid in safety_ids:
        s = get_series_df(sid, 2015, 2025)
        for yr, val in s.items():
            safety_data[yr] = safety_data.get(yr, 0) + val
    
    # Also use CBO mandatory for longer range
    income_sec = get_series_df('CBO_MAND_Income_securityᵇ', 2000, 2025)
    medicaid = get_series_df('CBO_MAND_Medicaid', 2000, 2025)
    
    cbo_safety = {}
    for yr in set(list(income_sec.index) + list(medicaid.index)):
        cbo_safety[yr] = (income_sec.get(yr, 0) or 0) + (medicaid.get(yr, 0) or 0)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    if interest.any():
        ax.plot(interest.index, interest.values, 'o-', color='#e63946',
                linewidth=2.5, markersize=4, label='Net Interest (LOW propensity)', zorder=3)
    
    if cbo_safety:
        yrs = sorted(cbo_safety.keys())
        vals = [cbo_safety[y] for y in yrs]
        ax.plot(yrs, vals, 's-', color='#2a9d8f', linewidth=2.5,
                markersize=4, label='Income Security + Medicaid (HIGH propensity)', zorder=3)
    
    ax.set_title('Net Interest Payments vs. Safety-Net Spending\n(Real 2024 Dollars)', fontweight='bold')
    ax.set_ylabel('Annual Outlays (Billions, Real 2024$)')
    ax.set_xlabel('Fiscal Year')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_fmt))
    ax.legend(loc='upper left', fontsize=11)
    
    # Annotate the crossover
    ax.axvline(x=2023, color='gray', linestyle='--', alpha=0.5)
    ax.text(2023.1, 300, 'Interest surges\npast safety net\n(in real terms)', fontsize=9, color='gray')
    
    plt.tight_layout()
    path = FIGURES / "real_interest_vs_safety_net.png"
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


# ============================================================================
# CHART 4: Budget Function Waterfall (Real FY2020 → FY2025)
# ============================================================================

def chart_budget_function_waterfall():
    """Waterfall chart showing real changes in each budget function."""
    from run_real_analysis import PROPENSITY_BUDGET_FUNCTION
    
    changes = []
    for sid, (tier, desc) in PROPENSITY_BUDGET_FUNCTION.items():
        s20 = get_series_df(sid, 2020, 2020)
        s25 = get_series_df(sid, 2025, 2025)
        v20 = s20.get(2020, 0)
        v25 = s25.get(2025, 0)
        if v20 == 0 and v25 == 0:
            continue
        delta = v25 - v20
        label = sid.replace('MTS_BF_', '').replace('_', ' ')
        if len(label) > 25:
            label = label[:23] + '…'
        changes.append((label, delta, tier))
    
    # Sort by change magnitude
    changes.sort(key=lambda x: x[1])
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    labels = [c[0] for c in changes]
    deltas = [c[1] for c in changes]
    colors = [TIER_COLORS[c[2]] for c in changes]
    
    bars = ax.barh(range(len(labels)), deltas, color=colors, alpha=0.85, edgecolor='white')
    
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Change in Real Outlays (Billions, 2024$)')
    ax.set_title('Change in Federal Spending by Budget Function\nFY2020 → FY2025 (Real 2024$)', fontweight='bold')
    ax.axvline(x=0, color='black', linewidth=0.8)
    
    # Value labels
    for bar, val in zip(bars, deltas):
        x_pos = bar.get_width()
        align = 'left' if val >= 0 else 'right'
        offset = 5 if val >= 0 else -5
        ax.text(x_pos + offset, bar.get_y() + bar.get_height()/2,
                f'{val:+,.0f}B', va='center', ha=align, fontsize=8)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=TIER_COLORS[t], label=TIER_LABELS[t])
                       for t in ['HIGH', 'MID', 'LOW']]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    plt.tight_layout()
    path = FIGURES / "real_budget_function_waterfall.png"
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


# ============================================================================
# CHART 5: Agency-Level Top 15 (Real)
# ============================================================================

def chart_top_agencies():
    """Top 15 agencies by FY2025 real outlays, color-coded by propensity."""
    from run_real_analysis import PROPENSITY_AGENCY
    
    agencies = []
    for sid, (tier, desc) in PROPENSITY_AGENCY.items():
        s25 = get_series_df(sid, 2025, 2025)
        v25 = s25.get(2025, 0)
        if v25 and abs(v25) > 1:  # Skip near-zero
            label = sid.replace('MTS_AG_', '').replace('_', ' ')
            if len(label) > 35:
                label = label[:33] + '…'
            agencies.append((label, v25, tier))
    
    # Sort by absolute value, take top 15
    agencies.sort(key=lambda x: abs(x[1]), reverse=True)
    agencies = agencies[:15]
    agencies.reverse()  # For horizontal bar (bottom to top)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    labels = [a[0] for a in agencies]
    vals = [a[1] for a in agencies]
    colors = [TIER_COLORS[a[2]] for a in agencies]
    
    bars = ax.barh(range(len(labels)), vals, color=colors, alpha=0.85, edgecolor='white')
    
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('FY2025 Net Outlays (Billions, Real 2024$)')
    ax.set_title('Top 15 Federal Agencies by Spending (FY2025)\nColor = Bottom-50% Propensity Tier', fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(billions_fmt))
    
    # Value labels
    for bar, val in zip(bars, vals):
        x_pos = bar.get_width()
        ax.text(x_pos + 10, bar.get_y() + bar.get_height()/2,
                f'${val:,.0f}B', va='center', fontsize=8)
    
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=TIER_COLORS[t], label=TIER_LABELS[t])
                       for t in ['HIGH', 'MID', 'LOW']]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    plt.tight_layout()
    path = FIGURES / "real_top_agencies.png"
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


# ============================================================================
# CHART 6: Tariff Windfall Flow Diagram
# ============================================================================

def chart_tariff_windfall():
    """Visual flow diagram of tariff→refund wealth transfer."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(5, 7.5, 'Tariff → Refund Wealth Transfer Model',
            fontsize=16, fontweight='bold', ha='center', va='center')
    ax.text(5, 7.0, '(Real 2024 Dollars)', fontsize=11, ha='center',
            va='center', color='gray')
    
    # Step boxes
    box_style = dict(boxstyle='round,pad=0.5', facecolor='#f1faee', edgecolor='#264653', linewidth=2)
    loss_box = dict(boxstyle='round,pad=0.5', facecolor='#ffccd5', edgecolor='#e63946', linewidth=2)
    gain_box = dict(boxstyle='round,pad=0.5', facecolor='#d4edda', edgecolor='#2a9d8f', linewidth=2)
    
    # Flow: Tariffs → Consumers pay → Revenue → Refund → Company profit → Shareholders
    #                                    ↓ Deficit ↓ → Bondholders
    
    # Top row: The tariff cycle
    ax.text(1.5, 5.5, 'Tariffs\nImposed\n(+$118B)', fontsize=11, ha='center',
            va='center', bbox=box_style)
    ax.text(4.0, 5.5, 'Consumers\nPay Higher\nPrices', fontsize=11, ha='center',
            va='center', bbox=loss_box)
    ax.text(6.5, 5.5, 'Gov\'t Collects\n$195B\n(FY2025)', fontsize=11, ha='center',
            va='center', bbox=box_style)
    ax.text(9.0, 5.5, 'Already Spent\n(Deficit\nFinanced)', fontsize=11, ha='center',
            va='center', bbox=box_style)
    
    # Arrows top row
    ax.annotate('', xy=(2.8, 5.5), xytext=(2.2, 5.5),
                arrowprops=dict(arrowstyle='->', color='#264653', lw=2))
    ax.annotate('', xy=(5.3, 5.5), xytext=(4.8, 5.5),
                arrowprops=dict(arrowstyle='->', color='#264653', lw=2))
    ax.annotate('', xy=(7.8, 5.5), xytext=(7.3, 5.5),
                arrowprops=dict(arrowstyle='->', color='#264653', lw=2))
    
    # Bottom row: The refund
    ax.text(1.5, 3.0, 'Tariff\nRefund\n(~$118B)', fontsize=11, ha='center',
            va='center', bbox=box_style)
    ax.text(4.0, 3.0, 'Companies\nReceive\nWindfall', fontsize=11, ha='center',
            va='center', bbox=gain_box)
    ax.text(6.5, 4.0, 'Shareholders\n+$2.4T\n(Market Cap)', fontsize=11, ha='center',
            va='center', bbox=gain_box)
    ax.text(6.5, 2.0, 'Bondholders\n+$5.3B/yr\n(Interest)', fontsize=11, ha='center',
            va='center', bbox=gain_box)
    ax.text(9.0, 3.0, 'Future Taxpayers\n-$5.3B/yr\n(Debt Service)', fontsize=11,
            ha='center', va='center', bbox=loss_box)
    
    # Arrows bottom row
    ax.annotate('', xy=(2.8, 3.0), xytext=(2.2, 3.0),
                arrowprops=dict(arrowstyle='->', color='#264653', lw=2))
    ax.annotate('', xy=(5.5, 3.7), xytext=(4.8, 3.2),
                arrowprops=dict(arrowstyle='->', color='#2a9d8f', lw=2))
    ax.annotate('', xy=(5.5, 2.3), xytext=(4.8, 2.8),
                arrowprops=dict(arrowstyle='->', color='#2a9d8f', lw=2))
    ax.annotate('', xy=(7.8, 3.5), xytext=(7.5, 3.8),
                arrowprops=dict(arrowstyle='->', color='#e63946', lw=1.5, linestyle='dashed'))
    ax.annotate('', xy=(7.8, 2.5), xytext=(7.5, 2.2),
                arrowprops=dict(arrowstyle='->', color='#e63946', lw=1.5, linestyle='dashed'))
    
    # Arrow from top to bottom (refund loop)
    ax.annotate('Refund\nAnnounced', xy=(1.5, 4.0), xytext=(1.5, 4.8),
                arrowprops=dict(arrowstyle='->', color='#e76f51', lw=2),
                fontsize=9, ha='center', color='#e76f51')
    
    # Key finding box
    finding = ("NET EFFECT: Wealth transferred FROM\n"
               "consumers & future taxpayers (bottom 50%)\n"
               "TO shareholders & bondholders (top 10%)")
    ax.text(5, 0.6, finding, fontsize=11, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#fff3cd',
                      edgecolor='#856404', linewidth=2),
            fontweight='bold')

    # Source/assumption footnote
    ax.text(5, -0.15,
            'Assumptions: 4.5% 10-yr Treasury (FRED DGS10, Jan 2025 avg); '
            '20× P/E (conservative; trailing S&P 500 ≈21–24×).\n'
            'Equity ownership: top 10% hold 93% (Fed 2023 SCF). '
            'Bond ownership: top 10% hold ≈67% (Fed DFA; Batty et al. 2019).',
            fontsize=7.5, ha='center', va='top', color='#555555',
            fontstyle='italic')
    
    plt.tight_layout()
    path = FIGURES / "real_tariff_windfall_flow.png"
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


# ============================================================================
# CHART 7: Real Interest Payments Timeline
# ============================================================================

def chart_real_interest_timeline():
    """Dual-axis: nominal vs real interest payments over time."""
    interest = get_series_df('CBO_OUT_Net_interest', 2000, 2025, use_real=True)
    interest_nom = get_series_df('CBO_OUT_Net_interest', 2000, 2025, use_real=False)
    
    if interest.empty:
        print("  No interest data for timeline chart")
        return
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    ax.fill_between(interest_nom.index, 0, interest_nom.values,
                    alpha=0.3, color='#e9c46a', label='Nominal Dollars')
    ax.plot(interest_nom.index, interest_nom.values, '-', color='#e9c46a',
            linewidth=1.5)
    
    ax.fill_between(interest.index, 0, interest.values,
                    alpha=0.3, color='#e63946', label='Real 2024 Dollars')
    ax.plot(interest.index, interest.values, 'o-', color='#e63946',
            linewidth=2.5, markersize=4)
    
    ax.set_title('Net Interest Payments: Nominal vs. Real 2024$', fontweight='bold')
    ax.set_ylabel('Annual Net Interest (Billions)')
    ax.set_xlabel('Fiscal Year')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_fmt))
    ax.legend(loc='upper left', fontsize=11)
    
    # Annotate the inflation gap
    yr_label = 2022
    if yr_label in interest.index and yr_label in interest_nom.index:
        gap = interest[yr_label] - interest_nom[yr_label]
        mid = (interest[yr_label] + interest_nom[yr_label]) / 2
        ax.annotate(f'Inflation\nadds\n${gap:.0f}B', xy=(yr_label, mid),
                     fontsize=9, color='gray', ha='center')
    
    plt.tight_layout()
    path = FIGURES / "real_interest_timeline.png"
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


# ============================================================================
# CHART 8: Defense vs. Social Spending (Real)
# ============================================================================

def chart_defense_vs_social():
    """Compare defense spending growth to social spending in real terms."""
    defense = get_series_df('MTS_BF_National_Defense', 2015, 2025)
    health = get_series_df('MTS_BF_Health', 2015, 2025)
    income_sec = get_series_df('MTS_BF_Income_Security', 2015, 2025)
    education = get_series_df('MTS_BF_Education_Training_Employment_and_Social_Services', 2015, 2025)
    interest = get_series_df('MTS_BF_Net_Interest', 2015, 2025)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    series_list = [
        (defense, 'National Defense', '#264653', 'o'),
        (health, 'Health (Medicaid etc.)', '#2a9d8f', 's'),
        (income_sec, 'Income Security', '#e63946', '^'),
        (education, 'Education/Training', '#e76f51', 'D'),
        (interest, 'Net Interest', '#f4a261', 'v'),
    ]
    
    for s, label, color, marker in series_list:
        if not s.empty:
            ax.plot(s.index, s.values, f'{marker}-', color=color,
                    linewidth=2, markersize=5, label=label)
    
    ax.set_title('Key Budget Functions in Real 2024 Dollars', fontweight='bold')
    ax.set_ylabel('Annual Outlays (Billions, Real 2024$)')
    ax.set_xlabel('Fiscal Year')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_fmt))
    ax.legend(loc='upper left', fontsize=10)
    
    # 2020 indicator
    ax.axvline(x=2020, color='gray', linestyle=':', alpha=0.5)
    ax.text(2020.1, ax.get_ylim()[1] * 0.95, 'COVID', fontsize=9, color='gray')
    
    plt.tight_layout()
    path = FIGURES / "real_defense_vs_social.png"
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


# ============================================================================
# CHART 9: Propensity Donut — Share of FY2025 Spending by Tier
# ============================================================================

def chart_propensity_donut():
    """Donut chart: share of FY2025 spending by propensity tier."""
    from run_real_analysis import PROPENSITY_BUDGET_FUNCTION
    
    tier_totals = {'HIGH': 0, 'MID': 0, 'LOW': 0}
    for sid, (tier, _) in PROPENSITY_BUDGET_FUNCTION.items():
        s = get_series_df(sid, 2025, 2025)
        v = s.get(2025, 0)
        if v and v > 0:
            tier_totals[tier] += v
    
    grand = sum(tier_totals.values())
    if grand == 0:
        print("  No data for propensity donut")
        return
    
    fig, ax = plt.subplots(figsize=(9, 9))
    
    sizes = [tier_totals['HIGH'], tier_totals['MID'], tier_totals['LOW']]
    labels = [f"HIGH\n${tier_totals['HIGH']:,.0f}B\n({tier_totals['HIGH']/grand*100:.0f}%)",
              f"MID\n${tier_totals['MID']:,.0f}B\n({tier_totals['MID']/grand*100:.0f}%)",
              f"LOW\n${tier_totals['LOW']:,.0f}B\n({tier_totals['LOW']/grand*100:.0f}%)"]
    colors = [TIER_COLORS['HIGH'], TIER_COLORS['MID'], TIER_COLORS['LOW']]
    
    wedges, texts = ax.pie(sizes, labels=labels, colors=colors,
                            startangle=90, pctdistance=0.85,
                            textprops={'fontsize': 12, 'fontweight': 'bold'})
    
    # Inner circle for donut
    centre = plt.Circle((0, 0), 0.60, fc='white')
    ax.add_patch(centre)
    
    ax.text(0, 0, f'FY2025\n${grand:,.0f}B\nTotal', ha='center', va='center',
            fontsize=14, fontweight='bold')
    
    ax.set_title('FY2025 Federal Spending by Bottom-50% Propensity\n(Real 2024$)', fontweight='bold')
    
    plt.tight_layout()
    path = FIGURES / "real_propensity_donut.png"
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


# ============================================================================
# CHART 10: Cumulative Real Change Since FY2019 by Tier
# ============================================================================

def chart_cumulative_change():
    """Cumulative $ change since FY2019 by propensity tier."""
    from run_real_analysis import PROPENSITY_BUDGET_FUNCTION
    
    tier_data = {'HIGH': {}, 'MID': {}, 'LOW': {}}
    for sid, (tier, _) in PROPENSITY_BUDGET_FUNCTION.items():
        s = get_series_df(sid, 2019, 2025)
        for yr, val in s.items():
            tier_data[tier][yr] = tier_data[tier].get(yr, 0) + val
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    for tier, color in TIER_COLORS.items():
        data = tier_data[tier]
        if 2019 not in data:
            continue
        base = data[2019]
        years = sorted(data.keys())
        changes = [data[y] - base for y in years]
        ax.plot(years, changes, 'o-', color=color, linewidth=2.5,
                markersize=6, label=TIER_LABELS[tier])
    
    ax.axhline(y=0, color='black', linewidth=0.8, linestyle='-')
    ax.set_title('Cumulative Change in Spending Since FY2019 by Propensity Tier\n(Real 2024$)', fontweight='bold')
    ax.set_ylabel('Change from FY2019 Baseline (Billions, Real 2024$)')
    ax.set_xlabel('Fiscal Year')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(billions_fmt))
    ax.legend(loc='upper left', fontsize=11)
    
    # Annotate COVID
    ax.axvline(x=2020, color='gray', linestyle=':', alpha=0.5)
    ax.text(2020.1, -100, 'COVID', fontsize=9, color='gray', rotation=90)
    
    plt.tight_layout()
    path = FIGURES / "real_cumulative_by_tier.png"
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n  Generating Real-Terms Charts...")
    print(f"  Output: {FIGURES}\n")
    
    chart_propensity_stacked_area()
    chart_propensity_comparison()
    chart_interest_vs_safety_net()
    chart_budget_function_waterfall()
    chart_top_agencies()
    chart_tariff_windfall()
    chart_real_interest_timeline()
    chart_defense_vs_social()
    chart_propensity_donut()
    chart_cumulative_change()
    
    session.close()
    print(f"\n  All charts saved to {FIGURES}")
    print("  Done.")
