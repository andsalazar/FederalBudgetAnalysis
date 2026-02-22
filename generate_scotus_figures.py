#!/usr/bin/env python3
"""
=============================================================================
GENERATE SCOTUS SCENARIO FIGURES — 4 publication-quality figures for Section 12
=============================================================================
Produces:
  fig21_scotus_scenario_comparison.png  — B50 per-person burden across scenarios
  fig22_scotus_quintile_decomposition.png — Stacked quintile burden + regressivity
  fig23_price_stickiness_flows.png       — Waterfall: incidence shift under stickiness
  fig24_scotus_welfare_sensitivity.png   — Tornado sensitivity + welfare annotation

Run:  python generate_scotus_figures.py
=============================================================================
"""

import sys, json, warnings
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent
FIGURES = BASE / "output" / "figures"
TABLES = BASE / "output" / "tables"
FIGURES.mkdir(parents=True, exist_ok=True)

# ── Publication style (matches generate_new_figures.py) ────────────────────────
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

# Color palette — consistent across paper
PALETTE = {
    'status_quo': '#264653',   # Dark teal
    'revocation': '#6c757d',   # Gray (no relief)
    'low':        '#2a9d8f',   # Teal
    'central':    '#e76f51',   # Burnt orange
    'high':       '#e63946',   # Red
    'spending':   '#457b9d',   # Blue
    'tariff':     '#f4a261',   # Orange
    'corporate':  '#2a9d8f',   # Teal
    'treasury':   '#264653',   # Dark
    'consumer':   '#e63946',   # Red
    'accent':     '#264653',
    'light':      '#a8dadc',
    'refund':     '#8338ec',   # Purple for refund flows
}

QUINTILE_COLORS = ['#e63946', '#f4a261', '#2a9d8f', '#457b9d', '#264653']


def load_json(name):
    with open(TABLES / name) as f:
        return json.load(f)


