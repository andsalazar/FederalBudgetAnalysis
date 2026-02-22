"""Inspect Treasury Table 9 structure."""
import requests

url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_9"
params = {
    "filter": "record_calendar_month:eq:09,record_fiscal_year:eq:2024",
    "page[size]": 500,
    "sort": "sequence_number_cd",
}
resp = requests.get(url, params=params, timeout=30)
data = resp.json()
records = data.get("data", [])
meta = data.get("meta", {})
print(f"Records: {len(records)}, Total: {meta.get('total-count')}")

seen = set()
for r in records:
    desc = r.get("classification_desc", "")
    seq = r.get("sequence_level_nbr", "")
    rec_type = r.get("record_type_cd", "")
    data_type = r.get("data_type_cd", "")
    amt_str = r.get("current_fytd_rcpt_outly_amt", "0")
    try:
        amt = float(amt_str) / 1e9
    except:
        amt = 0
    key = desc
    if key not in seen:
        seen.add(key)
        print(f"  seq={seq} rec={rec_type} dt={data_type} {desc:<55} ${amt:>8.1f}B")
