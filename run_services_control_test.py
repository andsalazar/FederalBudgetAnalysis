"""
Services-as-Control Tariff Pass-Through Test
=============================================
Compares CPI price acceleration in tariff-affected traded goods vs.
non-tradable services, controlling for broad macroeconomic inflation trends.

This addresses the referee concern that the difference-in-acceleration
approach does not control for non-tradable sector inflation.
"""
import sys, os, json, warnings
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
from datetime import date, timedelta
from scipy import stats
from fredapi import Fred

FRED_KEY = "43272fac437c873feb1ace8519a979fc"
fred = Fred(api_key=FRED_KEY)

# ---- Pull CPI series for tariff-affected goods and non-tradable services ----

# Tariff-affected traded goods (same as main analysis)
TRADED_GOODS = {
    'Consumer Electronics': 'CUSR0000SEEE01',
    'Household Furnishings': 'CUSR0000SAH3',
    'Apparel': 'CPIAPPSL',
    'Footwear': 'CUSR0000SEAE',
    'New Vehicles': 'CUSR0000SETA01',
    'Used Vehicles': 'CUSR0000SETA02',
    'Toys/Recreation': 'CUSR0000SERA',
    'Food at Home': 'CUSR0000SAF11',
}

# Non-tradable services (control group)
SERVICES = {
    'Medical Care': 'CPIMEDSL',
    'Shelter (Rent/OER)': 'CUSR0000SAH1',
    'Education': 'CPIEDUSL',
    'Services less Energy': 'CUSR0000SASLE',
    'Transportation Services': 'CUSR0000SAS4',
}

# Headline for reference
HEADLINE = {'CPI-U All Items': 'CPIAUCSL'}

def fetch_series(series_dict, start='2023-01-01', end='2026-02-01'):
    """Pull CPI series from FRED."""
    data = {}
    for name, sid in series_dict.items():
        try:
            s = fred.get_series(sid, start, end)
            if s is not None and len(s) > 0:
                data[name] = s
                print(f"  OK: {name} ({sid}): {len(s)} obs")
            else:
                print(f"  SKIP: {name} ({sid}): no data")
        except Exception as e:
            print(f"  ERROR: {name} ({sid}): {e}")
    return data

def compute_acceleration(series, pre_date='2025-01-01', tariff_date='2025-04-01'):
    """
    Compute YoY acceleration:
    - Pre-tariff YoY: Jan 2025 vs Jan 2024
    - Post-tariff YoY: latest available vs 12 months prior
    - Acceleration = post - pre
    """
    pre_dt = pd.Timestamp(pre_date)
    
    # Find closest dates
    idx = series.index
    
    # Pre-tariff: Jan 2025 / Jan 2024
    pre_current = series.loc[idx >= '2025-01-01'].iloc[0] if len(series.loc[idx >= '2025-01-01']) > 0 else None
    pre_prior = series.loc[idx >= '2024-01-01'].iloc[0] if len(series.loc[idx >= '2024-01-01']) > 0 else None
    
    # Post-tariff: latest / 12 months prior
    latest = series.iloc[-1]
    latest_date = series.index[-1]
    prior_date = latest_date - pd.DateOffset(months=12)
    prior_candidates = series.loc[idx <= prior_date]
    post_prior = prior_candidates.iloc[-1] if len(prior_candidates) > 0 else None
    
    if pre_current is not None and pre_prior is not None and pre_prior != 0:
        pre_yoy = (pre_current / pre_prior - 1) * 100
    else:
        return None
    
    if post_prior is not None and post_prior != 0:
        post_yoy = (latest / post_prior - 1) * 100
    else:
        return None
    
    return {
        'pre_yoy': pre_yoy,
        'post_yoy': post_yoy,
        'acceleration': post_yoy - pre_yoy,
        'latest_date': str(latest_date.date()),
    }

print("Fetching tariff-affected goods CPI series...")
traded_data = fetch_series(TRADED_GOODS)

