"""
Compute microdata-calibrated B50 tariff burden using CPS ASEC 2024.

The CEX calibration formula Q1+Q2+Q3+0.414×Q4 maps CEX consumer-unit income
quintiles to the bottom 50% of persons by household income rank. This formula
is valid ONLY for CEX quintile-level data (which have unequal person shares:
10.1%, 12.7%, 17.8%, 22.7%, 36.7%).

For CPS ASEC person-income quintile aggregation (where each quintile has
exactly 20% of persons), the bottom 50% by person pretax income = Q1+Q2+0.5×Q3.
"""
import pandas as pd
import numpy as np
import json

# ---- Step 1: CPS ASEC microdata calibration ----
df = pd.read_csv('data/external/cps_asec_2024_microdata.csv')
wt = df['MARSUPWT'].values / 100

# Group by household to get CU-equivalent income
hh = df.groupby('PH_SEQ').agg(hh_income=('pretax_income', 'sum')).reset_index()
df2 = df.merge(hh[['PH_SEQ', 'hh_income']], on='PH_SEQ')

hh_inc = df2['hh_income'].values
total_pop = np.sum(wt)

# Person-weighted P50 of household income
sort_idx = np.argsort(hh_inc)
cum = np.cumsum(wt[sort_idx])
p50_idx = np.searchsorted(cum / total_pop, 0.50)
p50_hh_income = hh_inc[sort_idx[p50_idx]]

print(f"CPS ASEC 2024: {len(df)} persons, {len(hh)} households")
print(f"Person-weighted P50 of HH income: ${p50_hh_income:,.0f}")

# CEX quintile boundaries
q_bounds = {
    'Q1': (float('-inf'), 23810),
    'Q2': (23810, 46063),
    'Q3': (46063, 77025),
    'Q4': (77025, 127080),
    'Q5': (127080, float('inf')),
}

# Count persons in each CEX quintile band
person_counts = {}
for q, (lo, hi) in q_bounds.items():
    mask = (hh_inc >= lo) & (hh_inc < hi)
    person_counts[q] = np.sum(wt[mask])

print("\nPersons per CEX quintile band:")
cum_pct = 0
for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
    pct = person_counts[q] / total_pop * 100
    cum_pct += pct
    print(f"  {q}: {person_counts[q]:,.0f} ({pct:.1f}%, cumulative {cum_pct:.1f}%)")

# Fraction of Q4 persons below P50
q4_mask = (hh_inc >= 77025) & (hh_inc < 127080)
q4_below = q4_mask & (hh_inc < p50_hh_income)
q4_pop = np.sum(wt[q4_mask])
q4_below_pop = np.sum(wt[q4_below])
frac_q4 = q4_below_pop / q4_pop if q4_pop > 0 else 0

print(f"\nQ4 persons below P50 (${p50_hh_income:,.0f}): {frac_q4:.4f} ({frac_q4*100:.1f}%)")
print(f"Calibrated B50 formula: Q1 + Q2 + Q3 + {frac_q4:.3f} x Q4")

# Verify
q123 = sum(person_counts[q] for q in ['Q1', 'Q2', 'Q3'])
b50_calibrated = q123 + frac_q4 * person_counts['Q4']
print(f"Calibrated B50 person share: {b50_calibrated/total_pop*100:.1f}%")

# ---- Step 2: Recompute tariff burden ----
CEX = {
    'Food at home': [4381, 5104, 5594, 6152, 7712],
    'Food away from home': [2231, 2998, 3697, 4647, 7546],
    'Alcoholic beverages': [255, 351, 451, 623, 1093],
    'Apparel and services': [957, 1182, 1535, 1912, 3242],
    'New vehicles': [1093, 1768, 2655, 4023, 5882],
    'Used vehicles': [1246, 1680, 2147, 2445, 2503],
    'Gasoline and motor oil': [1238, 1834, 2260, 2734, 3162],
    'Household furnishings': [668, 988, 1297, 1919, 3810],
    'Major appliances': [163, 214, 274, 366, 576],
    'Consumer electronics': [552, 741, 862, 1058, 1456],
    'Toys and recreation': [343, 487, 754, 1078, 2097],
    'Footwear': [227, 283, 355, 413, 558],
}

