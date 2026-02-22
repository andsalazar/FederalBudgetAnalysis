"""
CBO (Congressional Budget Office) data collector.

Downloads publicly available CSV datasets from the CBO website:
- Historical Budget Data
- Budget Projections
- Distribution of Household Income

Source: https://www.cbo.gov/data/budget-economic-data
"""

import io
from datetime import datetime

import pandas as pd
import requests
from loguru import logger

from src.utils.config import get_data_path

# CBO data download URLs (these are periodically updated by CBO)
CBO_URLS = {
    "historical_budget": {
        "url": "https://www.cbo.gov/system/files/2024-06/51134-2024-06-HistoricalBudgetData.xlsx",
        "description": "Historical Budget Data (1962-present)",
        "filename": "cbo_historical_budget.xlsx",
    },
    "budget_projections": {
        "url": "https://www.cbo.gov/system/files/2024-06/51118-2024-06-BudgetProjections.xlsx",
        "description": "Budget Projections (10-year window)",
        "filename": "cbo_budget_projections.xlsx",
    },
}


class CBOCollector:
    """Download and cache CBO public datasets."""

    def __init__(self):
        self.raw_path = get_data_path("raw")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "FederalBudgetAnalysis Research Project"
        })

    def download_file(self, url: str, filename: str) -> str:
        """Download a file from CBO and save to data/raw/."""
        filepath = self.raw_path / filename
        logger.info(f"Downloading {filename} from CBO...")

        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(response.content)

            size_mb = len(response.content) / (1024 * 1024)
            logger.info(f"Downloaded {filename} ({size_mb:.1f} MB)")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            return None

    def collect_historical_budget(self) -> str:
        """Download CBO historical budget data."""
        info = CBO_URLS["historical_budget"]
        return self.download_file(info["url"], info["filename"])

    def collect_budget_projections(self) -> str:
        """Download CBO budget projections."""
        info = CBO_URLS["budget_projections"]
        return self.download_file(info["url"], info["filename"])

    def collect_all(self) -> dict:
        """Download all CBO datasets."""
        results = {}
        for name, info in CBO_URLS.items():
            path = self.download_file(info["url"], info["filename"])
            results[name] = path
        return results

    @staticmethod
    def load_historical_budget(filepath: str = None) -> dict:
        """
        Parse the CBO historical budget Excel file into DataFrames.

        Returns a dict of {sheet_name: DataFrame}.
        """
        if filepath is None:
            filepath = get_data_path("raw") / "cbo_historical_budget.xlsx"

        try:
            sheets = pd.read_excel(filepath, sheet_name=None, header=None)
            logger.info(f"Loaded CBO historical budget: {list(sheets.keys())}")
            return sheets
        except FileNotFoundError:
            logger.error(f"CBO file not found at {filepath}. Run collect_all() first.")
            return {}


def collect_cbo_data() -> dict:
    """Convenience wrapper to collect CBO data."""
    collector = CBOCollector()
    return collector.collect_all()
