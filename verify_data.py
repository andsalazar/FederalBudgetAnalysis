"""Verify data coverage and report what we have for each hypothesis."""
import sys
sys.path.insert(0, '.')

from src.database.models import get_session, EconomicSeries, Observation, CollectionLog
from src.utils.config import load_config
from sqlalchemy import func

config = load_config()
session = get_session()

# Overall stats
total_series = session.query(EconomicSeries).count()
total_obs = session.query(Observation).count()
print("=" * 70)
print("DATA COVERAGE REPORT")
print("=" * 70)
print(f"\nTotal series in database: {total_series}")
print(f"Total observations: {total_obs:,}")

# Per-series detail
print(f"\n{'Series ID':<25} {'Source':<10} {'Obs':>8} {'Start':>12} {'End':>12}")
print("-" * 70)

series_list = session.query(EconomicSeries).order_by(EconomicSeries.source, EconomicSeries.series_id).all()
for s in series_list:
    obs_count = session.query(Observation).filter_by(series_id=s.series_id).count()
    min_date = session.query(func.min(Observation.date)).filter_by(series_id=s.series_id).scalar()
    max_date = session.query(func.max(Observation.date)).filter_by(series_id=s.series_id).scalar()
    print(f"{s.series_id:<25} {s.source:<10} {obs_count:>8} {str(min_date):>12} {str(max_date):>12}")

# Hypothesis coverage
print("\n" + "=" * 70)
print("HYPOTHESIS COVERAGE")
print("=" * 70)

hypothesis_map = config.get('analysis', {}).get('hypothesis_series_map', {})
for hyp, series_ids in hypothesis_map.items():
    print(f"\n--- {hyp} ---")
    for sid in series_ids:
        obs_count = session.query(Observation).filter_by(series_id=sid).count()
        if obs_count > 0:
            max_date = session.query(func.max(Observation.date)).filter_by(series_id=sid).scalar()
            print(f"  ✓ {sid:<25} {obs_count:>6} obs, latest: {max_date}")
        else:
            print(f"  ✗ {sid:<25} NO DATA")

# 2025 data availability
print("\n" + "=" * 70)
print("2025 DATA AVAILABILITY (critical for hypothesis testing)")
print("=" * 70)

from datetime import date
for s in series_list:
    obs_2025 = session.query(Observation).filter(
        Observation.series_id == s.series_id,
        Observation.date >= date(2025, 1, 1)
    ).count()
    if obs_2025 > 0:
        latest = session.query(func.max(Observation.date)).filter(
            Observation.series_id == s.series_id,
            Observation.date >= date(2025, 1, 1)
        ).scalar()
        print(f"  ✓ {s.series_id:<25} {obs_2025:>4} obs in 2025 (latest: {latest})")

# Errors
print("\n" + "=" * 70)
print("COLLECTION ERRORS")
print("=" * 70)
errors = session.query(CollectionLog).filter_by(status='error').all()
for e in errors:
    msg = str(e.error_message)[:80] if e.error_message is not None else 'Unknown'
    print(f"  ✗ {e.series_id:<25} {msg}")

session.close()
