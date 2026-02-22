"""Inspect Treasury Table 5 for agency-level outlays."""
import requests

url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_5"
params = {
    "filter": "record_calendar_month:eq:09,record_fiscal_year:eq:2024",
    "page[size]": 500,
    "sort": "sequence_number_cd",
}
resp = requests.get(url, params=params, timeout=30)
data = resp.json()
records = data.get("data", [])
print(f"Records: {len(records)}, Total: {data.get('meta',{}).get('total-count')}")

print("\nFields:", list(records[0].keys()) if records else "N/A")

seen = set()
for r in records:
    desc = r.get("classification_desc", "")
    seq = r.get("sequence_level_nbr", "")
    parent = r.get("parent_id", "")
    gross_str = r.get("fytd_gross_outly_amt", r.get("current_fytd_gross_outly_amt", "0"))
    app_str = r.get("fytd_app_rcpt_amt", r.get("current_fytd_app_rcpt_amt", "0"))
    try:
        gross = float(gross_str) / 1e9
    except:
        gross = 0
    try:
        app = float(app_str) / 1e9
    except:
        app = 0
    key = desc
    if key not in seen and seq == "1":
        seen.add(key)
        print(f"  seq={seq} parent={parent[:10]:<10} {desc:<55} gross=${gross:>8.1f}B  app=${app:>8.1f}B")