# ==============================================================================
# Figure 21: SCENARIO COMPARISON — B50 per-person burden bar chart
# ==============================================================================
def fig_scenario_comparison(data):
    """Grouped bars: Status Quo → Revocation → Low → Central → High
    with transfer-income reference line."""
    print("  [1/4] Scenario comparison bar chart...")

    sq = data['status_quo_comparison']
    rev = data['refund_scenario']
    combined = data['combined_scenarios']

    labels = [
        'Status Quo\n(FY2025)',
        'Revocation\nOnly',
        'Combined\n(Low)',
        'Combined\n(Central)',
        'Combined\n(High)',
    ]
    values = [
        sq['b50_per_person'],
        rev['b50_spending_cuts_B'] * 1e9 / data['metadata']['assumptions']['b50_population'],  # same as SQ under stickiness
        combined['Low']['b50_per_person'],
        combined['Central']['b50_per_person'],
        combined['High']['b50_per_person'],
    ]
    colors = [
        PALETTE['status_quo'],
        PALETTE['revocation'],
        PALETTE['low'],
        PALETTE['central'],
        PALETTE['high'],
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(range(len(labels)), values, color=colors, edgecolor='white',
                  linewidth=1.5, width=0.65)

    # Reference line: B50 mean transfer income
    transfer_income = 1111  # from CPS ASEC analysis
    ax.axhline(y=transfer_income, color='black', linestyle='--', linewidth=1.2,
               alpha=0.7, zorder=5)
    ax.text(4.35, transfer_income + 30, 'B50 mean transfer\nincome ($1,111)',
            fontsize=9, ha='right', va='bottom', style='italic',
            color='black', alpha=0.8)

    # Value labels on bars
    for bar, val in zip(bars, values):
        ypos = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, ypos + 30,
                f'${val:,.0f}', ha='center', va='bottom', fontsize=11,
                fontweight='bold')

    # Annotation: $0 relief arrow
    ax.annotate('$0 relief\n(price stickiness)',
                xy=(1, values[1] + 10), xytext=(1.5, values[1] + 400),
                fontsize=9, ha='center', color=PALETTE['revocation'],
                fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=PALETTE['revocation'],
                                linewidth=1.5))

    # +76% annotation on Central
    ax.annotate('+76%',
                xy=(3, values[3]), xytext=(3.55, values[3] - 200),
                fontsize=11, ha='center', color=PALETTE['central'],
                fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=PALETTE['central'],
                                linewidth=1.5))

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('B50 Per-Person Annual Burden ($)', fontsize=12)
    ax.set_title('SCOTUS Scenario: B50 Per-Person Burden Comparison',
                 fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_ylim(0, max(values) * 1.2)
    ax.grid(axis='x', visible=False)

    # Subtle bracket for "Combined" scenarios
    ax.axvspan(1.6, 4.4, alpha=0.04, color='gray')
    ax.text(3.0, max(values) * 1.12, 'Combined (Revocation + 15% Tariff)',
            ha='center', fontsize=9, style='italic', color='gray')

    fig.tight_layout()
    fig.savefig(FIGURES / "fig21_scotus_scenario_comparison.png")
    plt.close(fig)
    print("    ✓ fig21_scotus_scenario_comparison.png")


# ==============================================================================
# Figure 22: QUINTILE BURDEN DECOMPOSITION (Central Combined)
# ==============================================================================
def fig_quintile_decomposition(data):
    """Stacked bars (spending cuts + tariff) by quintile with regressivity line."""
    print("  [2/4] Quintile burden decomposition...")

    central = data['combined_scenarios']['Central']
    quintiles = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
    q_labels = ['Q1\n(Bottom 20%)', 'Q2', 'Q3', 'Q4', 'Q5\n(Top 20%)']

    spending_cuts = [central['quintile_detail'][q]['spending_cut_B'] for q in quintiles]
    tariff_burden = [central['quintile_detail'][q]['tariff_burden_B'] for q in quintiles]
    per_person = [central['quintile_detail'][q]['per_person'] for q in quintiles]

    # Use Q1 total income share (adjusted) for % of income
    # Raw pct_income for Q1 uses near-zero pretax; use a meaningful version
    pct_income_display = [
        44.3,   # Q1: % of total income incl. transfers ($5,097)
        central['quintile_detail']['Q2']['pct_income'],
        central['quintile_detail']['Q3']['pct_income'],
        central['quintile_detail']['Q4']['pct_income'],
        central['quintile_detail']['Q5']['pct_income'],
    ]

    fig, ax1 = plt.subplots(figsize=(10, 6.5))

    x = np.arange(len(quintiles))
    width = 0.55

    bars1 = ax1.bar(x, spending_cuts, width, label='Spending-cut burden',
                    color=PALETTE['spending'], edgecolor='white', linewidth=1)
    bars2 = ax1.bar(x, tariff_burden, width, bottom=spending_cuts,
                    label='New tariff burden (15%)',
                    color=PALETTE['tariff'], edgecolor='white', linewidth=1)

    # Total labels
    totals = [s + t for s, t in zip(spending_cuts, tariff_burden)]
    for i, (b, total) in enumerate(zip(bars2, totals)):
        ax1.text(b.get_x() + b.get_width() / 2,
                 total + 2,
                 f'${total:.1f}B\n(${per_person[i]:,.0f}/person)',
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax1.set_ylabel('Total Burden ($B)', fontsize=12, color=PALETTE['spending'])
    ax1.set_ylim(0, max(totals) * 1.35)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}B'))
    ax1.set_xticks(x)
    ax1.set_xticklabels(q_labels, fontsize=10)
    ax1.grid(axis='x', visible=False)

    # Secondary axis: burden as % of income
    ax2 = ax1.twinx()
    ax2.plot(x, pct_income_display, 'D-', color=PALETTE['consumer'],
             markersize=8, linewidth=2.0, label='% of income', zorder=5)
    for i, pct in enumerate(pct_income_display):
        offset = 1.5 if pct < 20 else -3
        ax2.text(i + 0.12, pct + offset, f'{pct:.1f}%',
                 fontsize=9, color=PALETTE['consumer'], fontweight='bold')

    ax2.set_ylabel('Burden as % of Income', fontsize=12, color=PALETTE['consumer'])
    ax2.set_ylim(0, max(pct_income_display) * 1.3)
    ax2.spines['right'].set_color(PALETTE['consumer'])
    ax2.tick_params(axis='y', colors=PALETTE['consumer'])

    # Combined legend
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2,
               loc='upper left', framealpha=0.9, fontsize=9)

    # Regressivity annotation
    ratio = pct_income_display[0] / pct_income_display[-1]
    ax1.text(0.5, 0.95,
             f'Regressivity ratio (Q1/Q5): {ratio:.0f}×',
             transform=ax1.transAxes, fontsize=10, fontweight='bold',
             ha='center', va='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff3cd',
                       edgecolor='#f4a261', alpha=0.9))

    ax1.set_title('Central Combined Scenario: Quintile Burden Decomposition',
                  fontsize=14, fontweight='bold')

    fig.tight_layout()
    fig.savefig(FIGURES / "fig22_scotus_quintile_decomposition.png")
    plt.close(fig)
    print("    ✓ fig22_scotus_quintile_decomposition.png")