tariff_rates = {
    'Food at home': 12, 'Food away from home': 5, 'Alcoholic beverages': 15,
    'Apparel and services': 20, 'New vehicles': 25, 'Used vehicles': 5,
    'Household furnishings': 18, 'Major appliances': 18,
    'Consumer electronics': 22, 'Toys and recreation': 25,
    'Footwear': 20, 'Gasoline and motor oil': 10,
}

n_cu = 27.17e6  # CUs per quintile
tariff_tax = [0.0] * 5
for cat, rate in tariff_rates.items():
    for i in range(5):
        tariff_tax[i] += CEX[cat][i] * (rate / 100) * n_cu

grand = sum(tariff_tax)

print("\n" + "=" * 60)
print("TARIFF BURDEN COMPARISON: OLD vs CALIBRATED B50")
print("=" * 60)

print("\nTariff tax by quintile:")
for i in range(5):
    print(f"  Q{i+1}: ${tariff_tax[i]/1e9:.2f}B ({tariff_tax[i]/grand*100:.1f}%)")
print(f"  Total: ${grand/1e9:.1f}B")

# Three formulas
formulas = {
    'OLD (Q1+Q2+0.25*Q3, ~27% of persons)': 
        tariff_tax[0] + tariff_tax[1] + 0.25 * tariff_tax[2],
    f'CALIBRATED (Q1+Q2+Q3+{frac_q4:.3f}*Q4, 50% of persons)':
        tariff_tax[0] + tariff_tax[1] + tariff_tax[2] + frac_q4 * tariff_tax[3],
    'BOUND_LOW (Q1+Q2+Q3, 40.6% of persons)':
        tariff_tax[0] + tariff_tax[1] + tariff_tax[2],
    'BOUND_HIGH (Q1+Q2+Q3+Q4, 63.3% of persons)':
        tariff_tax[0] + tariff_tax[1] + tariff_tax[2] + tariff_tax[3],
}

b50_pop = 136_571_514
b50_mean_inc = 12_064

for label, val in formulas.items():
    sh = val / grand * 100
    paid_195 = 195 * sh / 100
    paid_100 = 100 * sh / 100
    pp_total = paid_195 * 1e9 / b50_pop
    pp_above = paid_100 * 1e9 / b50_pop
    pct_inc_total = pp_total / b50_mean_inc * 100
    pct_inc_above = pp_above / b50_mean_inc * 100
    print(f"\n{label}:")
    print(f"  B50 share of tariff revenue: {sh:.1f}%")
    print(f"  Of $195B total: ${paid_195:.1f}B")
    print(f"  Of $100B above baseline: ${paid_100:.1f}B")
    print(f"  Per person (total): ${pp_total:.0f}")
    print(f"  Per person (above baseline): ${pp_above:.0f}")
    print(f"  As % of B50 mean income (total): {pct_inc_total:.1f}%")
    print(f"  As % of B50 mean income (above baseline): {pct_inc_above:.1f}%")

# Regressivity: B50 income share vs tariff share
calibrated_share = (tariff_tax[0] + tariff_tax[1] + tariff_tax[2] + frac_q4 * tariff_tax[3]) / grand * 100
print(f"\nRegressivity check:")
print(f"  B50 pretax income share: 11.1%")
print(f"  B50 tariff revenue share (calibrated): {calibrated_share:.1f}%")
print(f"  Ratio: {calibrated_share/11.1:.1f}x their income share")

# Save calibration results
results = {
    'p50_hh_income': float(p50_hh_income),
    'frac_q4_below_p50': float(frac_q4),
    'formula_cex': f'Q1 + Q2 + Q3 + {frac_q4:.3f} * Q4',
    'formula_cex_note': 'Applies to CEX quintile bands (unequal person shares). '
                        'For CPS person-income quintiles (equal 20% shares), '
                        'B50 = Q1 + Q2 + 0.5*Q3.',
    'person_shares': {q: float(person_counts[q]/total_pop*100) for q in ['Q1','Q2','Q3','Q4','Q5']},
    'old_b50_person_share': 27.2,
    'calibrated_b50_person_share': 50.0,
    'old_b50_tariff_share': 28.8,
    'calibrated_b50_tariff_share': round(calibrated_share, 1),
}
with open('output/tables/b50_calibration.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nSaved output/tables/b50_calibration.json")
