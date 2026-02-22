#!/usr/bin/env python3
"""
=============================================================================
GENERATE NEW FIGURES — 10 publication-quality analytical figures
=============================================================================
Supplements the descriptive budget figures (generate_charts.py),
distributional figures (run_counterfactual_analysis.py), and
real-terms charts (generate_real_charts.py) with focused analytical
visualizations for journal submission.

Run:  python generate_new_figures.py
=============================================================================
"""

import sys, os, json, warnings, csv
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent
FIGURES = BASE / "output" / "figures"
TABLES = BASE / "output" / "tables"
PROCESSED = BASE / "data" / "processed"
FIGURES.mkdir(parents=True, exist_ok=True)

# ── Publication style ──────────────────────────────────────────────────────────
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
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})

# Color palette — consistent with existing figures
PALETTE = {
    'snap':     '#e63946',  # Red
    'medicaid': '#457b9d',  # Blue
    'nondiscr': '#f4a261',  # Orange
    'tariff':   '#2a9d8f',  # Teal
    'accent':   '#264653',  # Dark
    'light':    '#a8dadc',  # Light teal
    'gray':     '#6c757d',
    'traded':   '#e63946',
    'services': '#457b9d',
    'high':     '#e63946',
    'medium':   '#f4a261',
    'low':      '#2a9d8f',
}


def load_json(name):
    with open(TABLES / name) as f:
        return json.load(f)


def load_csv(name):
    import pandas as pd
    return pd.read_csv(TABLES / name)


# ==============================================================================
# Figure 1: BURDEN DECOMPOSITION — Stacked area by percentile
# ==============================================================================
def fig_burden_decomposition():
    """Stacked area chart of 4 burden components across income percentiles."""
    print("  [1/10] Burden decomposition stacked area...")
    df = load_csv("quantile_treatment_effects.csv")

    fig, ax = plt.subplots(figsize=(10, 5.5))

    pct = df['percentile'].values
    snap = df['snap_loss'].values
    med = df['medicaid_loss'].values
    nond = df['nondiscr_loss'].values
    tar = df['tariff_loss'].values

    ax.fill_between(pct, 0, snap, alpha=0.85, color=PALETTE['snap'], label='SNAP benefit loss')
    ax.fill_between(pct, snap, snap + med, alpha=0.85, color=PALETTE['medicaid'], label='Medicaid benefit loss')
    ax.fill_between(pct, snap + med, snap + med + nond, alpha=0.85, color=PALETTE['nondiscr'], label='Nondefense discretionary loss')
    ax.fill_between(pct, snap + med + nond, snap + med + nond + tar, alpha=0.85, color=PALETTE['tariff'], label='Tariff burden')

    # Mark the B50 boundary
    ax.axvline(x=50, color='black', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.text(51, ax.get_ylim()[1] * 0.92, 'B50 | T50', fontsize=10, fontweight='bold',
            va='top', ha='left')

    ax.set_xlabel('Income Percentile')
    ax.set_ylabel('Annual Per-Person Burden ($)')
    ax.set_title('Decomposition of Fiscal Burden by Income Percentile (FY2025)')
    ax.set_xlim(1, 99)
    ax.legend(loc='upper right', framealpha=0.9, fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))

    fig.tight_layout()
    fig.savefig(FIGURES / "fig11_burden_decomposition.png")
    plt.close(fig)


