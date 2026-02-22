"""
=============================================================================
VISUALIZATION SUITE — Federal Budget & Taxpayer Welfare
=============================================================================
Generates all charts for the hypothesis analysis:
  1. Budget composition stacked area (CBO outlays over time)
  2. Revenue composition (who pays what)
  3. Interest vs Safety-net spending
  4. CPI essentials comparison (tariff impact)
  5. Corporate profits vs wages indexed
  6. Customs revenue spike
  7. Deficit trend with policy markers
  8. Sankey flow diagram: "Where Did the Money Go?"
=============================================================================
"""

import sys, os, warnings
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import seaborn as sns
from datetime import date

from src.utils.config import load_config, get_output_path, setup_logging
from src.database.models import get_session, Observation, EconomicSeries
from src.analysis.policy_impact import load_series

setup_logging()
config = load_config()
FIGURES = get_output_path("figures")
os.makedirs(FIGURES, exist_ok=True)

session = get_session()

# Style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('colorblind')
DPI = 150

POLICY_EVENTS = {
    'Inauguration': '2025-01-20',
    'China 10% Tariff': '2025-02-04',
    'Canada/Mexico 25%': '2025-03-04',
    'Reciprocal Tariffs': '2025-04-02',
}


def get_cbo_annual(series_id, start_year=2000, end_year=2025):
    """Get annual CBO data as year→value dict."""
    data = {}
    for yr in range(start_year, end_year + 1):
        obs = session.query(Observation).filter(
            Observation.series_id == series_id,
            Observation.date >= date(yr, 1, 1),
            Observation.date <= date(yr, 12, 31)
        ).first()
        if obs:
            data[yr] = obs.value
    return data


# ============================================================================
# CHART 1: Federal Outlay Composition (Stacked Area)
# ============================================================================

