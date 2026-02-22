import pandas as pd, numpy as np
df = pd.read_csv('data/external/cps_asec_2024_microdata.csv')
wt = df['MARSUPWT'].values / 100
hh = df.groupby('PH_SEQ').agg(hh_income=('pretax_income','sum')).reset_index()
df2 = df.merge(hh[['PH_SEQ','hh_income']], on='PH_SEQ')

wt2 = df2['MARSUPWT'].values / 100

# PSZ B50 (person-level income)
psz_b50_mask = df['pretax_income'] < 35021
psz_mean_pre = np.average(df.loc[psz_b50_mask, 'pretax_income'], weights=wt[psz_b50_mask])
psz_mean_post = np.average(df.loc[psz_b50_mask, 'posttax_income'], weights=wt[psz_b50_mask])

# HH-income B50
hh_b50_mask = df2['hh_income'] < 96000
hh_mean_pre = np.average(df2.loc[hh_b50_mask, 'pretax_income'], weights=wt2[hh_b50_mask])
hh_mean_post = np.average(df2.loc[hh_b50_mask, 'posttax_income'], weights=wt2[hh_b50_mask])

total_pretax = np.sum(df2['pretax_income'] * wt2)
hh_b50_pretax = np.sum(df2.loc[hh_b50_mask, 'pretax_income'] * wt2[hh_b50_mask])

lines = [
    f"PSZ B50 mean pretax: {psz_mean_pre:.0f}",
    f"PSZ B50 mean posttax: {psz_mean_post:.0f}",
    f"HH B50 mean pretax: {hh_mean_pre:.0f}",
    f"HH B50 mean posttax: {hh_mean_post:.0f}",
    f"HH B50 pretax income share: {hh_b50_pretax/total_pretax*100:.1f}%",
    f"PSZ B50 count: {np.sum(wt[psz_b50_mask]):.0f}",
    f"HH B50 count: {np.sum(wt2[hh_b50_mask]):.0f}",
]
with open('_b50_compare.txt', 'w') as f:
    f.write('\n'.join(lines))
print('\n'.join(lines))
