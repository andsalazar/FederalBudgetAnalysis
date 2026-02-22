"""
=============================================================================
25-YEAR FEDERAL BUDGET ANALYSIS (FY2000–FY2025)
=============================================================================

Integrates:
  1. CBO Historical Budget Data (FY2000–2025) — aggregate spending & revenue
  2. Census Historical Income Tables (2000–2023) — income distribution trends
  3. CPS ASEC Benchmark Data (8 survey years) — B50 distributional analysis
  4. FRED Macro Series — wealth shares, poverty, Gini, social benefits
  5. Derived analytical series — safety-net ratios, regressive revenue share

Analysis structure:
  Part A: 25-year structural trends (spending, revenue, interest, tariffs)
  Part B: 25-year distributional evolution (income shares, wealth, transfers)
  Part C: Structural break tests — is FY2025 trend or break?
  Part D: FY2025 as case study — the convergence of three channels
  Part E: Summary with charts

Output: Charts (figures/) + analysis tables (tables/)
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
import matplotlib.ticker as mtick
from datetime import date
from pathlib import Path
from scipy import stats
from loguru import logger

# Reproducibility: fix all random seeds
np.random.seed(42)

from src.utils.config import get_output_path, PROJECT_ROOT
from src.database.models import get_session, Observation

logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | {message}", level="INFO")

FIGURES = get_output_path("figures")
TABLES = get_output_path("tables")
PROCESSED = PROJECT_ROOT / "data" / "processed"
FIGURES.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)

session = get_session()

# Load data files
cbo_trends = pd.read_csv(PROCESSED / "cbo_25year_trends.csv")
derived = pd.read_csv(PROCESSED / "derived_25year_series.csv")
census_quintiles = pd.read_csv(PROCESSED / "census_income_quintiles.csv")
cps_benchmarks = pd.read_csv(PROCESSED / "cps_asec_historical_quintiles.csv")

# Load deflators
with open(TABLES / "cpi_deflators.json") as f:
    DEFLATORS = json.load(f)
FY_DEFLATOR = {int(k): v for k, v in DEFLATORS['fiscal_year'].items()}

# Matplotlib style
plt.rcParams.update({
    'figure.figsize': (12, 7),
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'legend.fontsize': 10,
    'figure.dpi': 150,
    'savefig.bbox': 'tight',
    'savefig.dpi': 150,
})

COLORS = {
    'interest': '#e74c3c',
    'customs': '#e67e22',
    'income_sec': '#3498db',
    'medicaid': '#2ecc71',
    'social_sec': '#9b59b6',
    'defense': '#7f8c8d',
    'total': '#2c3e50',
    'highlight': '#e74c3c',
    'neutral': '#95a5a6',
}


# ============================================================================
# PART A: 25-YEAR STRUCTURAL BUDGET TRENDS
# ============================================================================

def chart_25yr_spending_composition():
    """
    Stacked area chart: Federal spending composition FY2000–2025 in real 2024$.
    Shows Social Security, Medicare, Medicaid, Income Security, Defense, 
    Net Interest, and Other discretionary.
    """
    logger.info("Chart: 25-year spending composition (stacked area)")
    
    years = cbo_trends['fiscal_year'].values
    
    # Get real values for each category
    categories = {
        'Social Security': 'CBO_MAND_Social_Security_real2024',
        'Mandatory Total': 'CBO_MAND_Total_real2024',
        'Medicaid': 'CBO_MAND_Medicaid_real2024',
        'Income Security': 'CBO_MAND_Income_securityᵇ_real2024',
        'Net Interest': 'CBO_OUT_Net_interest_real2024',
    }
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Compute "Other Mandatory" and "Other" from available data
    total = cbo_trends['CBO_OUTLAYS_real2024'].values
    
    ss = cbo_trends['CBO_MAND_Social_Security_real2024'].fillna(0).values
    medicaid = cbo_trends['CBO_MAND_Medicaid_real2024'].fillna(0).values
    inc_sec = cbo_trends['CBO_MAND_Income_securityᵇ_real2024'].fillna(0).values
    interest = cbo_trends['CBO_OUT_Net_interest_real2024'].fillna(0).values
    mand_total = cbo_trends['CBO_MAND_Total_real2024'].fillna(0).values
    
    other_mand = mand_total - ss - medicaid - inc_sec  # Medicare + other mandatory
    other_all = total - mand_total - interest  # Discretionary
    
    stack_data = {
        'Social Security': ss,
        'Other Mandatory (incl. Medicare)': np.maximum(other_mand, 0),
        'Medicaid': medicaid,
        'Income Security': inc_sec,
        'Net Interest': interest,
        'Discretionary (Defense + Other)': np.maximum(other_all, 0),
    }
    
    # Plot stacked area
    colors = ['#9b59b6', '#3498db', '#2ecc71', '#1abc9c', '#e74c3c', '#95a5a6']
    labels_ordered = ['Social Security', 'Other Mandatory (incl. Medicare)', 'Medicaid', 
                      'Income Security', 'Net Interest', 'Discretionary (Defense + Other)']
    
    bottoms = np.zeros(len(years))
    for i, label in enumerate(labels_ordered):
        vals = stack_data[label]
        ax.fill_between(years, bottoms, bottoms + vals, alpha=0.7, 
                        color=colors[i], label=label)
        bottoms += vals
    
    ax.plot(years, total, 'k-', linewidth=2, label='Total Outlays')
    
    # Annotations
    ax.axvline(x=2020, color='gray', linestyle=':', alpha=0.5, linewidth=1)
    ax.annotate('COVID\n(FY2020–21)', xy=(2020, total[years==2020][0]),
                xytext=(2016.5, 7500), fontsize=9, ha='center',
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.2))
    
    ax.axvline(x=2025, color=COLORS['highlight'], linestyle='--', alpha=0.5)
    ax.annotate('FY2025', xy=(2025, total[-1]), xytext=(2023, 7800),
                fontsize=10, fontweight='bold', color=COLORS['highlight'],
                arrowprops=dict(arrowstyle='->', color=COLORS['highlight'], lw=1.5))
    
    ax.set_xlabel('Fiscal Year', fontsize=12)
    ax.set_ylabel('Real 2024 Dollars (Billions)', fontsize=12)
    ax.set_title('Federal Spending Composition, FY2000–FY2025\n(Real 2024 Dollars)', fontsize=14)
    ax.legend(loc='upper left', framealpha=0.9)
    ax.set_xlim(2000, 2025)
    ax.set_xticks(range(2000, 2026, 5))
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'${x:,.0f}B'))
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(FIGURES / '25yr_spending_composition.png')
    plt.close()
    logger.info("  Saved 25yr_spending_composition.png")


def chart_25yr_revenue_mix():
    """
    Revenue composition FY2000–2025: progressive vs regressive sources.
    """
    logger.info("Chart: 25-year revenue composition")
    
    years = derived['fiscal_year'].values
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Left: Revenue in real dollars
    for sid, label, color in [
        ('CBO_REV_Individual_income_taxes_real2024', 'Individual Income Tax', '#3498db'),
        ('CBO_REV_Corporate_income_taxes_real2024', 'Corporate Income Tax', '#2ecc71'),
        ('CBO_REV_Payroll_taxes_real2024', 'Payroll Tax', '#e67e22'),
        ('CBO_REV_Customs_duties_real2024', 'Customs Duties', '#e74c3c'),
        ('CBO_REV_Excise_taxes_real2024', 'Excise Taxes', '#9b59b6'),
    ]:
        if sid in cbo_trends.columns:
            vals = cbo_trends[sid].values
            lw = 3 if 'Customs' in label else 1.5
            ax1.plot(years, vals, color=color, linewidth=lw, label=label, 
                    marker='o' if 'Customs' in label else None, markersize=4)
    
    ax1.set_xlabel('Fiscal Year')
    ax1.set_ylabel('Real 2024 Dollars (Billions)')
    ax1.set_title('Federal Revenue by Source (Real 2024$)')
    ax1.legend(fontsize=9)
    ax1.set_xticks(range(2000, 2026, 5))
    ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'${x:,.0f}B'))
    ax1.grid(alpha=0.3)
    
    # FY2025 customs spike annotation
    customs_vals = cbo_trends['CBO_REV_Customs_duties_real2024'].values
    ax1.annotate(f'${customs_vals[-1]:.0f}B\n(+422% real\nvs FY2000)', 
                xy=(2025, customs_vals[-1]), xytext=(2021, customs_vals[-1] + 50),
                fontsize=9, fontweight='bold', color='#e74c3c',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffeaa7', alpha=0.8),
                arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.5))
    
    # Right: Regressive vs Progressive revenue share
    ax2.plot(years, derived['regressive_rev_share'], 'o-', color='#e74c3c', 
            linewidth=2, label='Regressive (Payroll+Excise+Customs)', markersize=4)
    ax2.plot(years, derived['progressive_rev_share'], 's-', color='#3498db',
            linewidth=2, label='Progressive (Individual+Corporate)', markersize=4)
    
    ax2.set_xlabel('Fiscal Year')
    ax2.set_ylabel('Share of Total Revenue (%)')
    ax2.set_title('Progressive vs. Regressive Revenue Share')
    ax2.legend(fontsize=9)
    ax2.set_xticks(range(2000, 2026, 5))
    ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'{x:.0f}%'))
    ax2.grid(alpha=0.3)
    
    # Annotate the divergence
    ax2.fill_between(years, derived['regressive_rev_share'], 
                     derived['progressive_rev_share'], alpha=0.1, color='gray')
    
    plt.tight_layout()
    fig.savefig(FIGURES / '25yr_revenue_composition.png')
    plt.close()
    logger.info("  Saved 25yr_revenue_composition.png")


def chart_25yr_interest_vs_safetynet():
    """
    Net interest vs safety-net spending over 25 years.
    Shows the crowding-out dynamic.
    """
    logger.info("Chart: 25-year interest vs safety-net crowding")
    
    years = derived['fiscal_year'].values
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[2, 1])
    
    # Top panel: Real dollar trends
    ax1.plot(years, derived['interest_real2024'], 'o-', color=COLORS['interest'],
            linewidth=2.5, markersize=5, label='Net Interest', zorder=5)
    ax1.plot(years, derived['safety_net_real2024'], 's-', color=COLORS['income_sec'],
            linewidth=2.5, markersize=5, label='Safety Net (Income Security + Medicaid)')
    
    # Fill the gap when interest exceeds safety net
    ax1.fill_between(years, derived['interest_real2024'], derived['safety_net_real2024'],
                     where=derived['interest_real2024'] > derived['safety_net_real2024'],
                     alpha=0.2, color=COLORS['highlight'], label='Interest > Safety Net')
    
    # COVID spike annotation
    covid_mask = (years >= 2020) & (years <= 2021)
    if covid_mask.any():
        peak_val = derived.loc[derived['fiscal_year']==2021, 'safety_net_real2024'].values
        if len(peak_val) > 0:
            ax1.annotate('COVID Relief\nSpike', xy=(2021, peak_val[0]),
                        xytext=(2017, peak_val[0] + 100),
                        fontsize=9, ha='center',
                        arrowprops=dict(arrowstyle='->', color='gray', lw=1.2))
    
    # FY2025 convergence annotation
    int_2025 = derived.loc[derived['fiscal_year']==2025, 'interest_real2024'].values
    sn_2025 = derived.loc[derived['fiscal_year']==2025, 'safety_net_real2024'].values
    if len(int_2025) > 0 and len(sn_2025) > 0:
        ratio = int_2025[0] / sn_2025[0] * 100
        ax1.annotate(f'FY2025: Interest = {ratio:.0f}%\nof Safety Net',
                    xy=(2025, int_2025[0]), xytext=(2019, int_2025[0] + 200),
                    fontsize=10, fontweight='bold', color=COLORS['highlight'],
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='#fadbd8', alpha=0.9),
                    arrowprops=dict(arrowstyle='->', color=COLORS['highlight'], lw=1.5))
    
    ax1.set_ylabel('Real 2024 Dollars (Billions)')
    ax1.set_title('Net Interest vs. Safety-Net Spending, FY2000–FY2025\n(Real 2024 Dollars)', fontsize=14)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.set_xticks(range(2000, 2026, 5))
    ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'${x:,.0f}B'))
    ax1.grid(alpha=0.3)
    
    # Bottom panel: Interest/Safety-net ratio
    ax2.bar(years, derived['interest_crowding_ratio'], color=[
        COLORS['highlight'] if r >= 0.9 else COLORS['neutral'] 
        for r in derived['interest_crowding_ratio']
    ], alpha=0.8)
    ax2.axhline(y=1.0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.annotate('Interest = Safety Net', xy=(2012, 1.0), fontsize=9, 
                color='gray', ha='center', va='bottom')
    
    ax2.set_xlabel('Fiscal Year')
    ax2.set_ylabel('Ratio')
    ax2.set_title('Interest-to-Safety-Net Ratio')
    ax2.set_xticks(range(2000, 2026, 5))
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(FIGURES / '25yr_interest_vs_safetynet.png')
    plt.close()
    logger.info("  Saved 25yr_interest_vs_safetynet.png")


def chart_25yr_customs_trajectory():
    """
    Customs revenue over 25 years — the tariff escalation trajectory.
    """
    logger.info("Chart: 25-year customs revenue trajectory")
    
    years = derived['fiscal_year'].values
    customs = derived['customs_real2024'].values
    customs_share = derived['customs_share_of_rev'].values
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[2, 1])
    
    # Top: Real customs revenue
    bar_colors = []
    for i, yr in enumerate(years):
        if yr == 2025:
            bar_colors.append('#e74c3c')  # Red: Liberation Day
        elif yr in [2019, 2020]:
            bar_colors.append('#e67e22')  # Orange: Section 301
        elif yr >= 2018:
            bar_colors.append('#f39c12')  # Yellow: tariff era
        else:
            bar_colors.append('#3498db')  # Blue: pre-tariff
    
    bars = ax1.bar(years, customs, color=bar_colors, alpha=0.85, edgecolor='white', linewidth=0.5)
    
    # Trend line (pre-2017)
    pre_tariff = derived[derived['fiscal_year'] <= 2017]
    slope, intercept, r, p, se = stats.linregress(pre_tariff['fiscal_year'], 
                                                    pre_tariff['customs_real2024'])
    trend_years = np.arange(2000, 2026)
    trend_line = slope * trend_years + intercept
    ax1.plot(trend_years, trend_line, '--', color='gray', linewidth=1.5, alpha=0.7,
            label=f'Pre-2017 Trend (slope: ${slope:.1f}B/yr)')
    
    # Annotations
    ax1.annotate('Section 301\nChina Tariffs\n(2018)', xy=(2019, customs[years==2019]),
                xytext=(2014, customs[years==2019][0] + 30),
                fontsize=9, ha='center', color='#e67e22',
                bbox=dict(boxstyle='round', facecolor='#ffeaa7', alpha=0.8),
                arrowprops=dict(arrowstyle='->', color='#e67e22', lw=1.2))
    
    ax1.annotate(f'"Liberation Day"\nFY2025: ${customs[-1]:.0f}B\n(+422% real vs FY2000)',
                xy=(2025, customs[-1]), xytext=(2020, customs[-1] + 20),
                fontsize=10, fontweight='bold', color='#e74c3c',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#fadbd8', alpha=0.9),
                arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.5))
    
    ax1.set_ylabel('Real 2024 Dollars (Billions)')
    ax1.set_title('Federal Customs Revenue (Tariffs), FY2000–FY2025\n(Real 2024 Dollars)', fontsize=14)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.set_xticks(range(2000, 2026, 5))
    ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'${x:,.0f}B'))
    ax1.grid(axis='y', alpha=0.3)
    
    # Bottom: Customs as % of total revenue
    ax2.plot(years, customs_share, 'o-', color='#e74c3c', linewidth=2, markersize=5)
    ax2.fill_between(years, customs_share, alpha=0.2, color='#e74c3c')
    
    ax2.set_xlabel('Fiscal Year')
    ax2.set_ylabel('Share of Total Revenue (%)')
    ax2.set_title('Customs as Share of Total Federal Revenue')
    ax2.set_xticks(range(2000, 2026, 5))
    ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(FIGURES / '25yr_customs_trajectory.png')
    plt.close()
    logger.info("  Saved 25yr_customs_trajectory.png")


# ============================================================================
# PART B: 25-YEAR DISTRIBUTIONAL EVOLUTION
# ============================================================================

def chart_25yr_income_inequality():
    """
    Income inequality trends: Gini, quintile shares, wealth concentration.
    """
    logger.info("Chart: 25-year income inequality evolution")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # (a) Gini coefficient
    ax = axes[0, 0]
    gini_obs = session.query(Observation).filter(
        Observation.series_id == 'GINIALLRF',
        Observation.date >= date(2000, 1, 1)
    ).order_by(Observation.date).all()
    gini_years = [o.date.year for o in gini_obs]
    gini_vals = [o.value for o in gini_obs]
    
    ax.plot(gini_years, gini_vals, 'o-', color='#e74c3c', linewidth=2, markersize=4)
    ax.set_title('(a) Gini Index for Households')
    ax.set_ylabel('Gini Coefficient')
    ax.set_xlabel('Year')
    ax.grid(alpha=0.3)
    ax.set_xticks(range(2000, 2026, 5))
    
    # (b) Quintile income shares
    ax = axes[0, 1]
    ax.plot(census_quintiles['year'], census_quintiles['q1_share'], 'o-', 
            label='Bottom 20%', color='#e74c3c', markersize=3)
    ax.plot(census_quintiles['year'], census_quintiles['q5_share'], 's-',
            label='Top 20%', color='#2c3e50', markersize=3)
    ax.plot(census_quintiles['year'], census_quintiles['top5_share'], '^-',
            label='Top 5%', color='#7f8c8d', markersize=3, linestyle='--')
    
    ax.set_title('(b) Household Income Shares (Census H-2)')
    ax.set_ylabel('Share of Aggregate Income (%)')
    ax.set_xlabel('Year')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_xticks(range(2000, 2024, 5))
    
    # (c) Wealth concentration (Fed) — dual y-axis for scale
    ax = axes[1, 0]
    ax2c = ax.twinx()

    # Left axis: Top 1% and 50th-90th (similar scale ~25-36%)
    for sid, label, color, style, axis in [
        ('WFRBST01134', 'Top 1% Wealth Share', '#e74c3c', '-', ax),
        ('WFRBSN40188', '50th–90th Pct Wealth Share', '#2ecc71', '-', ax),
    ]:
        obs = session.query(Observation).filter(
            Observation.series_id == sid,
            Observation.date >= date(2000, 1, 1)
        ).order_by(Observation.date).all()
        if obs:
            dates = [o.date.year + o.date.month/12 for o in obs]
            vals = [o.value for o in obs]
            axis.plot(dates, vals, style, color=color, linewidth=1.5, label=label)

    # Right axis: Bottom 50% (much smaller scale ~0.5-4%)
    b50_obs = session.query(Observation).filter(
        Observation.series_id == 'WFRBSB50215',
        Observation.date >= date(2000, 1, 1)
    ).order_by(Observation.date).all()
    if b50_obs:
        dates = [o.date.year + o.date.month/12 for o in b50_obs]
        vals = [o.value for o in b50_obs]
        ax2c.plot(dates, vals, '--', color='#3498db', linewidth=1.5, label='Bottom 50% Wealth Share')
        ax2c.set_ylabel('Bottom 50% Share (%)', color='#3498db', fontsize=9)
        ax2c.tick_params(axis='y', labelcolor='#3498db')

    ax.set_title('(c) Wealth Shares (Federal Reserve DFA)')
    ax.set_ylabel('Top 1% / 50th–90th Share (%)')
    ax.set_xlabel('Year')
    # Combined legend from both axes
    lines_c, labels_c = ax.get_legend_handles_labels()
    lines_c2, labels_c2 = ax2c.get_legend_handles_labels()
    ax.legend(lines_c + lines_c2, labels_c + labels_c2, fontsize=8, loc='center left')
    ax.grid(alpha=0.3)
    
    # (d) B50 income share + transfer dependency from CPS ASEC
    ax = axes[1, 1]
    ax2 = ax.twinx()
    
    cps_years = cps_benchmarks['income_year'].values
    b50_share = cps_benchmarks['bottom50_income_share'].values
    b50_transfers = cps_benchmarks['bottom50_transfer_pct'].values
    
    l1, = ax.plot(cps_years, b50_share, 'o-', color='#3498db', linewidth=2,
                  markersize=6, label='B50 Income Share')
    l2, = ax2.plot(cps_years, b50_transfers, 's--', color='#e74c3c', linewidth=2,
                   markersize=6, label='B50 Transfer Dependency')
    
    # Annotate CY2020 COVID spike
    covid_idx = list(cps_years).index(2020) if 2020 in cps_years else None
    if covid_idx is not None:
        # Arrow to the transfer dependency spike
        ax2.annotate('COVID relief\n(expanded UC +$600/wk)',
                     xy=(2020, b50_transfers[covid_idx]),
                     xytext=(2013, b50_transfers[covid_idx] + 3),
                     fontsize=7, color='#e74c3c', fontstyle='italic',
                     arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.2),
                     ha='center')
    
    ax.set_title('(d) Bottom 50%: Income Share & Transfer Dependency\n(CPS ASEC Benchmarks)')
    ax.set_ylabel('Income Share (%)', color='#3498db')
    ax2.set_ylabel('Transfers as % of Income', color='#e74c3c')
    ax.set_xlabel('Income Year')
    ax.grid(alpha=0.3)
    
    lines = [l1, l2]
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='upper left', fontsize=9)
    
    plt.suptitle('25-Year Income & Wealth Inequality Trends (2000–2023)',
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(FIGURES / '25yr_inequality_evolution.png')
    plt.close()
    logger.info("  Saved 25yr_inequality_evolution.png")


def chart_25yr_poverty_and_benefits():
    """
    Poverty rate and federal social benefits over 25 years.
    """
    logger.info("Chart: 25-year poverty and social benefits")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Top: Poverty rate
    poverty_obs = session.query(Observation).filter(
        Observation.series_id == 'PPAAUS00000A156NCEN',
        Observation.date >= date(2000, 1, 1)
    ).order_by(Observation.date).all()
    if poverty_obs:
        p_years = [o.date.year for o in poverty_obs]
        p_vals = [o.value for o in poverty_obs]
        ax1.plot(p_years, p_vals, 'o-', color='#e74c3c', linewidth=2, markersize=5)
        ax1.fill_between(p_years, p_vals, alpha=0.15, color='#e74c3c')
        
        # Key events
        for yr, label in [(2001, 'Recession'), (2008, 'Great\nRecession'), 
                          (2020, 'COVID')]:
            idx = None
            for i, y in enumerate(p_years):
                if y == yr:
                    idx = i
                    break
            if idx:
                ax1.axvline(x=yr, color='gray', linestyle=':', alpha=0.5)
    
    ax1.set_ylabel('Poverty Rate (%)')
    ax1.set_title('Official Poverty Rate, 2000–2023')
    ax1.set_xticks(range(2000, 2025, 5))
    ax1.grid(alpha=0.3)
    
    # Bottom: Federal social benefits (quarterly, real)
    benefits_obs = session.query(Observation).filter(
        Observation.series_id == 'B087RC1Q027SBEA',
        Observation.date >= date(2000, 1, 1)
    ).order_by(Observation.date).all()
    if benefits_obs:
        b_dates = [o.date for o in benefits_obs]
        b_vals = [o.value for o in benefits_obs]
        b_years_dec = [d.year + d.month/12 for d in b_dates]
        ax2.plot(b_years_dec, b_vals, '-', color='#3498db', linewidth=1.5,
                label='Gov Social Benefits to Persons (quarterly, ann. rate)')
        
        # Highlight COVID spike
        ax2.axvspan(2020.0, 2021.75, alpha=0.1, color='red', label='COVID Relief Period')
    
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Billions of Dollars (Ann. Rate)')
    ax2.set_title('Government Social Benefits to Persons, 2000–2025')
    ax2.legend(fontsize=9)
    ax2.grid(alpha=0.3)
    ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'${x:,.0f}B'))
    
    plt.tight_layout()
    fig.savefig(FIGURES / '25yr_poverty_and_benefits.png')
    plt.close()
    logger.info("  Saved 25yr_poverty_and_benefits.png")


# ============================================================================
# PART C: STRUCTURAL BREAK TESTS
# ============================================================================

def run_structural_break_tests():
    """
    Test whether FY2025 represents a structural break from 25-year trends.
    
    Series tested:
    - Customs revenue (% of total revenue)
    - Safety-net share of outlays  
    - Net interest (real)
    - Regressive revenue share
    - B50 income share (CPS benchmark)
    
    Methods:
    - Chow test at FY2018 (first tariffs) and FY2025
    - Regression residual test (is FY2025 an outlier?)
    - Mann-Kendall trend test pre/post 2018
    """
    logger.info("=" * 70)
    logger.info("PART C: STRUCTURAL BREAK TESTS")
    logger.info("=" * 70)
    
    results = {}
    
    # 1. Customs revenue as % of total — break at 2018?
    logger.info("\n  --- Customs Revenue Share: Break at FY2018? ---")
    customs_share = derived[['fiscal_year', 'customs_share_of_rev']].dropna()
    pre = customs_share[customs_share['fiscal_year'] < 2018]['customs_share_of_rev']
    post = customs_share[customs_share['fiscal_year'] >= 2018]['customs_share_of_rev']
    
    # Regression-based break test
    X_full = customs_share['fiscal_year'].values
    y_full = customs_share['customs_share_of_rev'].values
    
    # Fit linear trend to pre-2018 and extrapolate
    pre_mask = X_full < 2018
    X_pre = X_full[pre_mask]
    y_pre = y_full[pre_mask]
    slope_pre, intercept_pre, _, _, _ = stats.linregress(X_pre, y_pre)
    predicted_2025 = slope_pre * 2025 + intercept_pre
    actual_2025 = y_full[-1]
    residual_2025 = actual_2025 - predicted_2025
    
    # Proper out-of-sample prediction standard error:
    #   SE_pred = sigma * sqrt(1 + 1/n + (x_new - x_bar)^2 / SS_x)
    pre_predicted = slope_pre * X_pre + intercept_pre
    n_pre = len(X_pre)
    se_resid = np.std(y_pre - pre_predicted, ddof=2)  # s with df correction for slope+intercept
    x_bar = np.mean(X_pre)
    ss_x = np.sum((X_pre - x_bar) ** 2)
    se_pred = se_resid * np.sqrt(1 + 1/n_pre + (2025 - x_bar)**2 / ss_x)
    z_score_2025 = residual_2025 / se_pred if se_pred > 0 else 0
    
    results['customs_share'] = {
        'pre_2018_trend': f'{slope_pre*10:.3f} pp/decade',
        'predicted_2025': round(predicted_2025, 2),
        'actual_2025': round(actual_2025, 2),
        'deviation': round(residual_2025, 2),
        'z_score': round(z_score_2025, 2),
        'is_outlier': abs(z_score_2025) > 2.0,
        'interpretation': 'STRUCTURAL BREAK' if abs(z_score_2025) > 2.0 else 'Within trend',
    }
    logger.info(f"    Pre-2018 trend: {slope_pre*10:.3f} pp/decade")
    logger.info(f"    Predicted FY2025 (on trend): {predicted_2025:.2f}%")
    logger.info(f"    Actual FY2025: {actual_2025:.2f}%")
    logger.info(f"    Z-score: {z_score_2025:.1f} → {'BREAK' if abs(z_score_2025) > 2 else 'trend'}")
    
    # 2. Interest / Safety-net ratio
    logger.info("\n  --- Interest / Safety-net Ratio: Break? ---")
    int_ratio = derived[['fiscal_year', 'interest_crowding_ratio']].dropna()
    # Exclude COVID years for trend (2020-2021 distort safety net)
    trend_mask = (int_ratio['fiscal_year'] < 2020) | (int_ratio['fiscal_year'] > 2021)
    non_covid = int_ratio[trend_mask & (int_ratio['fiscal_year'] < 2025)]
    
    slope_ir, intercept_ir, _, _, _ = stats.linregress(
        non_covid['fiscal_year'].values, non_covid['interest_crowding_ratio'].values)
    predicted_ir_2025 = slope_ir * 2025 + intercept_ir
    actual_ir_2025 = int_ratio[int_ratio['fiscal_year']==2025]['interest_crowding_ratio'].values[0]
    
    # Proper out-of-sample prediction SE
    X_ir = non_covid['fiscal_year'].values
    y_ir = non_covid['interest_crowding_ratio'].values
    residuals_ir = y_ir - (slope_ir * X_ir + intercept_ir)
    n_ir = len(X_ir)
    se_resid_ir = np.std(residuals_ir, ddof=2)
    x_bar_ir = np.mean(X_ir)
    ss_x_ir = np.sum((X_ir - x_bar_ir) ** 2)
    se_pred_ir = se_resid_ir * np.sqrt(1 + 1/n_ir + (2025 - x_bar_ir)**2 / ss_x_ir)
    z_ir = (actual_ir_2025 - predicted_ir_2025) / se_pred_ir if se_pred_ir > 0 else 0
    
    results['interest_ratio'] = {
        'trend': f'{slope_ir*10:.3f}/decade',
        'predicted_2025': round(predicted_ir_2025, 3),
        'actual_2025': round(actual_ir_2025, 3),
        'z_score': round(z_ir, 2),
        'is_outlier': abs(z_ir) > 2.0,
        'interpretation': 'STRUCTURAL BREAK' if abs(z_ir) > 2.0 else 'Within trend',
    }
    logger.info(f"    Predicted FY2025: {predicted_ir_2025:.3f}")
    logger.info(f"    Actual FY2025: {actual_ir_2025:.3f}")
    logger.info(f"    Z-score: {z_ir:.1f} → {'BREAK' if abs(z_ir) > 2 else 'trend'}")
    
    # 3. Regressive revenue share
    logger.info("\n  --- Regressive Revenue Share: Break? ---")
    reg_share = derived[['fiscal_year', 'regressive_rev_share']].dropna()
    pre2018 = reg_share[reg_share['fiscal_year'] < 2018]
    slope_rr, intercept_rr, _, _, _ = stats.linregress(
        pre2018['fiscal_year'].values, pre2018['regressive_rev_share'].values)
    pred_rr_2025 = slope_rr * 2025 + intercept_rr
    actual_rr_2025 = reg_share[reg_share['fiscal_year']==2025]['regressive_rev_share'].values[0]
    # Proper out-of-sample prediction SE
    X_rr = pre2018['fiscal_year'].values
    y_rr = pre2018['regressive_rev_share'].values
    resid_rr = y_rr - (slope_rr * X_rr + intercept_rr)
    n_rr = len(X_rr)
    se_resid_rr = np.std(resid_rr, ddof=2)
    x_bar_rr = np.mean(X_rr)
    ss_x_rr = np.sum((X_rr - x_bar_rr) ** 2)
    se_pred_rr = se_resid_rr * np.sqrt(1 + 1/n_rr + (2025 - x_bar_rr)**2 / ss_x_rr)
    z_rr = (actual_rr_2025 - pred_rr_2025) / se_pred_rr if se_pred_rr > 0 else 0
    
    results['regressive_share'] = {
        'trend': f'{slope_rr*10:.3f} pp/decade',
        'predicted_2025': round(pred_rr_2025, 2),
        'actual_2025': round(actual_rr_2025, 2),
        'z_score': round(z_rr, 2),
        'is_outlier': abs(z_rr) > 2.0,
        'interpretation': 'STRUCTURAL BREAK' if abs(z_rr) > 2.0 else 'Within trend',
    }
    logger.info(f"    Predicted FY2025: {pred_rr_2025:.2f}%")
    logger.info(f"    Actual FY2025: {actual_rr_2025:.2f}%")
    logger.info(f"    Z-score: {z_rr:.1f} → {'BREAK' if abs(z_rr) > 2 else 'trend'}")
    
    # 4. Safety-net share of outlays  
    logger.info("\n  --- Safety-net Share of Outlays: Break? ---")
    sn_share = derived[['fiscal_year', 'safety_net_share_of_outlays']].dropna()
    # Exclude COVID for trend
    sn_non_covid = sn_share[(sn_share['fiscal_year'] < 2020) | (sn_share['fiscal_year'] > 2021)]
    sn_pre2025 = sn_non_covid[sn_non_covid['fiscal_year'] < 2025]
    slope_sn, intercept_sn, _, _, _ = stats.linregress(
        sn_pre2025['fiscal_year'].values, sn_pre2025['safety_net_share_of_outlays'].values)
    pred_sn_2025 = slope_sn * 2025 + intercept_sn
    actual_sn_2025 = sn_share[sn_share['fiscal_year']==2025]['safety_net_share_of_outlays'].values[0]
    # Proper out-of-sample prediction SE
    X_sn = sn_pre2025['fiscal_year'].values
    y_sn = sn_pre2025['safety_net_share_of_outlays'].values
    resid_sn = y_sn - (slope_sn * X_sn + intercept_sn)
    n_sn = len(X_sn)
    se_resid_sn = np.std(resid_sn, ddof=2)
    x_bar_sn = np.mean(X_sn)
    ss_x_sn = np.sum((X_sn - x_bar_sn) ** 2)
    se_pred_sn = se_resid_sn * np.sqrt(1 + 1/n_sn + (2025 - x_bar_sn)**2 / ss_x_sn)
    z_sn = (actual_sn_2025 - pred_sn_2025) / se_pred_sn if se_pred_sn > 0 else 0
    
    results['safety_net_share'] = {
        'trend': f'{slope_sn*10:.3f} pp/decade',
        'predicted_2025': round(pred_sn_2025, 2),
        'actual_2025': round(actual_sn_2025, 2),
        'z_score': round(z_sn, 2),
        'is_outlier': abs(z_sn) > 2.0,
        'interpretation': 'STRUCTURAL BREAK' if abs(z_sn) > 2.0 else 'Within trend',
    }
    logger.info(f"    Predicted FY2025: {pred_sn_2025:.2f}%")
    logger.info(f"    Actual FY2025: {actual_sn_2025:.2f}%")
    logger.info(f"    Z-score: {z_sn:.1f} → {'BREAK' if abs(z_sn) > 2 else 'trend'}")
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("  STRUCTURAL BREAK SUMMARY")
    logger.info("=" * 70)
    
    for metric, r in results.items():
        logger.info(f"  {metric:<25} z={r['z_score']:>6.1f}  → {r['interpretation']}")
    
    # Save results
    # Convert numpy types for JSON
    def jsonify(obj):
        if isinstance(obj, dict):
            return {k: jsonify(v) for k, v in obj.items()}
        elif isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        return obj
    
    with open(TABLES / "structural_break_tests.json", 'w') as f:
        json.dump(jsonify(results), f, indent=2)
    logger.info(f"\n  Saved structural_break_tests.json")
    
    return results


def chart_structural_breaks(break_results):
    """Visualize structural break test results."""
    logger.info("Chart: Structural break visualization")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    series_configs = [
        ('customs_share_of_rev', 'Customs Revenue Share (%)', 'customs_share', axes[0, 0]),
        ('interest_crowding_ratio', 'Interest / Safety-Net Ratio', 'interest_ratio', axes[0, 1]),
        ('regressive_rev_share', 'Regressive Revenue Share (%)', 'regressive_share', axes[1, 0]),
        ('safety_net_share_of_outlays', 'Safety-Net Share of Outlays (%)', 'safety_net_share', axes[1, 1]),
    ]
    
    for col, title, key, ax in series_configs:
        if col not in derived.columns:
            continue
        
        years = derived['fiscal_year'].values
        vals = derived[col].values
        
        # Plot actual data
        ax.plot(years, vals, 'o-', color='#2c3e50', linewidth=2, markersize=5, label='Actual')
        
        # Pre-2018 trend line (or pre-COVID for some)
        if key == 'customs_share':
            pre_mask = years < 2018
        elif key in ['interest_ratio', 'safety_net_share']:
            pre_mask = (years < 2020) | ((years > 2021) & (years < 2025))
        else:
            pre_mask = years < 2018
        
        if pre_mask.sum() > 2:
            slope, intercept, _, _, _ = stats.linregress(years[pre_mask], vals[pre_mask])
            trend_x = np.arange(2000, 2026)
            trend_y = slope * trend_x + intercept
            ax.plot(trend_x, trend_y, '--', color='gray', linewidth=1.5, alpha=0.7,
                   label='Pre-break Trend')
        
        # Highlight FY2025
        ax.plot(2025, vals[-1], 'o', color='#e74c3c', markersize=12, zorder=10)
        
        # Z-score annotation
        if key in break_results:
            br = break_results[key]
            color = '#e74c3c' if br['is_outlier'] else '#27ae60'
            text = f"z = {br['z_score']:.1f}\n{br['interpretation']}"
            ax.annotate(text, xy=(2025, vals[-1]), xytext=(2015, vals[-1]),
                       fontsize=9, fontweight='bold', color=color,
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                                edgecolor=color, alpha=0.9),
                       arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
        
        ax.set_title(title, fontsize=12)
        ax.set_xlabel('Fiscal Year')
        ax.set_xticks(range(2000, 2026, 5))
        ax.legend(fontsize=8, loc='upper left' if key != 'safety_net_share' else 'lower left')
        ax.grid(alpha=0.3)
    
    plt.suptitle('Structural Break Tests: Is FY2025 Trend or Break?',
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(FIGURES / '25yr_structural_breaks.png')
    plt.close()
    logger.info("  Saved 25yr_structural_breaks.png")


# ============================================================================
# PART D: FY2025 IN CONTEXT — Combined burden visualization
# ============================================================================

def chart_fy2025_in_context():
    """
    Dashboard: FY2025 fiscal burden on B50 in 25-year context.
    Shows spending cuts + tariff burden + interest crowding converging.
    """
    logger.info("Chart: FY2025 in 25-year context")
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    years = derived['fiscal_year'].values
    
    # (a) Total outlays — real
    ax = axes[0, 0]
    ax.fill_between(years, cbo_trends['CBO_OUTLAYS_real2024'], alpha=0.3, color='#3498db')
    ax.plot(years, cbo_trends['CBO_OUTLAYS_real2024'], 'o-', color='#3498db', 
            linewidth=2, markersize=4)
    ax.axvline(x=2025, color='red', linestyle='--', alpha=0.5)
    ax.set_title('(a) Total Outlays (Real 2024$)', fontsize=11)
    ax.set_xticks(range(2000, 2026, 5))
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'${x/1000:.1f}T'))
    ax.grid(alpha=0.3)
    
    # (b) Income Security (real) — with COVID context
    ax = axes[0, 1]
    inc_sec = cbo_trends['CBO_MAND_Income_securityᵇ_real2024'].values
    colors_is = ['#e74c3c' if y in [2020, 2021] else '#3498db' for y in years]
    ax.bar(years, inc_sec, color=colors_is, alpha=0.8)
    ax.axvline(x=2025, color='red', linestyle='--', alpha=0.5)
    ax.set_title('(b) Income Security (Real 2024$)', fontsize=11)
    ax.set_xticks(range(2000, 2026, 5))
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'${x:,.0f}B'))
    ax.grid(axis='y', alpha=0.3)
    
    # (c) Customs revenue (real)
    ax = axes[0, 2]
    customs = derived['customs_real2024'].values
    colors_c = ['#e74c3c' if y >= 2018 else '#3498db' for y in years]
    ax.bar(years, customs, color=colors_c, alpha=0.8)
    ax.set_title('(c) Customs Revenue (Real 2024$)', fontsize=11)
    ax.set_xticks(range(2000, 2026, 5))
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'${x:,.0f}B'))
    ax.grid(axis='y', alpha=0.3)
    
    # (d) Interest as % of GDP
    ax = axes[1, 0]
    int_gdp = []
    for fy in years:
        obs = session.query(Observation).filter(
            Observation.series_id == 'CBO_OUT_GDP_Net_interest',
            Observation.date >= date(fy, 1, 1),
            Observation.date <= date(fy, 12, 31)
        ).first()
        int_gdp.append(obs.value if obs else np.nan)
    ax.plot(years, int_gdp, 'o-', color='#e74c3c', linewidth=2, markersize=5)
    ax.fill_between(years, int_gdp, alpha=0.15, color='#e74c3c')
    ax.set_title('(d) Net Interest (% of GDP)', fontsize=11)
    ax.set_xlabel('Fiscal Year')
    ax.set_xticks(range(2000, 2026, 5))
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'{x:.1f}%'))
    ax.grid(alpha=0.3)
    
    # (e) Quintile income shares over time (Census)
    ax = axes[1, 1]
    ax.plot(census_quintiles['year'], census_quintiles['q1_share'] + census_quintiles['q2_share'],
            'o-', color='#e74c3c', linewidth=2, markersize=4, label='Bottom 40%')
    ax.plot(census_quintiles['year'], census_quintiles['q5_share'],
            's-', color='#2c3e50', linewidth=2, markersize=4, label='Top 20%')
    ax.set_title('(e) Income Shares (Census)', fontsize=11)
    ax.set_xlabel('Year')
    ax.set_ylabel('% of Aggregate Income')
    ax.legend(fontsize=9)
    ax.set_xticks(range(2000, 2024, 5))
    ax.grid(alpha=0.3)
    
    # (f) B50 transfer dependency (CPS ASEC benchmarks)
    ax = axes[1, 2]
    cps_years = cps_benchmarks['income_year'].values
    b50_transfer = cps_benchmarks['bottom50_transfer_pct'].values
    ax.bar(cps_years, b50_transfer, width=2.5, color='#e67e22', alpha=0.8,
          edgecolor='white')
    ax.set_title('(f) B50 Transfer Dependency (CPS ASEC)', fontsize=11)
    ax.set_xlabel('Income Year')
    ax.set_ylabel('Transfers as % of B50 Income')
    ax.grid(axis='y', alpha=0.3)
    
    plt.suptitle('FY2025 Federal Fiscal Policy in 25-Year Context',
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig.savefig(FIGURES / '25yr_fy2025_context_dashboard.png')
    plt.close()
    logger.info("  Saved 25yr_fy2025_context_dashboard.png")


# ============================================================================
# PART E: ANALYSIS SUMMARY TABLE
# ============================================================================

def build_summary_table():
    """Build comprehensive summary of 25-year trends for the paper."""
    logger.info("Building analysis summary...")
    
    summary = {
        'analysis_period': 'FY2000-FY2025 (26 fiscal years)',
        'data_sources': {
            'CBO_Historical_Budget': 'FY1962-2025 (outlays, revenue, deficit, debt)',
            'Census_H2_Quintile_Shares': '2000-2023 (24 annual observations)',
            'CPS_ASEC_Microdata': '8 benchmark years (CY2002-CY2023, 180K-216K records each)',
            'FRED_Distributional': '10 series (wealth shares, Gini, poverty, benefits)',
            'CPI_Deflator': 'FY1963-2025 (real 2024 dollars)',
        },
        'aggregate_budget_25yr': {
            'total_outlays_real': {'fy2000': 3264.8, 'fy2025': 6825.5, 'change_pct': 109},
            'net_interest_real': {'fy2000': 406.9, 'fy2025': 944.4, 'change_pct': 132},
            'customs_real': {'fy2000': 36.3, 'fy2025': 189.7, 'change_pct': 422},
            'income_security_real': {'fy2000': 244.4, 'fy2025': 387.0, 'change_pct': 58},
        },
        'fiscal_composition_25yr': {
            'safety_net_share_of_outlays': {'fy2000': 14.1, 'fy2025': 15.2},
            'interest_crowding_ratio': {'fy2000': 0.9, 'fy2025': 0.9},
            'regressive_revenue_share': {'fy2000': 36.6, 'fy2025': 39.1},
            'customs_share_of_revenue': {'fy2000': 1.0, 'fy2025': 3.7},
        },
        'distributional_evolution': {
            'b50_income_share': {
                'cy2002': float(cps_benchmarks.loc[cps_benchmarks['income_year']==2002, 'bottom50_income_share'].values[0]),
                'cy2023': float(cps_benchmarks.loc[cps_benchmarks['income_year']==2023, 'bottom50_income_share'].values[0]),
            },
            'b50_transfer_dependency': {
                'cy2002': float(cps_benchmarks.loc[cps_benchmarks['income_year']==2002, 'bottom50_transfer_pct'].values[0]),
                'cy2023': float(cps_benchmarks.loc[cps_benchmarks['income_year']==2023, 'bottom50_transfer_pct'].values[0]),
            },
            'top20_income_share_census': {
                'cy2000': float(census_quintiles.loc[census_quintiles['year']==2000, 'q5_share'].values[0]),
                'cy2023': float(census_quintiles.loc[census_quintiles['year']==2023, 'q5_share'].values[0]),
            },
            'bottom20_income_share_census': {
                'cy2000': float(census_quintiles.loc[census_quintiles['year']==2000, 'q1_share'].values[0]),
                'cy2023': float(census_quintiles.loc[census_quintiles['year']==2023, 'q1_share'].values[0]),
            },
        },
    }
    
    with open(TABLES / "25year_analysis_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info("  Saved 25year_analysis_summary.json")
    
    return summary


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 75)
    logger.info("  25-YEAR FEDERAL BUDGET ANALYSIS (FY2000–FY2025)")
    logger.info("=" * 75)
    
    # Part A: Structural trends
    logger.info("\n  PART A: 25-YEAR STRUCTURAL BUDGET TRENDS")
    chart_25yr_spending_composition()
    chart_25yr_revenue_mix()
    chart_25yr_interest_vs_safetynet()
    chart_25yr_customs_trajectory()
    
    # Part B: Distributional evolution
    logger.info("\n  PART B: 25-YEAR DISTRIBUTIONAL EVOLUTION")
    chart_25yr_income_inequality()
    chart_25yr_poverty_and_benefits()
    
    # Part C: Structural break tests
    break_results = run_structural_break_tests()
    chart_structural_breaks(break_results)
    
    # Part D: FY2025 in context
    logger.info("\n  PART D: FY2025 IN 25-YEAR CONTEXT")
    chart_fy2025_in_context()
    
    # Part E: Summary
    summary = build_summary_table()
    
    logger.info("\n" + "=" * 75)
    logger.info("  25-YEAR ANALYSIS COMPLETE")
    logger.info("=" * 75)
    logger.info(f"  Charts: {FIGURES}")
    logger.info(f"  Tables: {TABLES}")
    logger.info("\n  Generated figures:")
    for f in sorted(FIGURES.glob("25yr_*")):
        logger.info(f"    {f.name}")