# ==============================================================================
# Figure 23: PRICE STICKINESS FLOWS — Waterfall / incidence diagram
# ==============================================================================
def fig_price_stickiness_flows(data):
    """Horizontal waterfall showing where money flows under price stickiness."""
    print("  [3/4] Price stickiness incidence diagram...")

    fig, ax = plt.subplots(figsize=(11, 7))

    # Main flow stages (top to bottom, plotted as horizontal waterfall)
    stages = [
        ('IEEPA Tariffs\nCollected', 133, PALETTE['treasury'], 'right'),
        ('SCOTUS\nRevocation', 0, '#cccccc', 'center'),
        ('Refund to\nImporters', 133, PALETTE['corporate'], 'right'),
        ('Consumer\nPrices', 0, PALETTE['consumer'], 'center'),
        ('New 15%\nTariff', 0, PALETTE['tariff'], 'right'),
    ]

    # Build the visual as a multi-panel diagram
    y_positions = [5, 4, 3, 2, 1]
    bar_height = 0.6

    # Stage 1: IEEPA collections → Treasury (past)
    ax.barh(5, 133, height=bar_height, color=PALETTE['treasury'],
            edgecolor='white', linewidth=1.5, alpha=0.9)
    ax.text(133/2, 5, '$133B collected\nby Treasury', ha='center', va='center',
            fontsize=10, fontweight='bold', color='white')
    ax.text(-2, 5, 'FY2025\nIEEPA Tariffs', ha='right', va='center',
            fontsize=10, fontweight='bold')

    # Stage 2: Consumer burden (status quo) — consumers paid higher prices
    ax.barh(4, 140, height=bar_height, color=PALETTE['consumer'],
            edgecolor='white', linewidth=1.5, alpha=0.85)
    ax.text(140/2, 4, '$140B consumer burden\n(already paid — sunk cost)', ha='center',
            va='center', fontsize=10, fontweight='bold', color='white')
    ax.text(-2, 4, 'Consumer\nWelfare Loss', ha='right', va='center',
            fontsize=10, fontweight='bold')

    # Arrow: SCOTUS ruling
    ax.annotate('', xy=(0, 3.5), xytext=(0, 4.4),
                arrowprops=dict(arrowstyle='->', color='black', linewidth=2.5))
    ax.text(72, 3.65, 'SCOTUS: IEEPA tariffs vacated (Feb. 20, 2026)',
            ha='center', va='center', fontsize=10, fontweight='bold',
            style='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffff',
                      edgecolor='black', linewidth=1.5))

    # Stage 3: Refund flows to importers (NOT consumers)
    ax.barh(2.8, 133, height=bar_height, color=PALETTE['refund'],
            edgecolor='white', linewidth=1.5, alpha=0.85)
    ax.text(133/2, 2.8, '$133B refund → importers\n(corporate windfall)', ha='center',
            va='center', fontsize=10, fontweight='bold', color='white')
    ax.text(-2, 2.8, 'Refund\nRecipient', ha='right', va='center',
            fontsize=10, fontweight='bold')

    # Stage 4: Price stickiness — consumer prices UNCHANGED
    ax.barh(1.7, 140, height=bar_height, color=PALETTE['consumer'],
            edgecolor='white', linewidth=1.5, alpha=0.5)
    ax.text(140/2, 1.7, 'Consumer prices unchanged\n(price stickiness)', ha='center',
            va='center', fontsize=10, fontweight='bold', color=PALETTE['consumer'])
    ax.text(-2, 1.7, 'Retail\nPrices', ha='right', va='center',
            fontsize=10, fontweight='bold')

    # Hatching pattern on the price bar to show it's the "ghost" of old tariff
    ax.barh(1.7, 140, height=bar_height, color='none',
            edgecolor=PALETTE['consumer'], linewidth=0.5, hatch='///', alpha=0.4)

    # Stage 5: New 15% tariff adds MORE burden
    # Central consumer burden = 566.1B
    new_consumer = 566.1
    # Scale bar to fit — use same axis scale, but annotate the number
    bar_width_display = min(new_consumer, 180)  # clip for visual
    ax.barh(0.6, bar_width_display, height=bar_height, color=PALETTE['tariff'],
            edgecolor='white', linewidth=1.5, alpha=0.9)
    ax.text(bar_width_display/2, 0.6,
            f'+ ${new_consumer:.0f}B new tariff burden\n(15% universal → B50: $188B)',
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    ax.text(-2, 0.6, 'New 15%\nTariff', ha='right', va='center',
            fontsize=10, fontweight='bold')

    # Connecting arrows for flow
    for y_start, y_end in [(4.7, 4.3), (2.5, 2.0)]:
        ax.annotate('', xy=(70, y_end), xytext=(70, y_start),
                    arrowprops=dict(arrowstyle='->', color='gray',
                                    linewidth=1.5, alpha=0.5))

    # Key insight box
    ax.text(0.98, 0.02,
            'Key: Under price stickiness, revocation shifts\n'
            'the tariff wedge from Treasury to corporate margins.\n'
            'B50 consumer relief = $0.',
            transform=ax.transAxes, fontsize=9,
            ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8d7da',
                      edgecolor=PALETTE['consumer'], alpha=0.9))

    # Fiscal cost box
    ax.text(0.98, 0.18,
            'Fiscal cost: $133B refund debt\n→ $6.0B/yr interest (67% to top decile)',
            transform=ax.transAxes, fontsize=9,
            ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#e2e3f5',
                      edgecolor=PALETTE['refund'], alpha=0.9))

    ax.set_xlim(-30, 200)
    ax.set_ylim(0, 5.8)
    ax.set_xlabel('Billions ($)', fontsize=12)
    ax.set_yticks([])
    ax.grid(axis='y', visible=False)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}B'))

    ax.set_title('Price Stickiness and the Incidence of Tariff Revocation',
                 fontsize=14, fontweight='bold', y=1.01)

    fig.tight_layout()
    fig.savefig(FIGURES / "fig23_price_stickiness_flows.png")
    plt.close(fig)
    print("    ✓ fig23_price_stickiness_flows.png")


