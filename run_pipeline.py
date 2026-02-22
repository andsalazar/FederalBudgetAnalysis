"""
Federal Budget Analysis — Main Pipeline Runner

Usage:
    python run_pipeline.py --init-db          Initialize the database
    python run_pipeline.py --collect           Collect all data sources
    python run_pipeline.py --collect-fred      Collect FRED data only
    python run_pipeline.py --collect-treasury  Collect Treasury data only
    python run_pipeline.py --collect-cbo       Download CBO datasets
    python run_pipeline.py --analyze           Run standard analyses
    python run_pipeline.py --dashboard         Launch interactive dashboard
    python run_pipeline.py --all               Full pipeline (collect + analyze)
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import load_config, setup_logging
from loguru import logger


def init_database():
    """Initialize the SQLite database."""
    from src.database.models import init_database
    logger.info("Initializing database...")
    init_database()
    logger.info("Database initialized successfully.")


def collect_fred():
    """Collect data from FRED."""
    from src.collectors.fred_collector import collect_fred_data
    logger.info("Starting FRED data collection...")
    results = collect_fred_data()
    total = sum(results.values())
    logger.info(f"FRED: collected {total} observations across {len(results)} series")
    return results


def collect_treasury():
    """Collect data from Treasury Fiscal Data."""
    from src.collectors.treasury_collector import collect_treasury_data
    logger.info("Starting Treasury data collection...")
    results = collect_treasury_data()
    total = sum(results.values())
    logger.info(f"Treasury: collected {total} observations")
    return results


def collect_cbo():
    """Download CBO datasets."""
    from src.collectors.cbo_collector import collect_cbo_data
    logger.info("Starting CBO data download...")
    results = collect_cbo_data()
    logger.info(f"CBO: downloaded {len(results)} datasets")
    return results


def collect_all():
    """Run all data collectors."""
    logger.info("=" * 60)
    logger.info("STARTING FULL DATA COLLECTION")
    logger.info("=" * 60)

    results = {}
    try:
        results["fred"] = collect_fred()
    except Exception as e:
        logger.error(f"FRED collection failed: {e}")
        results["fred"] = {"error": str(e)}

    try:
        results["treasury"] = collect_treasury()
    except Exception as e:
        logger.error(f"Treasury collection failed: {e}")
        results["treasury"] = {"error": str(e)}

    try:
        results["cbo"] = collect_cbo()
    except Exception as e:
        logger.error(f"CBO download failed: {e}")
        results["cbo"] = {"error": str(e)}

    logger.info("=" * 60)
    logger.info("DATA COLLECTION COMPLETE")
    logger.info("=" * 60)
    return results


def run_analysis():
    """Run standard analyses on collected data."""
    from src.analysis.policy_impact import (
        load_series, interrupted_time_series, percent_change_around_event, test_stationarity
    )
    from src.visualization.charts import plot_time_series, plot_its_results, plot_policy_comparison

    config = load_config()
    policy_periods = config.get("analysis", {}).get("policy_periods", {})

    logger.info("=" * 60)
    logger.info("RUNNING ANALYSIS")
    logger.info("=" * 60)

    # --- 1. Federal Deficit Trend ---
    deficit = load_series("FYFSGDA188S")
    if not deficit.empty:
        logger.info("Analyzing federal deficit trends...")
        stat_test = test_stationarity(deficit)
        logger.info(f"Deficit stationarity: {stat_test}")

        # ITS around TCJA
        tcja = policy_periods.get("tcja", {})
        if tcja.get("start"):
            its_results = interrupted_time_series(deficit, tcja["start"])
            logger.info(f"TCJA ITS - intervention effect: {its_results['intervention_effect']:.3f}")
            logger.info(f"TCJA ITS - trend change: {its_results['trend_change']:.4f}")
            plot_its_results(
                its_results,
                title="Federal Deficit (% GDP) — TCJA Impact",
                ylabel="% of GDP",
                save_as="its_deficit_tcja",
            )

    # --- 2. Trade balance around tariffs ---
    trade = load_series("BOPGSTB")
    if not trade.empty:
        tariff_2018 = policy_periods.get("tariff_era_2018", {})
        if tariff_2018.get("start"):
            pct = percent_change_around_event(trade, tariff_2018["start"], window_years=2)
            logger.info(f"Trade balance around 2018 tariffs: {pct}")

    # --- 3. Policy comparison ---
    deficit = load_series("FYFSGDA188S")
    if not deficit.empty:
        plot_policy_comparison(
            deficit,
            policy_periods,
            ylabel="% of GDP",
            title="Federal Deficit by Policy Period",
            save_as="deficit_by_policy_period",
        )

    logger.info("Analysis complete. Check output/figures/ for charts.")


def launch_dashboard():
    """Launch the interactive Dash dashboard."""
    logger.info("Launching dashboard...")
    from dashboards.budget_dashboard import app
    app.run(debug=True, port=8050)


def main():
    parser = argparse.ArgumentParser(
        description="Federal Budget & Policy Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--init-db", action="store_true", help="Initialize the database")
    parser.add_argument("--collect", action="store_true", help="Collect all data sources")
    parser.add_argument("--collect-fred", action="store_true", help="Collect FRED data only")
    parser.add_argument("--collect-treasury", action="store_true", help="Collect Treasury data only")
    parser.add_argument("--collect-cbo", action="store_true", help="Download CBO datasets")
    parser.add_argument("--analyze", action="store_true", help="Run analyses")
    parser.add_argument("--dashboard", action="store_true", help="Launch dashboard")
    parser.add_argument("--all", action="store_true", help="Full pipeline")

    args = parser.parse_args()

    # Setup
    config = load_config()
    setup_logging(config)

    if not any(vars(args).values()):
        parser.print_help()
        return

    if args.init_db or args.all:
        init_database()

    if args.collect or args.all:
        collect_all()
    else:
        if args.collect_fred:
            collect_fred()
        if args.collect_treasury:
            collect_treasury()
        if args.collect_cbo:
            collect_cbo()

    if args.analyze or args.all:
        run_analysis()

    if args.dashboard:
        launch_dashboard()


if __name__ == "__main__":
    main()
