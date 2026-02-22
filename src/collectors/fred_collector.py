"""
FRED (Federal Reserve Economic Data) collector.

Fetches time series data from the FRED API and stores it in the local database.
Requires a free API key: https://fred.stlouisfed.org/docs/api/api_key.html
"""

import time
from datetime import datetime, date
from typing import List, Optional

import pandas as pd
import requests
from loguru import logger

from src.utils.config import get_api_key, load_config
from src.database.models import (
    get_session, EconomicSeries, Observation, CollectionLog
)

FRED_BASE_URL = "https://api.stlouisfed.org/fred"


class FREDCollector:
    """Collect economic data from the FRED API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or get_api_key("FRED_API_KEY")
        if not self.api_key:
            raise ValueError(
                "FRED API key not found. Set FRED_API_KEY in your .env file. "
                "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html"
            )
        self.session = requests.Session()
        self.config = load_config()

    def _request(self, endpoint: str, params: dict) -> dict:
        """Make a FRED API request with rate limiting."""
        params["api_key"] = self.api_key
        params["file_type"] = "json"

        url = f"{FRED_BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()

        # FRED rate limit: 120 requests per minute
        time.sleep(0.6)
        return response.json()

    def get_series_info(self, series_id: str) -> dict:
        """Fetch metadata about a FRED series."""
        data = self._request("series", {"series_id": series_id})
        if "seriess" in data and len(data["seriess"]) > 0:
            return data["seriess"][0]
        return {}

    def get_observations(
        self,
        series_id: str,
        start_date: str = None,
        end_date: str = None,
        frequency: str = None,
    ) -> pd.DataFrame:
        """Fetch observations for a FRED series."""
        params = {"series_id": series_id}
        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date
        if frequency:
            params["frequency"] = frequency

        data = self._request("series/observations", params)
        observations = data.get("observations", [])

        if not observations:
            logger.warning(f"No observations returned for {series_id}")
            return pd.DataFrame()

        df = pd.DataFrame(observations)
        # Clean up
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])

        logger.info(f"Fetched {len(df)} observations for {series_id}")
        return df

    def collect_series(self, series_id: str, db_session=None) -> int:
        """Collect a single series: metadata + observations → database."""
        if db_session is None:
            db_session = get_session()

        fred_config = self.config.get("collectors", {}).get("fred", {})
        start_date = fred_config.get("start_date", "1970-01-01")
        frequency = fred_config.get("frequency")

        records_saved = 0
        status = "success"
        error_msg = None

        try:
            # --- Series metadata ---
            info = self.get_series_info(series_id)
            if info:
                existing = db_session.query(EconomicSeries).filter_by(
                    series_id=series_id
                ).first()
                if existing:
                    existing.title = info.get("title")
                    existing.units = info.get("units")
                    existing.frequency = info.get("frequency")
                    existing.seasonal_adjustment = info.get("seasonal_adjustment_short")
                    existing.last_updated = datetime.utcnow()
                    existing.notes = info.get("notes", "")[:2000]
                else:
                    db_session.add(EconomicSeries(
                        series_id=series_id,
                        source="FRED",
                        title=info.get("title"),
                        units=info.get("units"),
                        frequency=info.get("frequency"),
                        seasonal_adjustment=info.get("seasonal_adjustment_short"),
                        last_updated=datetime.utcnow(),
                        notes=info.get("notes", "")[:2000],
                    ))

            # --- Observations ---
            df = self.get_observations(
                series_id,
                start_date=start_date,
                frequency=frequency,
            )

            for _, row in df.iterrows():
                obs_date = row["date"].date()
                existing_obs = db_session.query(Observation).filter_by(
                    series_id=series_id, date=obs_date
                ).first()
                if existing_obs:
                    existing_obs.value = row["value"]
                else:
                    db_session.add(Observation(
                        series_id=series_id,
                        date=obs_date,
                        value=row["value"],
                    ))
                records_saved += 1

            db_session.commit()
            logger.info(f"Saved {records_saved} observations for {series_id}")

        except Exception as e:
            status = "error"
            error_msg = str(e)[:500]
            logger.error(f"Error collecting {series_id}: {e}")
            db_session.rollback()

        # --- Log the collection ---
        db_session.add(CollectionLog(
            source="FRED",
            series_id=series_id,
            records_fetched=records_saved,
            status=status,
            error_message=error_msg,
        ))
        db_session.commit()

        return records_saved

    def collect_all(self, series_ids: List[str] = None) -> dict:
        """
        Collect all configured FRED series.

        Returns dict of {series_id: records_saved}.
        """
        if series_ids is None:
            series_ids = (
                self.config.get("collectors", {})
                .get("fred", {})
                .get("series", [])
            )

        if not series_ids:
            logger.warning("No FRED series configured in config.yaml")
            return {}

        db_session = get_session()
        results = {}

        logger.info(f"Collecting {len(series_ids)} FRED series...")
        for i, sid in enumerate(series_ids, 1):
            logger.info(f"[{i}/{len(series_ids)}] Collecting {sid}...")
            results[sid] = self.collect_series(sid, db_session)

        total = sum(results.values())
        logger.info(f"FRED collection complete: {total} total observations from {len(series_ids)} series")
        return results


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def collect_fred_data(series_ids: List[str] = None) -> dict:
    """Convenience wrapper to collect FRED data."""
    collector = FREDCollector()
    return collector.collect_all(series_ids)
