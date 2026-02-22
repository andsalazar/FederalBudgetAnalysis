"""
Treasury Fiscal Data collector.

Fetches data from the U.S. Treasury's Fiscal Data API:
- Monthly Treasury Statement (MTS) — revenue and spending
- Debt to the Penny — daily total public debt
- Federal Spending by Category

API docs: https://fiscaldata.treasury.gov/api-documentation/
"""

import time
from datetime import datetime
from typing import Optional

import pandas as pd
import requests
from loguru import logger

from src.database.models import get_session, EconomicSeries, Observation, CollectionLog

TREASURY_BASE_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"

# Key Treasury endpoints
ENDPOINTS = {
    "mts_revenue": {
        "path": "/v1/accounting/mts/mts_table_4",
        "description": "Monthly Treasury Statement — Receipts by Source",
        "series_prefix": "TREASURY_REV",
    },
    "mts_outlays": {
        "path": "/v1/accounting/mts/mts_table_5",
        "description": "Monthly Treasury Statement — Outlays by Function",
        "series_prefix": "TREASURY_OUT",
    },
    "debt_to_penny": {
        "path": "/v2/accounting/od/debt_to_penny",
        "description": "Total Public Debt Outstanding (Daily)",
        "series_prefix": "TREASURY_DEBT",
    },
    "deficit_surplus": {
        "path": "/v1/accounting/mts/mts_table_1",
        "description": "Summary of Receipts, Outlays, and the Deficit/Surplus",
        "series_prefix": "TREASURY_SUMMARY",
    },
}


class TreasuryCollector:
    """Collect fiscal data from the US Treasury Fiscal Data API (no API key needed)."""

    def __init__(self):
        self.session = requests.Session()

    def _request(
        self,
        endpoint_path: str,
        fields: str = None,
        filters: str = None,
        sort: str = None,
        page_size: int = 10000,
        page_number: int = 1,
    ) -> dict:
        """Make a Treasury Fiscal Data API request."""
        url = f"{TREASURY_BASE_URL}{endpoint_path}"
        params = {
            "page[size]": page_size,
            "page[number]": page_number,
        }
        if fields:
            params["fields"] = fields
        if filters:
            params["filter"] = filters
        if sort:
            params["sort"] = sort

        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()

        time.sleep(0.3)  # Be polite
        return response.json()

    def collect_debt_to_penny(
        self, start_date: str = "1970-01-01", db_session=None
    ) -> int:
        """Collect daily total public debt outstanding."""
        if db_session is None:
            db_session = get_session()

        series_id = "TREASURY_DEBT_TOTAL"
        records_saved = 0
        status = "success"
        error_msg = None

        try:
            # Ensure series metadata exists
            existing_series = db_session.query(EconomicSeries).filter_by(
                series_id=series_id
            ).first()
            if not existing_series:
                db_session.add(EconomicSeries(
                    series_id=series_id,
                    source="Treasury",
                    title="Total Public Debt Outstanding",
                    units="Millions of Dollars",
                    frequency="Daily",
                    last_updated=datetime.utcnow(),
                ))

            # Paginate through all results
            page = 1
            while True:
                data = self._request(
                    ENDPOINTS["debt_to_penny"]["path"],
                    fields="record_date,tot_pub_debt_out_amt",
                    filters=f"record_date:gte:{start_date}",
                    sort="-record_date",
                    page_number=page,
                )

                records = data.get("data", [])
                if not records:
                    break

                for rec in records:
                    obs_date = datetime.strptime(rec["record_date"], "%Y-%m-%d").date()
                    try:
                        value = float(rec["tot_pub_debt_out_amt"])
                    except (ValueError, TypeError):
                        continue

                    existing_obs = db_session.query(Observation).filter_by(
                        series_id=series_id, date=obs_date
                    ).first()
                    if existing_obs:
                        existing_obs.value = value
                    else:
                        db_session.add(Observation(
                            series_id=series_id,
                            date=obs_date,
                            value=value,
                        ))
                    records_saved += 1

                # Check for more pages
                meta = data.get("meta", {})
                total_pages = meta.get("total-pages", 1)
                if page >= total_pages:
                    break
                page += 1

            db_session.commit()
            logger.info(f"Treasury debt data: saved {records_saved} observations")

        except Exception as e:
            status = "error"
            error_msg = str(e)[:500]
            logger.error(f"Error collecting Treasury debt data: {e}")
            db_session.rollback()

        db_session.add(CollectionLog(
            source="Treasury",
            series_id=series_id,
            records_fetched=records_saved,
            status=status,
            error_message=error_msg,
        ))
        db_session.commit()
        return records_saved

    def collect_mts_summary(
        self, start_date: str = "1970-01-01", db_session=None
    ) -> int:
        """Collect Monthly Treasury Statement summary (receipts, outlays, deficit)."""
        if db_session is None:
            db_session = get_session()

        series_id = "TREASURY_MTS_SUMMARY"
        records_saved = 0
        status = "success"
        error_msg = None

        try:
            existing_series = db_session.query(EconomicSeries).filter_by(
                series_id=series_id
            ).first()
            if not existing_series:
                db_session.add(EconomicSeries(
                    series_id=series_id,
                    source="Treasury",
                    title="Monthly Treasury Statement Summary",
                    units="Millions of Dollars",
                    frequency="Monthly",
                    last_updated=datetime.utcnow(),
                ))

            data = self._request(
                ENDPOINTS["deficit_surplus"]["path"],
                filters=f"record_date:gte:{start_date}",
                sort="-record_date",
            )

            for rec in data.get("data", []):
                obs_date = datetime.strptime(rec["record_date"], "%Y-%m-%d").date()
                # Store net value (surplus/deficit)
                try:
                    value = float(rec.get("net_outlays_amt", 0))
                except (ValueError, TypeError):
                    continue

                existing_obs = db_session.query(Observation).filter_by(
                    series_id=series_id, date=obs_date
                ).first()
                if existing_obs:
                    existing_obs.value = value
                else:
                    db_session.add(Observation(
                        series_id=series_id,
                        date=obs_date,
                        value=value,
                    ))
                records_saved += 1

            db_session.commit()
            logger.info(f"Treasury MTS summary: saved {records_saved} observations")

        except Exception as e:
            status = "error"
            error_msg = str(e)[:500]
            logger.error(f"Error collecting Treasury MTS data: {e}")
            db_session.rollback()

        db_session.add(CollectionLog(
            source="Treasury",
            series_id=series_id,
            records_fetched=records_saved,
            status=status,
            error_message=error_msg,
        ))
        db_session.commit()
        return records_saved

    def collect_all(self) -> dict:
        """Collect all Treasury data sources."""
        results = {}
        db_session = get_session()

        logger.info("Collecting Treasury Fiscal Data...")
        results["debt_to_penny"] = self.collect_debt_to_penny(db_session=db_session)
        results["mts_summary"] = self.collect_mts_summary(db_session=db_session)

        total = sum(results.values())
        logger.info(f"Treasury collection complete: {total} total observations")
        return results


def collect_treasury_data() -> dict:
    """Convenience wrapper to collect Treasury data."""
    collector = TreasuryCollector()
    return collector.collect_all()
