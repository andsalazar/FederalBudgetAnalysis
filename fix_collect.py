"""Collect the replacement FRED series that failed earlier."""
import sys
sys.path.insert(0, '.')

from src.utils.config import load_config, setup_logging
from src.collectors.fred_collector import FREDCollector

setup_logging()
collector = FREDCollector()

# The corrected series IDs
fix_series = [
    'USINCTAX',       # US Individual Income Tax Collections
    'IITTRHB',        # Individual Income Tax: Highest Bracket Rate
    'CUSR0000SAF11',  # CPI: Food at Home
    'CPIAPPSL',       # CPI: Apparel
    'CPIMEDSL',       # CPI: Medical Care
    'CPIEDUSL',       # CPI: Education & Communication
]

results = collector.collect_all(fix_series)
print(f"\nResults: {results}")
print(f"Total: {sum(results.values())} observations")