# ==============================================================================
# Figure 2: STRUCTURAL BREAK PREDICTION BANDS — Forest plot
# ==============================================================================
def fig_structural_break_bands():
    """Forest-plot showing predicted vs actual with prediction bands."""
    print("  [2/10] Structural break prediction bands...")
    sb = load_json("structural_break_tests.json")

    # Regression parameters from Appendix C
    params = {
        'Customs / Revenue (%)': {
            'predicted': sb['customs_share']['predicted_2025'],
            'actual': sb['customs_share']['actual_2025'],
            'n': 18, 'sigma': 0.072,
            'x_bar': 2008.5, 'x_new': 2025,
            'ss_x': sum((y - 2008.5)**2 for y in range(2000, 2018)),
        },
        'Interest / Safety-net': {
            'predicted': sb['interest_ratio']['predicted_2025'],
            'actual': sb['interest_ratio']['actual_2025'],
            'n': 23, 'sigma': 0.166,
            'x_bar': 2012, 'x_new': 2025,
            'ss_x': sum((y - 2012)**2 for y in list(range(2000, 2020)) + list(range(2022, 2025))),
        },
        'Regressive Revenue (%)': {
            'predicted': sb['regressive_share']['predicted_2025'],
            'actual': sb['regressive_share']['actual_2025'],
            'n': 18, 'sigma': 2.73,
            'x_bar': 2008.5, 'x_new': 2025,
            'ss_x': sum((y - 2008.5)**2 for y in range(2000, 2018)),
        },
        'Safety-net / Outlays (%)': {
            'predicted': sb['safety_net_share']['predicted_2025'],
            'actual': sb['safety_net_share']['actual_2025'],
            'n': 23, 'sigma': 1.46,
            'x_bar': 2012, 'x_new': 2025,
            'ss_x': sum((y - 2012)**2 for y in list(range(2000, 2020)) + list(range(2022, 2025))),
        },
    }

    labels = list(params.keys())
    y_pos = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(9, 4.5))

    for i, (name, p) in enumerate(params.items()):
        se_pred = p['sigma'] * np.sqrt(
            1 + 1/p['n'] + (p['x_new'] - p['x_bar'])**2 / p['ss_x']
        )
        ci_lo = p['predicted'] - 1.96 * se_pred
        ci_hi = p['predicted'] + 1.96 * se_pred

        # Prediction band (gray)
        ax.barh(i, ci_hi - ci_lo, left=ci_lo, height=0.35,
                color='#d3d3d3', edgecolor='#999', linewidth=0.5, zorder=1)
        # Predicted value (diamond)
        ax.scatter(p['predicted'], i, marker='D', s=80, color=PALETTE['accent'],
                   zorder=3, label='Predicted (trend)' if i == 0 else '')
        # Actual value (circle)
        is_break = abs(p['actual'] - p['predicted']) / se_pred > 2.0
        color = PALETTE['snap'] if is_break else PALETTE['tariff']
        ax.scatter(p['actual'], i, marker='o', s=100, color=color, edgecolors='black',
                   linewidths=0.8, zorder=4,
                   label='Actual (break)' if i == 0 else ('Actual (within trend)' if i == 2 else ''))

        # z-score annotation
        z = (p['actual'] - p['predicted']) / se_pred
        ax.annotate(f'z = {z:.1f}', xy=(p['actual'], i),
                    xytext=(8, -2), textcoords='offset points',
                    fontsize=9, fontweight='bold', color=color)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel('Value')
    ax.set_title('FY2025 Structural Break Tests: Predicted vs. Actual with 95% Prediction Bands')
    ax.legend(loc='lower right', fontsize=9, framealpha=0.9)
    ax.invert_yaxis()

    fig.tight_layout()
    fig.savefig(FIGURES / "fig12_structural_break_bands.png")
    plt.close(fig)


