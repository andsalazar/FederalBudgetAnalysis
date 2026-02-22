"""
Visualization module for the Federal Budget Analysis project.

Provides publication-quality charts and standard plotting functions
for fiscal data, policy impact analysis, and comparative visualizations.
"""

from typing import Optional, List, Dict, Tuple

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np
from loguru import logger

from src.utils.config import load_config, get_output_path


def _apply_style(config: dict = None):
    """Apply project visualization style from config."""
    if config is None:
        config = load_config()
    viz = config.get("visualization", {})
    style = viz.get("style", "seaborn-v0_8-whitegrid")
    try:
        plt.style.use(style)
    except OSError:
        plt.style.use("seaborn-v0_8-whitegrid")
    sns.set_palette(viz.get("color_palette", "colorblind"))


def save_figure(fig, filename: str, config: dict = None):
    """Save a figure to the output/figures directory in configured formats."""
    if config is None:
        config = load_config()
    viz = config.get("visualization", {})
    dpi = viz.get("figure_dpi", 150)
    formats = viz.get("export_formats", ["png"])
    output_dir = get_output_path("figures")

    for fmt in formats:
        path = output_dir / f"{filename}.{fmt}"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        logger.info(f"Saved figure: {path}")


# ---------------------------------------------------------------------------
# Core plotting functions
# ---------------------------------------------------------------------------

def plot_time_series(
    data: pd.DataFrame,
    title: str = "",
    ylabel: str = "",
    policy_dates: Dict[str, str] = None,
    recession_periods: List[Tuple[str, str]] = None,
    figsize: Tuple[int, int] = None,
    save_as: str = None,
) -> plt.Figure:
    """
    Plot one or more time series with optional policy event markers and recession shading.

    Parameters
    ----------
    data : DataFrame with DatetimeIndex, each column is a series
    title : chart title
    ylabel : y-axis label
    policy_dates : dict of {label: "YYYY-MM-DD"} for vertical policy markers
    recession_periods : list of (start, end) date strings for recession shading
    figsize : figure size tuple
    save_as : filename (without extension) to auto-save
    """
    config = load_config()
    _apply_style(config)
    viz = config.get("visualization", {})

    if figsize is None:
        figsize = tuple(viz.get("default_figsize", [12, 7]))

    fig, ax = plt.subplots(figsize=figsize)

    for col in data.columns:
        ax.plot(data.index, data[col], label=col, linewidth=1.5)

    # Recession shading
    if recession_periods:
        for start, end in recession_periods:
            ax.axvspan(
                pd.Timestamp(start), pd.Timestamp(end),
                alpha=0.15, color="gray", label="_recession"
            )

    # Policy event markers
    if policy_dates:
        colors = plt.cm.Set2(np.linspace(0, 1, len(policy_dates)))
        for (label, date_str), color in zip(policy_dates.items(), colors):
            ax.axvline(
                pd.Timestamp(date_str),
                color=color, linestyle="--", alpha=0.8, linewidth=1.2
            )
            ax.text(
                pd.Timestamp(date_str), ax.get_ylim()[1] * 0.98,
                f" {label}", rotation=90, va="top", fontsize=8, color=color,
            )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.legend(loc="best", fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    fig.autofmt_xdate()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_as:
        save_figure(fig, save_as, config)
    return fig


def plot_its_results(
    its_results: dict,
    title: str = "Interrupted Time Series Analysis",
    ylabel: str = "",
    save_as: str = None,
) -> plt.Figure:
    """
    Plot the results of an interrupted time series analysis.

    Shows actual data, fitted model, and counterfactual trajectory.
    """
    config = load_config()
    _apply_style(config)
    viz = config.get("visualization", {})
    figsize = tuple(viz.get("default_figsize", [12, 7]))

    fig, ax = plt.subplots(figsize=figsize)

    actual = its_results["actual"]
    fitted = its_results["fitted"]
    counterfactual = its_results["counterfactual"]

    ax.plot(actual.index, actual.values, "o", markersize=3, alpha=0.5, label="Actual", color="steelblue")
    ax.plot(fitted.index, fitted.values, "-", linewidth=2, label="Fitted (with intervention)", color="darkblue")
    ax.plot(
        counterfactual.index, counterfactual.values, "--",
        linewidth=2, label="Counterfactual (no intervention)", color="firebrick"
    )

    # Shade the gap between fitted and counterfactual
    ax.fill_between(
        fitted.index,
        fitted.values,
        counterfactual.values,
        alpha=0.15, color="firebrick", label="Policy effect"
    )

    # Intervention line
    intervention_effect = its_results.get("intervention_effect", 0)
    # Find intervention date from where 'intervention' column changes
    params = its_results.get("params", {})

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.legend(loc="best", fontsize=9)

    # Add model stats annotation
    r2 = its_results.get("r_squared", 0)
    pvals = its_results.get("pvalues", {})
    intervention_p = pvals.get("intervention", 1.0)
    trend_p = pvals.get("time_after", 1.0)

    stats_text = (
        f"R² = {r2:.3f}\n"
        f"Intervention p = {intervention_p:.4f}\n"
        f"Trend change p = {trend_p:.4f}"
    )
    ax.text(
        0.02, 0.98, stats_text, transform=ax.transAxes,
        fontsize=9, verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.tight_layout()
    if save_as:
        save_figure(fig, save_as, config)
    return fig


def plot_budget_composition(
    data: pd.DataFrame,
    title: str = "Federal Budget Composition",
    save_as: str = None,
) -> plt.Figure:
    """
    Stacked area chart showing budget composition over time.

    Parameters
    ----------
    data : DataFrame with DatetimeIndex, columns are budget categories
    """
    config = load_config()
    _apply_style(config)
    viz = config.get("visualization", {})
    figsize = tuple(viz.get("default_figsize", [12, 7]))

    fig, ax = plt.subplots(figsize=figsize)
    ax.stackplot(data.index, [data[col] for col in data.columns], labels=data.columns, alpha=0.8)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel("Amount")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.autofmt_xdate()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_as:
        save_figure(fig, save_as, config)
    return fig


def plot_policy_comparison(
    series: pd.Series,
    policy_periods: Dict[str, Dict],
    ylabel: str = "",
    title: str = "Policy Period Comparison",
    save_as: str = None,
) -> plt.Figure:
    """
    Bar chart comparing a metric's average across different policy periods.

    Parameters
    ----------
    series : pd.Series with DatetimeIndex
    policy_periods : dict from config (label -> {start, end, label})
    """
    config = load_config()
    _apply_style(config)
    viz = config.get("visualization", {})
    figsize = tuple(viz.get("default_figsize", [12, 7]))

    labels = []
    means = []
    stds = []

    for name, period in policy_periods.items():
        start = period.get("start")
        end = period.get("end")
        label = period.get("label", name)

        subset = series.loc[start:end]
        if not subset.empty:
            labels.append(label)
            means.append(subset.mean())
            stds.append(subset.std())

    fig, ax = plt.subplots(figsize=figsize)
    colors = sns.color_palette("colorblind", len(labels))
    bars = ax.barh(labels, means, xerr=stds, color=colors, alpha=0.85, capsize=4)

    ax.set_xlabel(ylabel)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    # Value labels
    for bar, mean in zip(bars, means):
        ax.text(
            bar.get_width() + bar.get_width() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{mean:,.1f}",
            va="center", fontsize=9,
        )

    plt.tight_layout()
    if save_as:
        save_figure(fig, save_as, config)
    return fig
