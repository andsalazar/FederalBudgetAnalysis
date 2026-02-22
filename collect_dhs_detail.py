"""
Collect DHS sub-agency spending from Treasury MTS Table 5.
Sub-agencies are listed alphabetically as individual entries (data_type_cd='D'),
not grouped under DHS. Amounts are in DOLLARS (divide by 1e9 for billions).
"""
import sys, os, json, requests
sys.path.insert(0, '.')

from datetime import date
from src.database.models import get_session, EconomicSeries, Observation

session = get_session()
BASE = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_5"
NET = "current_fytd_net_outly_amt"

# DHS sub-agencies — exact classification_desc from MTS Table 5
TARGETS = {
    "Total--Department of Homeland Security": "MTS_DHS_Total",
    "Immigration and Customs Enforcement":    "MTS_DHS_ICE",
    "U.S. Customs and Border Protection":     "MTS_DHS_CBP",
    "Customs and Border Protection":          "MTS_DHS_CBP",
    "United States Coast Guard":              "MTS_DHS_Coast_Guard",
    "U.S. Coast Guard":                       "MTS_DHS_Coast_Guard",
    "Transportation Security Administration": "MTS_DHS_TSA",
    "United States Secret Service":           "MTS_DHS_Secret_Service",
    "U.S. Secret Service":                    "MTS_DHS_Secret_Service",
    "Citizenship and Immigration Services":   "MTS_DHS_USCIS",
    "U.S. Citizenship and Immigration Services": "MTS_DHS_USCIS",
    "Total--Federal Emergency Management Agency": "MTS_DHS_FEMA",
    "Federal Emergency Management Agency":    "MTS_DHS_FEMA",
}


def save_obs(series_id, title, fy, amt_dollars):
    """Save observation. amt_dollars is raw dollar amount from API."""
    val_billions = amt_dollars / 1e9
    obs_date = date(fy, 9, 30)
    
    ex = session.query(EconomicSeries).filter_by(series_id=series_id).first()
    if not ex:
        session.add(EconomicSeries(
            series_id=series_id, source='Treasury_MTS',
            title=title, units='Billions of Dollars', frequency='Annual'))
    
    ex_obs = session.query(Observation).filter_by(series_id=series_id, date=obs_date).first()
    if ex_obs:
        ex_obs.value = val_billions
    else:
        session.add(Observation(series_id=series_id, date=obs_date, value=val_billions))


print("=" * 70)
print("  COLLECTING DHS SUB-AGENCY DATA (FY2015-FY2025)")
print("=" * 70)

collected = 0
for fy in range(2015, 2026):
    params = {
        "filter": f"record_fiscal_year:eq:{fy},record_calendar_month:eq:09",
        "fields": f"classification_desc,{NET},data_type_cd",
        "page[size]": 10000,
    }
    try:
        resp = requests.get(BASE, params=params, timeout=30)
        rows = resp.json().get('data', [])
    except Exception as e:
        print(f"  FY{fy}: error - {e}")
        continue

    found = []
    for row in rows:
        desc = row['classification_desc'].strip()
        amt_str = row[NET]
        if not amt_str or amt_str == 'null':
            continue
        
        for target_desc, series_id in TARGETS.items():
            if desc == target_desc or target_desc in desc or desc in target_desc:
                save_obs(series_id, f"DHS: {desc}", fy, float(amt_str))
                if series_id not in [f[0] for f in found]:
                    found.append((series_id, float(amt_str) / 1e9))
                collected += 1
                break

    session.commit()
    found_str = ", ".join(f"{s[0].replace('MTS_DHS_','')} ${s[1]:.1f}B" for s in found)
    print(f"  FY{fy}: {len(found)} agencies — {found_str}")

print(f"\n  Total observations: {collected}")


# ── Summary in real 2024 dollars ─────────────────────────────────────
print("\n" + "=" * 70)
print("  DHS & ICE SPENDING (Real 2024$)")
print("=" * 70)

with open(os.path.join('output', 'tables', 'cpi_deflators.json')) as f:
    deflators = json.load(f)
fy_def = {int(k): v for k, v in deflators['fiscal_year'].items()}

order = ['MTS_DHS_Total', 'MTS_DHS_CBP', 'MTS_DHS_ICE', 'MTS_DHS_FEMA',
         'MTS_DHS_Coast_Guard', 'MTS_DHS_TSA', 'MTS_DHS_USCIS', 'MTS_DHS_Secret_Service']

print(f"\n  {'Sub-Agency':<25} {'FY17':>8} {'FY18':>8} {'FY19':>8} {'FY20':>8} {'FY21':>8} {'FY22':>8} {'FY23':>8} {'FY24':>8} {'FY25':>8} {'Δ20→25':>9}")
print(f"  {'-'*25} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*9}")

for sid in order:
    vals = {}
    for yr in range(2017, 2026):
        obs = session.query(Observation).filter_by(series_id=sid, date=date(yr, 9, 30)).first()
        if obs:
            vals[yr] = obs.value * fy_def.get(yr, 1.0)
    
    if not vals:
        continue
    
    label = sid.replace('MTS_DHS_', '')
    v20 = vals.get(2020, 0)
    v25 = vals.get(2025, 0)
    delta = v25 - v20
    
    row_str = f"  {label:<25}"
    for yr in range(2017, 2026):
        v = vals.get(yr, 0)
        if v:
            row_str += f" ${v:>5.1f}B"
        else:
            row_str += f" {'--':>7}"
    row_str += f" {delta:>+8.1f}B"
    print(row_str)

print(f"""
  ANSWER TO YOUR QUESTION:
    ✗ DHS and ICE are NOT part of Defense spending.
    
    Defense spending (budget function 050) = Department of Defense military
    programs + some DOE nuclear weapons = ~$875B in FY2024.
    
    DHS is a SEPARATE cabinet department created in 2003. Its sub-agencies:
      - CBP (Customs & Border Protection): border security, ports of entry
      - ICE (Immigration & Customs Enforcement): immigration enforcement,
        deportation operations, Enforcement & Removal Operations (ERO)
      - FEMA: disaster relief (often the largest DHS outlay)
      - Coast Guard: maritime security
      - TSA: airport/transportation security
      - USCIS: immigration benefits processing (visas, green cards)
      - Secret Service: presidential protection + financial crimes
    
    Total DHS (~$89B in FY2024) is about 1/10th of Defense (~$875B).
    ICE specifically is ~$10B/year — a small agency by federal standards.
""")

session.close()
print("Done.")