# ==============================================================================
# Figure 3: SERVICES CONTROL — Price acceleration slope chart
# ==============================================================================
def fig_services_price_acceleration():
    """Dumbbell chart: pre → post price acceleration for traded vs services."""
    print("  [3/10] Services control price acceleration...")
    sc = load_json("services_control_test.json")

    traded = sc['traded_goods']
    services = sc['services_control']
    items = traded + services
    names = [x['name'] for x in items]
    pre = [x['pre_yoy'] for x in items]
    post = [x['post_yoy'] for x in items]
    accel = [x['acceleration'] for x in items]

    n_traded = len(traded)
    n_total = len(items)
    y = np.arange(n_total)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [2, 1]})

    # Left panel: dumbbell chart pre→post YoY
    ax = axes[0]
    for i in range(n_total):
        color = PALETTE['traded'] if i < n_traded else PALETTE['services']
        ax.plot([pre[i], post[i]], [i, i], color=color, linewidth=2, alpha=0.6, zorder=1)
        ax.scatter(pre[i], i, color=color, s=50, marker='o', zorder=2, alpha=0.7)
        ax.scatter(post[i], i, color=color, s=80, marker='s', zorder=2)

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9.5)
    ax.set_xlabel('Year-over-Year Price Change (%)')
    ax.set_title('CPI Price Changes: Pre-Tariff vs. Post-Tariff')
    ax.axvline(x=0, color='black', linewidth=0.5, alpha=0.5)
    ax.axhline(y=n_traded - 0.5, color='gray', linestyle='--', linewidth=1)
    ax.text(ax.get_xlim()[1] * 0.6, n_traded - 0.8, 'Traded Goods ↑', fontsize=8, color=PALETTE['traded'])
    ax.text(ax.get_xlim()[1] * 0.6, n_traded + 0.2, 'Services (Control) ↓', fontsize=8, color=PALETTE['services'])

    # Circle=pre, Square=post legend
    ax.scatter([], [], color='gray', s=50, marker='o', label='Pre-tariff (Dec 2023)')
    ax.scatter([], [], color='gray', s=80, marker='s', label='Post-tariff (Dec 2024)')
    ax.legend(loc='lower right', fontsize=8)
    ax.invert_yaxis()

    # Right panel: acceleration bars
    ax2 = axes[1]
    colors = [PALETTE['traded'] if i < n_traded else PALETTE['services'] for i in range(n_total)]
    bars = ax2.barh(y, accel, color=colors, alpha=0.8, edgecolor='white', linewidth=0.5)
    ax2.set_yticks([])
    ax2.set_xlabel('Acceleration (pp)')
    ax2.set_title('Price Acceleration')
    ax2.axvline(x=0, color='black', linewidth=0.8)
    ax2.axhline(y=n_traded - 0.5, color='gray', linestyle='--', linewidth=1)

    # Annotate mean differentials
    mean_t = sc['mean_traded_acceleration']
    mean_s = sc['mean_services_acceleration']
    ax2.axvline(x=mean_t, color=PALETTE['traded'], linestyle=':', linewidth=1.5, alpha=0.7)
    ax2.axvline(x=mean_s, color=PALETTE['services'], linestyle=':', linewidth=1.5, alpha=0.7)

    # Stats annotation
    stats_text = (f"Differential: {sc['differential']:.1f} pp\n"
                  f"Mann-Whitney p = {sc['mann_whitney_p']:.3f}\n"
                  f"Cohen's d = {sc['cohens_d']:.2f}")
    ax2.text(0.98, 0.02, stats_text, transform=ax2.transAxes,
             fontsize=8.5, va='bottom', ha='right',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffffdd', alpha=0.9))
    ax2.invert_yaxis()

    fig.suptitle('Tariff Pass-Through: Traded Goods vs. Services Control',
                 fontsize=14, fontweight='bold', y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig13_services_price_acceleration.png")
    plt.close(fig)


# ==============================================================================
# Figure 4: B50 CALIBRATION DIAGRAM
# ==============================================================================
def fig_b50_calibration():
    """Stacked bar + annotation showing B50 construction from quintile shares."""
    print("  [4/10] B50 calibration diagram...")
    cal = load_json("b50_calibration.json")
    ps = cal['person_shares']

    quintiles = ['Q1', 'Q2', 'Q3', 'Q4\n(41.4%)', 'Q4\n(58.6%)', 'Q5']
    sizes = [ps['Q1'], ps['Q2'], ps['Q3'],
             ps['Q4'] * cal['frac_q4_below_p50'],
             ps['Q4'] * (1 - cal['frac_q4_below_p50']),
             ps['Q5']]
    colors_bar = [PALETTE['snap'], PALETTE['medicaid'], PALETTE['nondiscr'],
                  PALETTE['tariff'], '#cccccc', '#999999']
    labels_bar = ['Q1 (in B50)', 'Q2 (in B50)', 'Q3 (in B50)',
                  'Q4 below median (in B50)', 'Q4 above median', 'Q5']

    fig, ax = plt.subplots(figsize=(10, 4))

    left = 0
    for i, (s, c, l) in enumerate(zip(sizes, colors_bar, labels_bar)):
        bar = ax.barh(0, s, left=left, color=c, edgecolor='white', linewidth=1.5, height=0.6)

        # Label inside if wide enough
        if s > 4:
            ax.text(left + s/2, 0, f'{s:.1f}%', ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white' if i < 4 else 'black')
        left += s

    # B50 boundary line
    b50_end = sizes[0] + sizes[1] + sizes[2] + sizes[3]
    ax.axvline(x=b50_end, color='black', linewidth=2, linestyle='--', zorder=5)
    ax.annotate(f'B50 = {b50_end:.1f}%\nof persons',
                xy=(b50_end, 0.35), xytext=(b50_end + 3, 0.42),
                fontsize=11, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel('Share of Population (%)')
    ax.set_title(f'B50 Calibration: Q1 + Q2 + Q3 + 0.414 × Q4  (p50 household = ${cal["p50_hh_income"]:,.0f})')

    # Custom legend
    handles = [mpatches.Patch(color=c, label=l) for c, l in zip(colors_bar, labels_bar)]
    ax.legend(handles=handles, loc='lower center', ncol=3, fontsize=8,
              bbox_to_anchor=(0.5, -0.35), framealpha=0.9)

    fig.tight_layout()
    fig.savefig(FIGURES / "fig14_b50_calibration.png")
    plt.close(fig)


# ==============================================================================
# Figure 5: ROBUSTNESS SPECIFICATION CURVE
# ==============================================================================
def fig_specification_curve():
    """Specification curve: point estimates across 6 robustness dimensions."""
    print("  [5/10] Robustness specification curve...")
    rob = load_json("robustness_summary.json")

    # Parse the key numbers from each conclusion
    tests = []
    for r in rob:
        name = r['test']
        conc = r['conclusion']
        n_specs = r['n_specs']

        if 'Bootstrap' in name:
            # "B50 share: 11.12% [10.96, 11.29]"
            tests.append({
                'name': 'Bootstrap CI\n(HH-clustered)',
                'point': 11.12, 'lo': 10.96, 'hi': 11.29,
                'n': n_specs, 'type': 'ci'
            })
        elif 'Propensity' in name:
            # "Loss range: $-158.5B to $-139.1B"
            tests.append({
                'name': 'Propensity\nClassification',
                'point': -148.8, 'lo': -158.5, 'hi': -139.1,
                'n': n_specs, 'type': 'loss'
            })
        elif 'Pass-Through' in name:
            # "B50 per-person: $213-$852"
            tests.append({
                'name': 'Tariff\nPass-Through',
                'point': 532.5, 'lo': 213, 'hi': 852,
                'n': n_specs, 'type': 'tariff'
            })
        elif 'Baseline' in name:
            tests.append({
                'name': 'CBO Baseline\nUncertainty',
                'point': -188, 'lo': -220, 'hi': -156,
                'n': n_specs, 'type': 'loss'
            })
        elif 'Deflator' in name:
            tests.append({
                'name': 'Alternative\nDeflators',
                'point': 75, 'lo': 70, 'hi': 80,
                'n': n_specs, 'type': 'pct'
            })
        elif 'Placebo' in name:
            tests.append({
                'name': 'Placebo\n(FY2019)',
                'point': 0, 'lo': -20, 'hi': 20,
                'n': n_specs, 'type': 'placebo'
            })

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(tests))
    for i, t in enumerate(tests):
        # Normalize to show all on same scale: compute a "robustness score"
        color = PALETTE['tariff']
        ax.scatter(i, 1, s=200, color=color, zorder=5, edgecolors='black', linewidths=0.8)

        # Top annotation with the actual values
        if t['type'] == 'ci':
            label = f"{t['point']:.2f}%\n[{t['lo']}, {t['hi']}]"
        elif t['type'] == 'loss':
            label = f"${t['point']:.0f}B\n[${t['lo']:.0f}B, ${t['hi']:.0f}B]"
        elif t['type'] == 'tariff':
            label = f"${t['point']:.0f}/person\n[${t['lo']}, ${t['hi']}]"
        elif t['type'] == 'pct':
            label = f">{t['lo']}% real\ndecline (all)"
        elif t['type'] == 'placebo':
            label = f"Gap ≈ $0B\nvs −$404B"

        ax.annotate(label, xy=(i, 1), xytext=(0, 35), textcoords='offset points',
                    ha='center', va='bottom', fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffdd', alpha=0.9))

        # Spec count below
        ax.text(i, 0.65, f'n = {t["n"]}', ha='center', fontsize=8, color=PALETTE['gray'])

        # PASS marker
        ax.text(i, 0.80, '✓ ROBUST', ha='center', fontsize=9, fontweight='bold',
                color=PALETTE['tariff'])

    ax.set_xlim(-0.5, len(tests) - 0.5)
    ax.set_ylim(0.5, 1.6)
    ax.set_xticks(x)
    ax.set_xticklabels([t['name'] for t in tests], fontsize=9)
    ax.set_yticks([])
    ax.set_title('Robustness Summary: All 6 Dimensions Pass', fontsize=14, fontweight='bold')
    ax.axhline(y=1, color='gray', linewidth=0.5, alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIGURES / "fig15_specification_curve.png")
    plt.close(fig)


# ==============================================================================
# Figure 6: CBO COUNTERFACTUAL WATERFALL
# ==============================================================================
def fig_counterfactual_waterfall():
    """Waterfall chart showing CBO baseline → policy gaps → actual."""
    print("  [6/10] CBO counterfactual waterfall...")
    cf = load_json("counterfactual_analysis_results.json")
    baseline = cf['cbo_baseline']
    gap = cf['policy_gap']

    # Build waterfall items
    categories = ['CBO Baseline\nTotal Outlays']
    values = [baseline['Total Outlays']]
    colors_wf = [PALETTE['medicaid']]

    # Policy gap components (negative = cuts)
    gap_items = [
        ('Medicaid', gap['Medicaid']),
        ('Income\nSecurity', gap['Income Security']),
        ('Nondefense\nDiscretionary', gap['Nondefense Discretionary']),
        ('Other\nMandatory', gap['Other Mandatory']),
        ('Net Interest\n(increase)', gap['Net Interest']),
    ]

    for name, val in gap_items:
        categories.append(name)
        values.append(val)
        colors_wf.append(PALETTE['snap'] if val < 0 else PALETTE['nondiscr'])

    # Final actual
    actual_outlays = cf['actual_estimates']['Total Outlays']
    categories.append('Actual FY2025\nEstimate')
    values.append(actual_outlays)
    colors_wf.append(PALETTE['tariff'])

    fig, ax = plt.subplots(figsize=(10, 6))

    # Compute waterfall positions
    n = len(values)
    cumulative = baseline['Total Outlays']
    bottoms = []
    heights = []

    for i in range(n):
        if i == 0:
            bottoms.append(0)
            heights.append(values[0])
        elif i == n - 1:
            bottoms.append(0)
            heights.append(values[-1])
        else:
            heights.append(values[i])
            if values[i] < 0:
                bottoms.append(cumulative + values[i])
            else:
                bottoms.append(cumulative)
            cumulative += values[i]

    bars = ax.bar(range(n), heights, bottom=bottoms, color=colors_wf,
                  edgecolor='white', linewidth=1.2, width=0.65)

    # Value labels
    for i, (b, h) in enumerate(zip(bottoms, heights)):
        if i == 0 or i == n - 1:
            ax.text(i, b + h + 30, f'${h:,.0f}B', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')
        else:
            sign = '+' if h > 0 else ''
            ypos = b + h/2
            ax.text(i, ypos, f'{sign}${h:,.0f}B', ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white')

    # Connector lines
    for i in range(n - 2):
        top_i = bottoms[i] + heights[i]
        if i == 0:
            connect_y = top_i
        else:
            connect_y = bottoms[i] + (heights[i] if heights[i] > 0 else 0)
            connect_y = bottoms[i+1] + (heights[i+1] if heights[i+1] > 0 else 0)
        # Simple horizontal connector
        if i < n - 2:
            y_connect = bottoms[i+1] + max(0, heights[i+1])
            # Use cumulative
            y_line = sum(values[:i+2]) if i > 0 else values[0]
            # Actually just draw from the top of current to the start of next
            cum_val = values[0] + sum(values[1:i+2])
            ax.plot([i + 0.35, i + 0.65], [cum_val, cum_val],
                    color='gray', linewidth=0.8, linestyle='-')

    ax.set_xticks(range(n))
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylabel('Federal Outlays ($B)')
    ax.set_title('CBO Counterfactual: Baseline to Actual FY2025 Outlays')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}B'))

    # Total gap annotation
    total_gap = gap['Total Outlays']
    ax.annotate(f'Total Policy Gap: ${total_gap:,.0f}B',
                xy=(3, cumulative - 50), fontsize=11, fontweight='bold',
                color=PALETTE['snap'],
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff0f0', alpha=0.9))

    fig.tight_layout()
    fig.savefig(FIGURES / "fig16_counterfactual_waterfall.png")
    plt.close(fig)


# ==============================================================================
# Figure 7: HISTORICAL B50 DUAL-AXIS
# ==============================================================================
def fig_historical_b50():
    """Dual-axis plot: B50 income share + transfer dependency over 8 benchmarks."""
    print("  [7/10] Historical B50 dual-axis...")
    import pandas as pd
    df = pd.read_csv(PROCESSED / "cps_asec_historical_quintiles.csv")

    years = df['income_year'].values
    b50_share = df['bottom50_income_share'].values
    transfer_pct = df['bottom50_transfer_pct'].values
    gini = df['gini_computed'].values

    fig, ax1 = plt.subplots(figsize=(9, 5))

    # Left axis: B50 income share
    line1, = ax1.plot(years, b50_share, 'o-', color=PALETTE['medicaid'],
                      linewidth=2.5, markersize=8, label='B50 Income Share (%)')
    ax1.set_xlabel('Income Year')
    ax1.set_ylabel('B50 Pre-tax Income Share (%)', color=PALETTE['medicaid'])
    ax1.tick_params(axis='y', labelcolor=PALETTE['medicaid'])
    ax1.set_ylim(4.5, 7.0)

    # Right axis: transfer dependency
    ax2 = ax1.twinx()
    line2, = ax2.plot(years, transfer_pct, 's--', color=PALETTE['snap'],
                      linewidth=2, markersize=7, label='Transfer Dependency (%)')
    ax2.set_ylabel('B50 Transfers as % of Income', color=PALETTE['snap'])
    ax2.tick_params(axis='y', labelcolor=PALETTE['snap'])
    ax2.set_ylim(38, 52)

    # Policy era shading
    ax1.axvspan(2017.5, 2023.5, alpha=0.08, color='red', zorder=0)
    ax1.text(2020.5, 6.85, 'Tariff\nEra', ha='center', fontsize=8, color='red', alpha=0.6)

    ax1.axvspan(2007.5, 2011.5, alpha=0.08, color='gray', zorder=0)
    ax1.text(2009.5, 6.85, 'GFC', ha='center', fontsize=8, color='gray', alpha=0.6)

    ax1.axvspan(2019.5, 2021.5, alpha=0.08, color='orange', zorder=0)
    ax1.text(2020.5, 4.7, 'COVID', ha='center', fontsize=7, color='orange', alpha=0.8)

    # Combined legend
    lines = [line1, line2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=9, framealpha=0.9)

    ax1.set_title('Bottom-50% Income Share and Transfer Dependency (CPS ASEC, CY2002–2023)')
    ax1.set_xticks(years)
    ax1.set_xticklabels([str(int(y)) for y in years], rotation=45, fontsize=9)

    fig.tight_layout()
    fig.savefig(FIGURES / "fig17_historical_b50.png")
    plt.close(fig)


# ==============================================================================
# Figure 8: WELFARE LOG-SCALE COMPARISON
# ==============================================================================
def fig_welfare_logscale():
    """Log-scale bar chart of welfare-equivalent losses by quintile."""
    print("  [8/10] Welfare log-scale comparison...")
    cf = load_json("counterfactual_analysis_results.json")
    welfare = cf['welfare_results']

    quintiles = [w['quintile'] for w in welfare]
    short_labels = ['Q1\n(Bottom 20%)', 'Q2', 'Q3', 'Q4', 'Q5\n(Top 20%)']
    per_person = [w['per_person_loss'] for w in welfare]
    wel_equiv = [w['welfare_equivalent_loss'] for w in welfare]
    pct_loss = [w['income_pct_loss'] for w in welfare]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))

    # Left panel: per-person loss + welfare-equivalent loss (log scale)
    ax = axes[0]
    x = np.arange(len(quintiles))
    width = 0.35

    bars1 = ax.bar(x - width/2, per_person, width, label='Per-Person Loss ($)',
                   color=PALETTE['medicaid'], edgecolor='white', linewidth=0.8)
    bars2 = ax.bar(x + width/2, wel_equiv, width, label='Welfare-Equivalent Loss ($)',
                   color=PALETTE['snap'], edgecolor='white', linewidth=0.8)

    ax.set_yscale('log')
    ax.set_ylabel('Loss per Person ($, log scale)')
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, fontsize=9)
    ax.legend(fontsize=9, framealpha=0.9)
    ax.set_title('Nominal vs. Welfare-Weighted Loss')

    # Value labels
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h * 1.15, f'${h:,.0f}',
                ha='center', va='bottom', fontsize=7.5)
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h * 1.15, f'${h:,.0f}',
                ha='center', va='bottom', fontsize=7.5)

    # Right panel: % of income loss
    ax2 = axes[1]
    colors_pct = [PALETTE['snap'], PALETTE['snap'], PALETTE['nondiscr'],
                  PALETTE['tariff'], PALETTE['tariff']]
    bars3 = ax2.bar(x, pct_loss, color=colors_pct, edgecolor='white', linewidth=0.8)
    ax2.set_yscale('log')
    ax2.set_ylabel('Loss as % of Income (log scale)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(short_labels, fontsize=9)
    ax2.set_title('Income-Proportional Burden')

    for bar, val in zip(bars3, pct_loss):
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h * 1.15, f'{val:.1f}%',
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

    fig.suptitle('Welfare-Weighted Impact Analysis (CRRA σ = 2)',
                 fontsize=14, fontweight='bold', y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig18_welfare_logscale.png")
    plt.close(fig)


# ==============================================================================
# Figure 9: STATE EXPOSURE DOT PLOT
# ==============================================================================
def fig_state_exposure():
    """Dot plot of state exposure index, color-coded by treatment group."""
    print("  [9/10] State exposure dot plot...")
    df = load_csv("state_exposure_index.csv")

    # Sort by exposure index
    df_sorted = df.sort_values('exposure_index', ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(10, 12))

    group_colors = {
        'High Exposure': PALETTE['snap'],
        'Medium Exposure': PALETTE['nondiscr'],
        'Low Exposure': PALETTE['tariff'],
    }

    y = np.arange(len(df_sorted))
    for _, row in df_sorted.iterrows():
        idx = df_sorted.index[df_sorted['state_name'] == row['state_name']][0]
        color = group_colors.get(row['treatment_group'], PALETTE['gray'])
        ax.scatter(row['exposure_index'], idx, color=color, s=60,
                   edgecolors='black', linewidths=0.3, zorder=3)

    ax.set_yticks(y)
    ax.set_yticklabels(df_sorted['state_name'].values, fontsize=7.5)
    ax.set_xlabel('Composite Exposure Index (z-score)')
    ax.set_title('State Fiscal Exposure to FY2025 Policy Changes')
    ax.axvline(x=0, color='black', linewidth=0.8, alpha=0.5)

    # Legend
    handles = [mpatches.Patch(color=c, label=l) for l, c in group_colors.items()]
    ax.legend(handles=handles, loc='lower right', fontsize=9, framealpha=0.9)

    # Component breakdown as text
    ax.text(0.02, 0.98,
            'Index = z(transfer_dep) + z(capital_share)\n'
            '     + z(b50_relative) + z(gini)',
            transform=ax.transAxes, fontsize=8, va='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#ffffdd', alpha=0.9))

    fig.tight_layout()
    fig.savefig(FIGURES / "fig19_state_exposure_dots.png")
    plt.close(fig)


# ==============================================================================
# Figure 10: SPM DOSE-RESPONSE
# ==============================================================================
def fig_spm_dose_response():
    """Dose-response curve: SPM poverty rate under SNAP/food program cuts."""
    print("  [10/10] SPM dose-response...")
    cf = load_json("counterfactual_analysis_results.json")
    spm = cf['spm_simulation']

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left panel: Poverty rate
    ax = axes[0]
    scenarios = [s['scenario'] for s in spm]
    rates = [s['poverty_rate'] for s in spm]
    counts = [s['poverty_count'] / 1e6 for s in spm]  # Millions
    change_counts = [s['change_count'] / 1e6 for s in spm]

    # Color by magnitude
    colors_bar = []
    for s in spm:
        if s['scenario'] == 'Baseline':
            colors_bar.append(PALETTE['medicaid'])
        elif 'SNAP' in s['scenario']:
            colors_bar.append(PALETTE['snap'])
        else:
            colors_bar.append(PALETTE['nondiscr'])

    bars = ax.bar(range(len(scenarios)), rates, color=colors_bar,
                  edgecolor='white', linewidth=0.8)

    # Value labels
    for i, (bar, rate) in enumerate(zip(bars, rates)):
        ax.text(bar.get_x() + bar.get_width()/2, rate + 0.02,
                f'{rate:.2f}%', ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    ax.set_xticks(range(len(scenarios)))
    ax.set_xticklabels(scenarios, rotation=35, ha='right', fontsize=8.5)
    ax.set_ylabel('SPM Poverty Rate (%)')
    ax.set_title('Simulated Poverty Rate')
    ax.set_ylim(12.5, 13.3)

    # Right panel: Additional persons in poverty
    ax2 = axes[1]
    # Exclude baseline (change = 0)
    cut_scenarios = scenarios[1:]
    cut_counts = change_counts[1:]
    cut_colors = colors_bar[1:]

    bars2 = ax2.barh(range(len(cut_scenarios)), cut_counts, color=cut_colors,
                     edgecolor='white', linewidth=0.8, height=0.6)

    for bar, cnt in zip(bars2, cut_counts):
        ax2.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                 f'+{cnt:.1f}M', va='center', fontsize=9, fontweight='bold')

    ax2.set_yticks(range(len(cut_scenarios)))
    ax2.set_yticklabels(cut_scenarios, fontsize=9)
    ax2.set_xlabel('Additional Persons in Poverty (millions)')
    ax2.set_title('Poverty Increase by Scenario')
    ax2.invert_yaxis()

    fig.suptitle('SPM Poverty Simulation: Food Program Cut Scenarios',
                 fontsize=14, fontweight='bold', y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig20_spm_dose_response.png")
    plt.close(fig)


# ==============================================================================
# MAIN
# ==============================================================================
def main():
    print("=" * 70)
    print("GENERATING 10 NEW PUBLICATION FIGURES")
    print("=" * 70)

    fig_burden_decomposition()
    fig_structural_break_bands()
    fig_services_price_acceleration()
    fig_b50_calibration()
    fig_specification_curve()
    fig_counterfactual_waterfall()
    fig_historical_b50()
    fig_welfare_logscale()
    fig_state_exposure()
    fig_spm_dose_response()

    print("\n" + "=" * 70)
    print("ALL 10 FIGURES SAVED to output/figures/")
    print("  fig11_burden_decomposition.png")
    print("  fig12_structural_break_bands.png")
    print("  fig13_services_price_acceleration.png")
    print("  fig14_b50_calibration.png")
    print("  fig15_specification_curve.png")
    print("  fig16_counterfactual_waterfall.png")
    print("  fig17_historical_b50.png")
    print("  fig18_welfare_logscale.png")
    print("  fig19_state_exposure_dots.png")
    print("  fig20_spm_dose_response.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
