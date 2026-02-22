"""Discover granular agency-level spending data from Treasury Fiscal Data API and FRED."""
import sys, time
sys.path.insert(0, '.')
from fredapi import Fred
import requests

fred = Fred(api_key='43272fac437c873feb1ace8519a979fc')

# 1. Try wider BEA NIPA series range
print("=== BEA NIPA Government Spending by Function ===")
for i in [21, 31, 41, 51, 61, 71, 81, 91, 101, 111, 121, 131, 141, 151, 161, 171, 181, 191, 201, 211, 221, 231, 241, 251, 261, 271]:
    sid = f'G16{i:04d}A027NBEA'
    try:
        info = fred.get_series_info(sid)
        title = info.get('title', 'N/A')
        print(f'  {sid}  {title[:80]}')
    except:
        pass
    time.sleep(0.15)

# 2. Treasury MTS Table 5 = Budget Receipts by Source
# Treasury MTS Table 9 = Outlays by Agency
print("\n=== Treasury Fiscal Data API: Outlays by Agency ===")
url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_9"
params = {
    "filter": "record_fiscal_year:gte:2020,record_calendar_month:eq:09",
    "page[size]": 200,
    "sort": "-record_fiscal_year,current_fytd_rcpt_outly_amt",
}
try:
    resp = requests.get(url, params=params, timeout=30)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        records = data.get("data", [])
        print(f"  Records returned: {len(records)}")
        if records:
            print(f"  Fields: {list(records[0].keys())}")
            for rec in records[:10]:
                agency = rec.get("classification_desc", "?")
                year = rec.get("record_fiscal_year", "?")
                amt = rec.get("current_fytd_rcpt_outly_amt", "?")
                print(f"    FY{year}: {agency[:50]:<50} ${amt}")
    else:
        print(f"  Response: {resp.text[:300]}")
except Exception as e:
    print(f"  Error: {e}")

# 3. Try table 4 — Outlays by Budget Function
print("\n=== Treasury Fiscal Data API: Outlays by Budget Function ===")
for table_num in [4, 5, 6, 7, 8, 9]:
    url = f"https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_{table_num}"
    try:
        resp = requests.get(url, params={"page[size]": 3}, timeout=15)
        if resp.status_code == 200:
            recs = resp.json().get("data", [])
            if recs:
                print(f"\n  Table {table_num}: fields = {list(recs[0].keys())[:6]}")
                for r in recs[:2]:
                    desc = r.get("classification_desc", r.get("line_code_desc", "?"))
                    print(f"    {desc[:60]}")
    except Exception as e:
        print(f"  Table {table_num}: Error - {e}")