def chart_outlay_composition():
    print("  [1] Outlay Composition...")
    components = {
        'Social Security': 'CBO_MAND_Social_Security',
        'Medicare + Medicaid': None,  # combined
        'Income Security': 'CBO_MAND_Income_securityᵇ',
        'Veterans': 'CBO_MAND_Veterans_programs',
        'Discretionary': 'CBO_OUT_Discretionary',
        'Net Interest': 'CBO_OUT_Net_interest',
    }

    years = list(range(2000, 2026))
    df = pd.DataFrame(index=years)

    for label, sid in components.items():
        if sid:
            data = get_cbo_annual(sid, 2000, 2025)
            df[label] = pd.Series(data)

    # Combine Medicare + Medicaid
    medicare = get_cbo_annual('CBO_MAND_Medicareᵃ', 2000, 2025)
    medicaid = get_cbo_annual('CBO_MAND_Medicaid', 2000, 2025)
    combined = {}
    for yr in years:
        m1 = medicare.get(yr, 0)
        m2 = medicaid.get(yr, 0)
        if m1 or m2:
            combined[yr] = m1 + m2
    df['Medicare + Medicaid'] = pd.Series(combined)

    df = df.dropna(how='all')
    cols = ['Social Security', 'Medicare + Medicaid', 'Income Security',
            'Veterans', 'Discretionary', 'Net Interest']
    df = df[[c for c in cols if c in df.columns]].fillna(0)

    fig, ax = plt.subplots(figsize=(14, 8))
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#607D8B', '#F44336']
    ax.stackplot(df.index, [df[c] for c in df.columns], labels=df.columns,
                 colors=colors, alpha=0.85)

    ax.axvline(2025, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(2025.1, ax.get_ylim()[1] * 0.95, '2025 Policy\nShift',
            fontsize=10, color='red', fontweight='bold')

    ax.set_title('Federal Outlay Composition (FY2000–FY2025)', fontsize=16, fontweight='bold')
    ax.set_ylabel('Billions of Dollars', fontsize=12)
    ax.set_xlabel('Fiscal Year', fontsize=12)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}B'))
    ax.set_xlim(2000, 2025)
    plt.tight_layout()
    fig.savefig(FIGURES / '01_outlay_composition.png', dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ============================================================================
# CHART 2: Revenue Composition — Who Pays What?
# ============================================================================

def chart_revenue_composition():
    print("  [2] Revenue Composition...")
    rev = {
        'Individual Income': 'CBO_REV_Individual_income_taxes',
        'Payroll (Regressive)': 'CBO_REV_Payroll_taxes',
        'Corporate Income': 'CBO_REV_Corporate_income_taxes',
        'Excise (Regressive)': 'CBO_REV_Excise_taxes',
        'Customs/Tariffs': 'CBO_REV_Customs_duties',
    }

    years = list(range(2000, 2026))
    df = pd.DataFrame(index=years)
    for label, sid in rev.items():
        data = get_cbo_annual(sid, 2000, 2025)
        df[label] = pd.Series(data)
    df = df.dropna(how='all').fillna(0)

    fig, ax = plt.subplots(figsize=(14, 8))
    colors = ['#1976D2', '#F44336', '#4CAF50', '#FF9800', '#9C27B0']
    ax.stackplot(df.index, [df[c] for c in df.columns], labels=df.columns,
                 colors=colors, alpha=0.85)
    ax.axvline(2025, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax.set_title('Federal Revenue by Source (FY2000–FY2025)', fontsize=16, fontweight='bold')
    ax.set_ylabel('Billions of Dollars')
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}B'))
    ax.set_xlim(2000, 2025)

    # Annotate tariff spike
    if 2025 in df.index:
        customs_25 = df.loc[2025, 'Customs/Tariffs']
        customs_24 = df.loc[2024, 'Customs/Tariffs'] if 2024 in df.index else 0
        if customs_25 > customs_24 * 1.5:
            total_below = df.loc[2025, ['Individual Income', 'Payroll (Regressive)',
                                        'Corporate Income', 'Excise (Regressive)']].sum()
            ax.annotate(f'Tariff Spike\n${customs_25:.0f}B (+{((customs_25-customs_24)/customs_24)*100:.0f}%)',
                        xy=(2025, total_below + customs_25/2),
                        xytext=(2022, total_below + customs_25*1.5),
                        fontsize=10, fontweight='bold', color='#9C27B0',
                        arrowprops=dict(arrowstyle='->', color='#9C27B0'))

    plt.tight_layout()
    fig.savefig(FIGURES / '02_revenue_composition.png', dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ============================================================================
# CHART 3: Net Interest vs Safety-Net Spending
# ============================================================================

def chart_interest_vs_safety_net():
    print("  [3] Interest vs Safety Net...")
    years = list(range(2000, 2026))
    interest = get_cbo_annual('CBO_OUT_Net_interest', 2000, 2025)
    income_sec = get_cbo_annual('CBO_MAND_Income_securityᵇ', 2000, 2025)
    medicaid = get_cbo_annual('CBO_MAND_Medicaid', 2000, 2025)

    df = pd.DataFrame({
        'Net Interest': pd.Series(interest),
        'Income Security': pd.Series(income_sec),
        'Medicaid': pd.Series(medicaid),
    })
    df = df.dropna(how='all')
    df['Safety Net Total'] = df['Income Security'].fillna(0) + df['Medicaid'].fillna(0)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.fill_between(df.index, df['Net Interest'], alpha=0.3, color='#F44336')
    ax.plot(df.index, df['Net Interest'], 'o-', color='#F44336', linewidth=2.5,
            label='Net Interest Payments', markersize=5)
    ax.plot(df.index, df['Safety Net Total'], 's-', color='#2196F3', linewidth=2.5,
            label='Safety Net (Medicaid + Income Security)', markersize=5)
    ax.plot(df.index, df['Income Security'], '^--', color='#FF9800', linewidth=1.5,
            label='Income Security (SNAP, EITC, etc.)', markersize=4, alpha=0.7)

    # Highlight crossover region
    if any(df['Net Interest'] > df['Safety Net Total']):
        cross_yr = df[df['Net Interest'] > df['Safety Net Total']].index[0]
        ax.axvspan(cross_yr - 0.5, df.index[-1] + 0.5, alpha=0.1, color='red',
                   label='Interest > Safety Net')

    # -- Clear x-axis year labels --
    ax.set_xticks(range(2000, 2026, 1))
    ax.set_xticklabels([str(yr) if yr % 5 == 0 else '' for yr in range(2000, 2026)],
                        fontsize=10)
    # Add minor ticks for every year
    ax.tick_params(axis='x', which='major', length=6)
    ax.set_xlim(1999.5, 2026)

    # -- FY2025 vertical marker --
    ax.axvline(2025, color='gray', linestyle=':', linewidth=1.5, alpha=0.7)
    ax.text(2025.1, ax.get_ylim()[1] * 0.97, 'FY2025', fontsize=9,
            color='gray', va='top', fontstyle='italic')

    # -- Annotate the COVID spike --
    if 2020 in df.index:
        covid_val = df.loc[2020, 'Income Security']
        ax.annotate(f'COVID Relief\nFY2020: ${covid_val:,.0f}B',
                    xy=(2020, covid_val), xytext=(2015, covid_val * 1.05),
                    fontsize=9, fontweight='bold', color='#FF9800',
                    arrowprops=dict(arrowstyle='->', color='#FF9800', lw=1.5),
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF3E0', alpha=0.8))
    if 2021 in df.index:
        covid_val_21 = df.loc[2021, 'Income Security']
        ax.annotate(f'FY2021: ${covid_val_21:,.0f}B',
                    xy=(2021, covid_val_21), xytext=(2021.5, covid_val_21 * 1.08),
                    fontsize=8, color='#FF9800',
                    arrowprops=dict(arrowstyle='->', color='#FF9800', lw=1))

    ax.set_title('Net Interest Payments vs Safety-Net Spending\n',
                 fontsize=16, fontweight='bold')
    ax.text(0.5, 1.01, 'FY2000–FY2025  |  Source: CBO Historical Budget Data',
            transform=ax.transAxes, fontsize=10, ha='center', color='#666',
            fontstyle='italic')
    ax.set_xlabel('Fiscal Year', fontsize=11)
    ax.set_ylabel('Billions of Dollars', fontsize=11)
    ax.legend(fontsize=10, framealpha=0.9, loc='upper left')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}B'))

    # Annotate latest interest
    if len(df) > 0:
        latest_yr = df.index[-1]
        int_val = df.loc[latest_yr, 'Net Interest']
        sn_val = df.loc[latest_yr, 'Safety Net Total']
        ratio = (int_val / sn_val) * 100 if sn_val > 0 else 0
        ax.text(latest_yr + 0.3, int_val, f'FY{latest_yr}: ${int_val:.0f}B\n({ratio:.0f}% of\nsafety net)',
                fontsize=9, color='#F44336', fontweight='bold')

    plt.tight_layout()
    fig.savefig(FIGURES / '03_interest_vs_safety_net.png', dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ============================================================================
# CHART 4: CPI Essentials — Tariff Impact on Consumer Prices
# ============================================================================

def chart_cpi_essentials():
    print("  [4] CPI Essentials...")
    cpi_series = {
        'All Items': 'CPIAUCSL',
        'Food at Home': 'CUSR0000SAF11',
        'Shelter': 'CUSR0000SAH1',
        'Medical Care': 'CPIMEDSL',
        'Apparel': 'CPIAPPSL',
        'Gasoline': 'CUSR0000SETB01',
    }

    fig, ax = plt.subplots(figsize=(14, 7))
    colors = ['#000000', '#F44336', '#2196F3', '#4CAF50', '#9C27B0', '#FF9800']

    for (label, sid), color in zip(cpi_series.items(), colors):
        s = load_series(sid, '2020-01-01')
        if not s.empty:
            # Index to Jan 2020 = 100
            base = s.iloc[0]
            indexed = (s / base) * 100
            linewidth = 3 if label == 'All Items' else 1.5
            style = '-' if label == 'All Items' else '--'
            ax.plot(indexed.index, indexed.values, style, color=color,
                    linewidth=linewidth, label=label, alpha=0.85)

    # Add vertical lines for tariff events
    tariff_colors = plt.cm.Reds(np.linspace(0.4, 0.8, len(POLICY_EVENTS)))
    for (event, dt), c in zip(POLICY_EVENTS.items(), tariff_colors):
        ax.axvline(pd.Timestamp(dt), color=c, linestyle=':', linewidth=1.2, alpha=0.7)
        ax.text(pd.Timestamp(dt), ax.get_ylim()[1] if ax.get_ylim()[1] > 100 else 130,
                f' {event}', rotation=90, va='top', fontsize=7, color=c)

    ax.set_title('Consumer Price Index — Essentials vs Overall (Jan 2020 = 100)',
                 fontsize=16, fontweight='bold')
    ax.set_ylabel('Index (Jan 2020 = 100)')
    ax.legend(fontsize=10, framealpha=0.9, loc='upper left')
    ax.axhline(100, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    fig.autofmt_xdate()
    plt.tight_layout()
    fig.savefig(FIGURES / '04_cpi_essentials.png', dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ============================================================================
# CHART 5: Corporate Profits vs Wages (indexed)
# ============================================================================

def chart_profits_vs_wages():
    print("  [5] Profits vs Wages...")
    series_map = {
        'Corporate Profits (After Tax)': 'CP',
        'S&P 500': 'SP500',
        'Real Disposable Income': 'DSPIC96',
    }

    fig, ax = plt.subplots(figsize=(14, 7))
    colors = ['#F44336', '#4CAF50', '#2196F3']

    for (label, sid), color in zip(series_map.items(), colors):
        s = load_series(sid, '2019-01-01')
        if not s.empty:
            base = s.iloc[0]
            indexed = (s / base) * 100
            ax.plot(indexed.index, indexed.values, '-', color=color,
                    linewidth=2, label=label)

    # CBO annual wage data
    wages = get_cbo_annual('CBO_WAGES', 2019, 2025)
    if wages:
        w_series = pd.Series(wages)
        base = w_series.iloc[0]
        w_indexed = (w_series / base) * 100
        ax.plot([pd.Timestamp(f'{yr}-06-30') for yr in w_indexed.index], w_indexed.values,
                's-', color='#FF9800', linewidth=2, label='CBO: Wages & Salaries', markersize=8)

    for event, dt in POLICY_EVENTS.items():
        if event == 'Inauguration':
            ax.axvline(pd.Timestamp(dt), color='red', linestyle='--', linewidth=1.5, alpha=0.5)

    ax.set_title('Corporate Profits vs Household Income (Jan 2019 = 100)',
                 fontsize=16, fontweight='bold')
    ax.set_ylabel('Index (Jan 2019 = 100)')
    ax.legend(fontsize=10, framealpha=0.9)
    ax.axhline(100, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    fig.autofmt_xdate()
    plt.tight_layout()
    fig.savefig(FIGURES / '05_profits_vs_wages.png', dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ============================================================================
# CHART 6: Customs Revenue Spike (Tariff Revenue History)
# ============================================================================

def chart_customs_revenue():
    print("  [6] Customs Revenue...")
    customs = get_cbo_annual('CBO_REV_Customs_duties', 1990, 2025)
    if not customs:
        return

    fig, ax = plt.subplots(figsize=(14, 7))
    years = list(customs.keys())
    vals = list(customs.values())

    bars = ax.bar(years, vals, color='#9C27B0', alpha=0.7, edgecolor='#7B1FA2')

    # Highlight FY2019 (first tariff spike)
    if 2019 in customs:
        idx_19 = years.index(2019)
        bars[idx_19].set_color('#FF9800')
        bars[idx_19].set_alpha(1.0)
        ax.annotate(f'FY2019: ${customs[2019]:.0f}B\n(Section 301\nChina tariffs,\n+71% YoY)',
                    xy=(2019, customs[2019]),
                    xytext=(2012, customs[2019] * 1.3),
                    fontsize=9, fontweight='bold', color='#FF9800',
                    arrowprops=dict(arrowstyle='->', color='#FF9800', lw=1.5),
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF3E0', alpha=0.8))

    # Highlight FY2025 (major tariff spike)
    if 2025 in customs:
        idx_25 = years.index(2025)
        bars[idx_25].set_color('#F44336')
        bars[idx_25].set_alpha(1.0)
        ax.annotate(f'FY2025: ${customs[2025]:.0f}B\n(Liberation Day +\nuniversal tariffs,\n+153% YoY)',
                    xy=(2025, customs[2025]),
                    xytext=(2017, customs[2025] * 0.85),
                    fontsize=10, fontweight='bold', color='#F44336',
                    arrowprops=dict(arrowstyle='->', color='#F44336', lw=2),
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFEBEE', alpha=0.8))

    # -- Clear x-axis year labels --
    ax.set_xticks(range(min(years), max(years) + 1, 1))
    ax.set_xticklabels([str(yr) if yr % 5 == 0 else '' for yr in range(min(years), max(years) + 1)],
                        fontsize=10)
    ax.tick_params(axis='x', which='major', length=6)
    ax.set_xlim(min(years) - 0.8, max(years) + 0.8)

    ax.set_title('Customs Duties / Tariff Revenue\n',
                 fontsize=16, fontweight='bold')
    ax.text(0.5, 1.01, 'FY1990–FY2025  |  Source: CBO Historical Budget Data',
            transform=ax.transAxes, fontsize=10, ha='center', color='#666',
            fontstyle='italic')
    ax.set_xlabel('Fiscal Year', fontsize=11)
    ax.set_ylabel('Billions of Dollars', fontsize=11)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}B'))
    plt.tight_layout()
    fig.savefig(FIGURES / '06_customs_revenue_spike.png', dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ============================================================================
# CHART 7: Deficit Trend with Policy Periods
# ============================================================================

def chart_deficit_trend():
    print("  [7] Deficit Trend...")
    revenues = get_cbo_annual('CBO_REVENUES', 2000, 2025)
    outlays = get_cbo_annual('CBO_OUTLAYS', 2000, 2025)

    if not revenues or not outlays:
        return

    years = sorted(set(revenues.keys()) & set(outlays.keys()))
    deficits = {yr: revenues[yr] - outlays[yr] for yr in years}

    fig, ax = plt.subplots(figsize=(14, 7))
    vals = [deficits[yr] for yr in years]
    colors_bars = ['#F44336' if v < 0 else '#4CAF50' for v in vals]
    ax.bar(years, vals, color=colors_bars, alpha=0.8, edgecolor='#333')

    # Policy period annotations
    periods = [
        (2001, 2009, 'Bush Tax Cuts', '#FFE0B2'),
        (2009, 2012, 'Great Recession\nStimulus', '#BBDEFB'),
        (2018, 2020, 'TCJA + COVID', '#E1BEE7'),
        (2025, 2025.8, '2025 Tariffs\n& Cuts', '#FFCDD2'),
    ]
    for start, end, label, color in periods:
        ax.axvspan(start - 0.5, end + 0.5, alpha=0.2, color=color)
        ax.text((start + end) / 2, ax.get_ylim()[0] * 0.95, label,
                ha='center', fontsize=8, fontstyle='italic')

    ax.axhline(0, color='black', linewidth=1)
    ax.set_title('Federal Budget Deficit (Revenue − Outlays)', fontsize=16, fontweight='bold')
    ax.set_ylabel('Billions of Dollars (Negative = Deficit)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}B'))
    plt.tight_layout()
    fig.savefig(FIGURES / '07_deficit_trend.png', dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ============================================================================
# CHART 8: Sankey Flow — "Where Did the Money Go?" (FY2020 → FY2024)
# ============================================================================

def chart_sankey_flow():
    print("  [8] Sankey Flow Diagram...")
    try:
        import plotly.graph_objects as go
    except ImportError:
        print("    Plotly not available, skipping Sankey")
        return

    # Data: Changes from FY2020 to FY2024
    # Revenue side
    rev_indiv_change = (get_cbo_annual('CBO_REV_Individual_income_taxes', 2024, 2024).get(2024, 0)
                        - get_cbo_annual('CBO_REV_Individual_income_taxes', 2020, 2020).get(2020, 0))
    rev_corp_change = (get_cbo_annual('CBO_REV_Corporate_income_taxes', 2024, 2024).get(2024, 0)
                       - get_cbo_annual('CBO_REV_Corporate_income_taxes', 2020, 2020).get(2020, 0))
    rev_payroll_change = (get_cbo_annual('CBO_REV_Payroll_taxes', 2024, 2024).get(2024, 0)
                          - get_cbo_annual('CBO_REV_Payroll_taxes', 2020, 2020).get(2020, 0))

    # Spending side changes
    interest_change = (get_cbo_annual('CBO_OUT_Net_interest', 2024, 2024).get(2024, 0)
                       - get_cbo_annual('CBO_OUT_Net_interest', 2020, 2020).get(2020, 0))
    ss_change = (get_cbo_annual('CBO_MAND_Social_Security', 2024, 2024).get(2024, 0)
                 - get_cbo_annual('CBO_MAND_Social_Security', 2020, 2020).get(2020, 0))
    income_sec_change = (get_cbo_annual('CBO_MAND_Income_securityᵇ', 2024, 2024).get(2024, 0)
                         - get_cbo_annual('CBO_MAND_Income_securityᵇ', 2020, 2020).get(2020, 0))
    medicaid_change = (get_cbo_annual('CBO_MAND_Medicaid', 2024, 2024).get(2024, 0)
                       - get_cbo_annual('CBO_MAND_Medicaid', 2020, 2020).get(2020, 0))

    # Nodes: Sources → Federal Budget → Destinations
    labels = [
        # Source nodes (0-2)
        "Individual Income Tax\n(+$" + f"{rev_indiv_change:.0f}B)",
        "Payroll Tax\n(+$" + f"{rev_payroll_change:.0f}B)",
        "Corporate Tax\n(+$" + f"{rev_corp_change:.0f}B)",
        # Central node (3)
        "Federal Budget\nΔ FY2020→FY2024",
        # Destination nodes (4-8)
        f"Net Interest (Bondholders)\n(+${interest_change:.0f}B)",
        f"Social Security\n(+${ss_change:.0f}B)",
        f"Medicaid\n(+${medicaid_change:.0f}B)",
        f"Income Security (SNAP, etc.)\n(${income_sec_change:.0f}B)",
        "Higher Deficit\n(Debt Accumulation)",
    ]

    # Color by node
    node_colors = [
        '#1976D2', '#F44336', '#4CAF50',  # Revenue sources
        '#607D8B',                          # Central
        '#F44336', '#2196F3', '#4CAF50', '#FF9800', '#9E9E9E'  # Destinations
    ]

    # Links: source → target, value
    # Revenue → Budget
    sources = [0, 1, 2]
    targets = [3, 3, 3]
    values = [max(rev_indiv_change, 1), max(rev_payroll_change, 1), max(rev_corp_change, 1)]

    # Budget → Destinations
    sources += [3, 3, 3, 3, 3]
    targets += [4, 5, 6, 7, 8]
    interest_abs = abs(interest_change)
    ss_abs = abs(ss_change)
    medicaid_abs = abs(medicaid_change)
    income_sec_abs = abs(income_sec_change)
    deficit_flow = max(abs(rev_indiv_change + rev_payroll_change + rev_corp_change
                          - interest_abs - ss_abs - medicaid_abs), 100)
    values += [interest_abs, ss_abs, medicaid_abs, income_sec_abs, deficit_flow]

    link_colors = [
        'rgba(25,118,210,0.3)', 'rgba(244,67,54,0.3)', 'rgba(76,175,80,0.3)',
        'rgba(244,67,54,0.5)', 'rgba(33,150,243,0.3)', 'rgba(76,175,80,0.3)',
        'rgba(255,152,0,0.3)', 'rgba(158,158,158,0.3)',
    ]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20, thickness=30,
            label=labels,
            color=node_colors,
        ),
        link=dict(
            source=sources, target=targets,
            value=values, color=link_colors,
        ),
    )])

    fig.update_layout(
        title_text="Where Did the Money Go? Federal Budget Shifts (FY2020 → FY2024)",
        title_font_size=18,
        font_size=11,
        height=600, width=1100,
    )
    fig.write_html(str(FIGURES / '08_sankey_budget_flow.html'))
    try:
        fig.write_image(str(FIGURES / '08_sankey_budget_flow.png'), scale=2)
        print("    Saved Sankey (HTML + PNG)")
    except (ValueError, ImportError):
        print("    Saved Sankey (HTML only — install kaleido for PNG export)")


# ============================================================================
# CHART 9: Waterfall — Income Security Decline
# ============================================================================

def chart_income_security_waterfall():
    print("  [9] Income Security Waterfall...")
    income_sec = get_cbo_annual('CBO_MAND_Income_securityᵇ', 2019, 2025)
    if not income_sec:
        return

    years = sorted(income_sec.keys())
    vals = [income_sec[yr] for yr in years]

    fig, ax = plt.subplots(figsize=(12, 7))

    changes = [vals[0]]  # Base
    for i in range(1, len(vals)):
        changes.append(vals[i] - vals[i - 1])

    bottoms = [0]
    for i in range(1, len(changes)):
        bottoms.append(bottoms[i - 1] + changes[i - 1])

    colors_bars = ['#2196F3']  # Base
    for c in changes[1:]:
        colors_bars.append('#4CAF50' if c > 0 else '#F44336')

    labels = [f'FY{yr}' if i == 0 else f'Δ{yr}' for i, yr in enumerate(years)]
    bars = ax.bar(labels, [abs(c) for c in changes], bottom=[max(b, 0) if i > 0 else 0 for i, b in enumerate(bottoms)],
                  color=colors_bars, edgecolor='#333', alpha=0.85)

    # Actually use cumulative values for clarity
    ax.clear()
    bars = ax.bar([f'FY{yr}' for yr in years], vals,
                  color=['#F44336' if v < vals[0] else '#2196F3' for v in vals],
                  edgecolor='#333', alpha=0.85)

    # Add value labels
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                f'${val:.0f}B', ha='center', fontsize=10, fontweight='bold')

    # Highlight COVID spike and post-COVID drop
    ax.annotate('COVID\nSpending\nSurge', xy=(1, vals[1]), xytext=(1, vals[1] + 100),
                fontsize=9, ha='center', color='#4CAF50',
                arrowprops=dict(arrowstyle='->', color='#4CAF50'))

    ax.set_title('Income Security Spending (SNAP, EITC, etc.) — Rise and Fall',
                 fontsize=16, fontweight='bold')
    ax.set_ylabel('Billions of Dollars')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}B'))
    plt.tight_layout()
    fig.savefig(FIGURES / '09_income_security_waterfall.png', dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ============================================================================
# CHART 10: Interest as % of GDP Over Time
# ============================================================================

def chart_interest_gdp():
    print("  [10] Interest as % GDP...")
    interest_gdp = get_cbo_annual('CBO_OUT_GDP_Net_interest', 1990, 2025)
    if not interest_gdp:
        return

    fig, ax = plt.subplots(figsize=(14, 6))
    years_list = sorted(interest_gdp.keys())
    vals = [interest_gdp[yr] for yr in years_list]

    ax.fill_between(years_list, vals, alpha=0.3, color='#F44336')
    ax.plot(years_list, vals, 'o-', color='#F44336', linewidth=2.5, markersize=5)

    # Historical context lines
    avg = np.mean(vals)
    ax.axhline(avg, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.text(years_list[0], avg + 0.05, f'Avg: {avg:.1f}%', fontsize=9, color='gray')

    # Annotate current
    if years_list:
        latest_yr = years_list[-1]
        latest_val = interest_gdp[latest_yr]
        ax.annotate(f'{latest_val:.1f}%\n(FY{latest_yr})',
                    xy=(latest_yr, latest_val),
                    xytext=(latest_yr - 3, latest_val + 0.5),
                    fontsize=12, fontweight='bold', color='#F44336',
                    arrowprops=dict(arrowstyle='->', color='#F44336'))

    ax.set_title('Net Interest Payments as % of GDP (FY1990–FY2025)',
                 fontsize=16, fontweight='bold')
    ax.set_ylabel('Percent of GDP')
    ax.set_xlabel('Fiscal Year')
    plt.tight_layout()
    fig.savefig(FIGURES / '10_interest_pct_gdp.png', dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\nGenerating visualizations...")
    print(f"Output: {FIGURES}\n")

    chart_outlay_composition()
    chart_revenue_composition()
    chart_interest_vs_safety_net()
    chart_cpi_essentials()
    chart_profits_vs_wages()
    chart_customs_revenue()
    chart_deficit_trend()
    chart_sankey_flow()
    chart_income_security_waterfall()
    chart_interest_gdp()

    session.close()
    print(f"\nAll charts saved to {FIGURES}")
    print("Done.")