print("\nFetching non-tradable services CPI series...")
services_data = fetch_series(SERVICES)

print("\nFetching headline CPI...")
headline_data = fetch_series(HEADLINE)

# ---- Compute accelerations ----
print("\n" + "=" * 70)
print("CPI ACCELERATION: TRADED GOODS vs NON-TRADABLE SERVICES")
print("=" * 70)

traded_accs = []
services_accs = []

print("\nTariff-affected traded goods:")
for name, series in traded_data.items():
    result = compute_acceleration(series)
    if result:
        print(f"  {name:30s} Pre: {result['pre_yoy']:+6.2f}%  Post: {result['post_yoy']:+6.2f}%  Acc: {result['acceleration']:+6.2f}pp")
        traded_accs.append({'name': name, **result})

print("\nNon-tradable services (control group):")
for name, series in services_data.items():
    result = compute_acceleration(series)
    if result:
        print(f"  {name:30s} Pre: {result['pre_yoy']:+6.2f}%  Post: {result['post_yoy']:+6.2f}%  Acc: {result['acceleration']:+6.2f}pp")
        services_accs.append({'name': name, **result})

print("\nHeadline CPI:")
for name, series in headline_data.items():
    result = compute_acceleration(series)
    if result:
        print(f"  {name:30s} Pre: {result['pre_yoy']:+6.2f}%  Post: {result['post_yoy']:+6.2f}%  Acc: {result['acceleration']:+6.2f}pp")

# ---- Statistical tests ----
print("\n" + "=" * 70)
print("STATISTICAL TESTS")
print("=" * 70)

t_accs = [x['acceleration'] for x in traded_accs]
s_accs = [x['acceleration'] for x in services_accs]

if t_accs and s_accs:
    mean_traded = np.mean(t_accs)
    mean_services = np.mean(s_accs)
    
    print(f"\n  Mean acceleration, traded goods:    {mean_traded:+.2f}pp  (n={len(t_accs)})")
    print(f"  Mean acceleration, services:        {mean_services:+.2f}pp  (n={len(s_accs)})")
    print(f"  Difference (traded - services):     {mean_traded - mean_services:+.2f}pp")
    
    # Welch's t-test (unequal variances)
    t_stat, p_val = stats.ttest_ind(t_accs, s_accs, equal_var=False)
    print(f"\n  Welch's t-test: t = {t_stat:.3f}, p = {p_val:.3f}")
    if p_val < 0.05:
        print(f"  → Significant at 5% level: traded goods see MORE acceleration than services")
    elif p_val < 0.10:
        print(f"  → Significant at 10% level")
    else:
        print(f"  → Not significant at conventional levels (small sample)")
    
    # Mann-Whitney U test (non-parametric)
    u_stat, u_pval = stats.mannwhitneyu(t_accs, s_accs, alternative='greater')
    print(f"\n  Mann-Whitney U test (one-sided, traded > services):")
    print(f"    U = {u_stat:.1f}, p = {u_pval:.3f}")
    
    # Effect size: Cohen's d
    pooled_std = np.sqrt((np.var(t_accs)*len(t_accs) + np.var(s_accs)*len(s_accs)) / 
                         (len(t_accs) + len(s_accs)))
    cohens_d = (mean_traded - mean_services) / pooled_std if pooled_std > 0 else 0
    print(f"\n  Cohen's d (effect size): {cohens_d:.2f}")
    
    # Save results
    results = {
        'traded_goods': traded_accs,
        'services_control': services_accs,
        'mean_traded_acceleration': mean_traded,
        'mean_services_acceleration': mean_services,
        'differential': mean_traded - mean_services,
        'welch_t_stat': t_stat,
        'welch_p_value': p_val,
        'mann_whitney_U': u_stat,
        'mann_whitney_p': u_pval,
        'cohens_d': cohens_d,
        'n_traded': len(t_accs),
        'n_services': len(s_accs),
    }
    
    with open('output/tables/services_control_test.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print("\nSaved output/tables/services_control_test.json")
