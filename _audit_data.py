"""Audit database freshness and output file ages."""
import sqlite3, os, json, glob
from datetime import datetime

db = sqlite3.connect('data/federal_budget.db')

# Schema
print('=== DATABASE SCHEMA ===')
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    name = t[0]
    count = db.execute(f'SELECT COUNT(*) FROM [{name}]').fetchone()[0]
    cols = db.execute(f'PRAGMA table_info([{name}])').fetchall()
    col_names = [c[1] for c in cols]
    print(f'  {name}: {count} rows, cols: {col_names}')

# economic_series sample
print('\n=== ECONOMIC SERIES (sample) ===')
rows = db.execute('SELECT series_id, source, title FROM economic_series LIMIT 15').fetchall()
for r in rows:
    print(f'  {r[0]:35s} src={r[1]:10s} {r[2][:60]}')
total = db.execute('SELECT COUNT(DISTINCT series_id) FROM economic_series').fetchone()[0]
print(f'  ... total distinct series: {total}')

# observations date ranges by source
print('\n=== OBSERVATIONS DATE RANGES BY SOURCE ===')
rows = db.execute('''
    SELECT e.source, COUNT(DISTINCT e.series_id), MIN(o.date), MAX(o.date), COUNT(*)
    FROM observations o JOIN economic_series e ON o.series_id = e.id
    GROUP BY e.source
    ORDER BY e.source
''').fetchall()
for r in rows:
    print(f'  src={r[0]:15s} series={r[1]:4d}  {r[2]} to {r[3]}  ({r[4]} obs)')

# Per-series detail for most recent obs
print('\n=== TOP 20 SERIES BY LATEST OBS DATE ===')
rows = db.execute('''
    SELECT e.series_id, e.source, MAX(o.date) as maxd, COUNT(*) as cnt
    FROM observations o JOIN economic_series e ON o.series_id = e.id
    GROUP BY e.series_id
    ORDER BY maxd DESC
    LIMIT 20
''').fetchall()
for r in rows:
    print(f'  {r[0]:35s} src={r[1]:12s} latest={r[2]}  ({r[3]} obs)')

# collection_log
print('\n=== COLLECTION LOG (recent) ===')
try:
    rows = db.execute('SELECT * FROM collection_log ORDER BY rowid DESC LIMIT 10').fetchall()
    for r in rows:
        print(f'  {r}')
except Exception as ex:
    print(f'  Error: {ex}')

db.close()

# DB file mod time
print(f'\nDB last modified: {datetime.fromtimestamp(os.path.getmtime("data/federal_budget.db"))}')

# Output files and their ages
print('\n=== OUTPUT FILE AGES ===')
for pattern in ['output/tables/*.json', 'output/tables/*.csv', 'output/figures/*.png',
                'output/figures/tables/*.json']:
    files = sorted(glob.glob(pattern))
    for f in files:
        mtime = datetime.fromtimestamp(os.path.getmtime(f))
        size = os.path.getsize(f)
        print(f'  {mtime.strftime("%Y-%m-%d %H:%M")}  {size:>10,d}B  {os.path.basename(f)}')

# Processed data files
print('\n=== PROCESSED DATA FILE AGES ===')
for f in sorted(glob.glob('data/processed/*')):
    mtime = datetime.fromtimestamp(os.path.getmtime(f))
    size = os.path.getsize(f)
    print(f'  {mtime.strftime("%Y-%m-%d %H:%M")}  {size:>10,d}B  {os.path.basename(f)}')

# Key numbers from existing JSON results
print('\n=== CURRENT KEY NUMBERS ===')
for jf in ['output/tables/counterfactual_analysis_results.json',
           'output/tables/tariff_incidence_analysis.json',
           'output/tables/robustness_summary.json',
           'output/tables/real_terms_analysis.json']:
    if os.path.exists(jf):
        data = json.load(open(jf))
        print(f'\n--- {os.path.basename(jf)} ---')
        for k, v in data.items():
            if isinstance(v, (int, float, str, bool)):
                print(f'  {k}: {v}')
            elif isinstance(v, dict) and len(str(v)) < 300:
                print(f'  {k}: {v}')
            else:
                print(f'  {k}: <{type(v).__name__} len={len(v) if hasattr(v,"__len__") else "?"}>')
