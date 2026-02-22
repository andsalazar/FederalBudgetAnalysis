"""
Collect granular budget function outlays from Treasury MTS Table 9.
Filter: record_type_cd=F (function), sequence_level_nbr=2
These are the OMB budget function categories like National Defense, Health, etc.
"""
import sys, time
sys.path.insert(0, '.')

import requests
import pandas as pd
from datetime import date, datetime
from src.database.models import get_session, EconomicSeries, Observation
from src.utils.config import setup_logging

setup_logging()
session = get_session()

url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_9"

all_records = []
page = 1
while True:
    params = {
        "filter": "record_calendar_month:eq:09,record_fiscal_year:gte:2000,record_type_cd:eq:F",
        "page[size]": 500,
        "page[number]": page,
        "sort": "record_fiscal_year,sequence_number_cd",
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

# Group by function
functions = {}
for rec in all_records:
    desc = rec.get("classification_desc", "")
    year = int(rec.get("record_fiscal_year", 0))
    amt_str = rec.get("current_fytd_rcpt_outly_amt", "0")
    try:
        amt = float(amt_str) / 1e9  # Convert to billions
    except:
        continue
    
    if not desc or year < 2000:
        continue
    
    if desc not in functions:
        functions[desc] = {}
    functions[desc][year] = amt

print(f"\nBudget Functions found: {len(functions)}")

obs_count = 0
for func_name, year_data in sorted(functions.items()):
    if len(year_data) < 3:
        continue
    
    clean_name = func_name.replace(' ', '_').replace(',', '').replace("'", '')
    clean_name = clean_name.replace('-', '_').replace('(', '').replace(')', '')
    clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')[:50]
    series_id = f"MTS_BF_{clean_name}"
    
    existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
    if not existing:
        session.add(EconomicSeries(
            series_id=series_id, source='Treasury_MTS',
            title=f"Budget Function Outlays: {func_name}",
            units='Billions of Dollars', frequency='Annual',
            last_updated=datetime.utcnow()
        ))
    
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
    
    latest = max(year_data.keys())
    print(f"  {series_id:<55} {len(year_data):>3} yrs | FY{latest}: ${year_data[latest]:>8.1f}B | {func_name}")

session.commit()
print(f"\nTotal observations stored: {obs_count}")

# Also get agency-level net outlays from Table 5 (need seq=2 for totals by agency)
print("\n=== Table 5: Agency Net Outlays ===")
url5 = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_5"

all5 = []
page = 1
while True:
    params = {
        "filter": "record_calendar_month:eq:09,record_fiscal_year:gte:2015,sequence_level_nbr:eq:1",
        "fields": "classification_desc,current_fytd_net_outly_amt,record_fiscal_year",
        "page[size]": 500,
        "page[number]": page,
    }
    resp = requests.get(url5, params=params, timeout=30)
    if resp.status_code != 200:
        break
    data = resp.json()
    records = data.get("data", [])
    if not records:
        break
    all5.extend(records)
    total_pages = data.get("meta", {}).get("total-pages", 1)
    if page >= total_pages:
        break
    page += 1
    time.sleep(0.3)

print(f"  Agency records: {len(all5)}")
agencies = {}
for rec in all5:
    desc = rec.get("classification_desc", "").rstrip(":")
    year = int(rec.get("record_fiscal_year", 0))
    amt_str = rec.get("current_fytd_net_outly_amt", "0")
    try:
        amt = float(amt_str) / 1e9
    except:
        continue
    if amt == 0 or not desc:
        continue
    if desc not in agencies:
        agencies[desc] = {}
    agencies[desc][year] = amt

for agency, yd in sorted(agencies.items(), key=lambda x: -abs(x[1].get(2024, 0))):
    if len(yd) < 2:
        continue
    clean_name = agency.replace(' ', '_').replace(',', '').replace("'", '')
    clean_name = clean_name.replace('-', '_').replace('(', '').replace(')', '')
    clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')[:50]
    series_id = f"MTS_AG_{clean_name}"
    
    existing = session.query(EconomicSeries).filter_by(series_id=series_id).first()
    if not existing:
        session.add(EconomicSeries(
            series_id=series_id, source='Treasury_MTS',
            title=f"Agency Net Outlays: {agency}",
            units='Billions of Dollars', frequency='Annual',
            last_updated=datetime.utcnow()
        ))
    
    for year, val in yd.items():
        obs_date = date(year, 9, 30)
        existing_obs = session.query(Observation).filter_by(
            series_id=series_id, date=obs_date
        ).first()
        if existing_obs:
            existing_obs.value = val
        else:
            session.add(Observation(series_id=series_id, date=obs_date, value=val))
        obs_count += 1
    
    latest = max(yd.keys())
    print(f"  {series_id:<55} {len(yd):>3} yrs | FY{latest}: ${yd[latest]:>8.1f}B")

session.commit()
print(f"\nGrand total observations: {obs_count}")
session.close()