# ==============================================================================
# Figure 24: WELFARE SENSITIVITY TORNADO
# ==============================================================================
def fig_welfare_sensitivity(data):
    """Horizontal tornado showing Low/Central/High B50 burden + welfare annotation."""
    print("  [4/4] Welfare sensitivity tornado chart...")

    combined = data['combined_scenarios']
    welfare = data['welfare_analysis']
    sq = data['status_quo_comparison']

    fig, ax = plt.subplots(figsize=(10, 5.5))

    # Metrics to display
    metrics = [
        {
            'label': 'B50 Combined\nBurden ($B)',
            'low': combined['Low']['b50_combined_B'],
            'central': combined['Central']['b50_combined_B'],
            'high': combined['High']['b50_combined_B'],
            'sq': sq['b50_combined_B'],
            'fmt': '${:.1f}B',
        },
        {
            'label': 'B50 Per\nPerson ($)',
            'low': combined['Low']['b50_per_person'],
            'central': combined['Central']['b50_per_person'],
            'high': combined['High']['b50_per_person'],
            'sq': sq['b50_per_person'],
            'fmt': '${:,.0f}',
        },
        {
            'label': 'B50 % of\nPretax Income',
            'low': combined['Low']['b50_pct_income'],
            'central': combined['Central']['b50_pct_income'],
            'high': combined['High']['b50_pct_income'],
            'sq': sq['b50_pct_income'],
            'fmt': '{:.1f}%',
        },
        {
            'label': 'Net Fiscal\nChange ($B/yr)',
            'low': combined['Low']['net_fiscal_change_B'],
            'central': combined['Central']['net_fiscal_change_B'],
            'high': combined['High']['net_fiscal_change_B'],
            'sq': 0,
            'fmt': '+${:.1f}B',
        },
    ]

    y_positions = np.arange(len(metrics))
    bar_height = 0.35

    for i, m in enumerate(metrics):
        # Normalize to central = 1.0 for visual comparison
        central_val = m['central']
        low_norm = m['low'] / central_val
        high_norm = m['high'] / central_val
        sq_norm = m['sq'] / central_val if central_val != 0 else 0

        # Draw range bar (Low to High)
        ax.barh(i, high_norm - low_norm, height=bar_height,
                left=low_norm, color=PALETTE['tariff'], alpha=0.3,
                edgecolor=PALETTE['tariff'], linewidth=1)

        # Central marker
        ax.plot(1.0, i, 'D', color=PALETTE['central'], markersize=10, zorder=5,
                markeredgecolor='white', markeredgewidth=1.5)

        # Status quo marker (if nonzero)
        if m['sq'] != 0:
            ax.plot(sq_norm, i, 's', color=PALETTE['status_quo'], markersize=8,
                    zorder=5, markeredgecolor='white', markeredgewidth=1)

        # Low and High value labels
        ax.text(low_norm - 0.01, i, m['fmt'].format(m['low']),
                ha='right', va='center', fontsize=9, color=PALETTE['low'])
        ax.text(high_norm + 0.01, i, m['fmt'].format(m['high']),
                ha='left', va='center', fontsize=9, color=PALETTE['high'])

        # Central value label
        ax.text(1.0, i + 0.25, m['fmt'].format(m['central']),
                ha='center', va='bottom', fontsize=10, fontweight='bold',
                color=PALETTE['central'])

    ax.set_yticks(y_positions)
    ax.set_yticklabels([m['label'] for m in metrics], fontsize=10)
    ax.set_xlabel('Normalized to Central Estimate (= 1.0)', fontsize=11)
    ax.axvline(x=1.0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.grid(axis='y', visible=False)

    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=PALETTE['status_quo'],
                   markersize=8, label='Status Quo (FY2025)'),
        plt.Line2D([0], [0], marker='D', color='w', markerfacecolor=PALETTE['central'],
                   markersize=8, label='Central Estimate'),
        mpatches.Patch(color=PALETTE['tariff'], alpha=0.3, label='Low–High Range'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9, framealpha=0.9)

    # Welfare annotation box
    welfare_pct = welfare['welfare_change_pct']
    ax.text(0.02, 0.98,
            f'CRRA Welfare-Weighted Loss:\n+{welfare_pct:.1f}% (Status Quo → Central)\nσ = {welfare["sigma"]}',
            transform=ax.transAxes, fontsize=10, fontweight='bold',
            va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff3cd',
                      edgecolor=PALETTE['central'], alpha=0.9))

    ax.set_title('SCOTUS Scenario: Sensitivity Range and Welfare Impact',
                 fontsize=14, fontweight='bold')

    fig.tight_layout()
    fig.savefig(FIGURES / "fig24_scotus_welfare_sensitivity.png")
    plt.close(fig)
    print("    ✓ fig24_scotus_welfare_sensitivity.png")


# ==============================================================================
# MAIN
# ==============================================================================
def main():
    print("=" * 70)
    print("GENERATING 4 SCOTUS SCENARIO FIGURES (Section 12)")
    print("=" * 70)

    data = load_json("scotus_tariff_scenario.json")

    fig_scenario_comparison(data)
    fig_quintile_decomposition(data)
    fig_price_stickiness_flows(data)
    fig_welfare_sensitivity(data)

    print("\n" + "=" * 70)
    print("ALL 4 SCOTUS FIGURES SAVED to output/figures/")
    print("  fig21_scotus_scenario_comparison.png")
    print("  fig22_scotus_quintile_decomposition.png")
    print("  fig23_price_stickiness_flows.png")
    print("  fig24_scotus_welfare_sensitivity.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
