"""Collect agency-level net outlays from Treasury MTS Table 5 (data_type_cd=T)."""
import sys, time
sys.path.insert(0, '.')

import requests
from datetime import date, datetime
from src.database.models import get_session, EconomicSeries, Observation
from src.utils.config import setup_logging

setup_logging()
session = get_session()

url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_5"

# Key agencies we want (department level)
TARGET_AGENCIES = [
    "Total--Department of Defense--Military Programs",
    "Total--Department of Health and Human Services",
    "Total--Centers for Medicare and Medicaid Services",
    "Total--Social Security Administration",
    "Total--Department of Education",
    "Total--Department of Veterans Affairs",
    "Total--Department of Homeland Security",
    "Total--Department of Agriculture",
    "Total--Department of Transportation",
    "Total--Department of Housing and Urban Development",
    "Total--Department of Labor",
    "Total--Department of Energy",
    "Total--Department of Justice",
    "Total--Department of the Treasury",
    "Total--Department of State",
    "Total--Department of the Interior",
    "Total--Department of Commerce",
    "Total--Environmental Protection Agency",
    "Total--National Aeronautics and Space Administration",
    "Total--Small Business Administration",
    "Total--International Assistance Programs",
    "Total--Food and Nutrition Service",
    "Total--Federal Emergency Management Agency",
    "Total--Interest on the Public Debt",
    "Total--Administration for Children and Families",
    "Total--Office of Federal Student Aid",
    "Total Outlays",
]

all_records = []
page = 1
while True:
    params = {
        "filter": "record_calendar_month:eq:09,record_fiscal_year:gte:2015,data_type_cd:eq:T",
        "page[size]": 500,
        "page[number]": page,
        "sort": "record_fiscal_year",
    }
    resp = requests.get(url, params=params, timeout=30)
    if resp.status_code != 200:
        print(f"HTTP {resp.status_code}")
        break
    data = resp.json()
    records = data.get("data", [])
    if not records:
        break
    all_records.extend(records)
    total_pages = data.get("meta", {}).get("total-pages", 1)
    print(f"  Page {page}/{total_pages}: {len(records)} records")
    if page >= total_pages:
        break
    page += 1
    time.sleep(0.3)

print(f"\nTotal records: {len(all_records)}")

# Parse and store
agencies = {}
for rec in all_records:
    desc = rec.get("classification_desc", "").rstrip(":")
    year = int(rec.get("record_fiscal_year", 0))
    net_str = rec.get("current_fytd_net_outly_amt", "0")
    try:
        net = float(net_str) / 1e9  # billions
    except:
        continue
    
    if desc not in TARGET_AGENCIES and not desc.startswith("Total--"):
        continue
    
    if desc not in agencies:
        agencies[desc] = {}
    agencies[desc][year] = net

obs_count = 0
for agency, year_data in sorted(agencies.items(), key=lambda x: -abs(x[1].get(2024, x[1].get(2025, 0)))):
    if len(year_data) < 2:
        continue
    
    short_name = agency.replace("Total--", "").replace("Department of ", "Dept_")
    short_name = short_name.replace("Total ", "").replace("the ", "")
    clean_name = short_name.replace(' ', '_').replace(',', '').replace("'", '')
    clean_name = clean_name.replace('-', '_').replace('(', '').replace(')', '')
    clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')[:50]
    series_id = f"MTS_AG_{clean_name}"
    
    existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
    if not existing:
        session.add(EconomicSeries(
            series_id=series_id, source='Treasury_MTS',
            title=f"Agency Net Outlays: {agency.replace('Total--','')}",
            units='Billions of Dollars', frequency='Annual',
            last_updated=datetime.utcnow()
        ))
    else:
        existing.title = f"Agency Net Outlays: {agency.replace('Total--','')}"
    
    for year, val in year_data.items():
        obs_date = date(year, 9, 30)
        existing_obs = session.query(Observation).filter_by(
            series_id=series_id, date=obs_date
        ).first()
        if existing_obs:
            existing_obs.value = val
        else:
            session.add(Observation(series_id=series_id, date=obs_date, value=val))
        obs_count += 1
    
    latest_yr = max(year_data.keys())
    print(f"  {series_id:<55} {len(year_data):>3} yrs | FY{latest_yr}: ${year_data[latest_yr]:>8.1f}B")

session.commit()
print(f"\nAgency observations stored: {obs_count}")
session.close()
