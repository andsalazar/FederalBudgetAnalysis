"""Quick script to find correct FRED series IDs for the ones that failed."""
import requests
import time

api_key = '43272fac437c873feb1ace8519a979fc'

searches = {
    'FTTCPI': 'federal tax collections CPI adjusted',
    'IITTCPI': 'individual income tax collections', 
    'IITTRL': 'individual income tax revenue monthly',
    'CUSR0000SAF1': 'CPI food at home',
    'CUSR0000SAA': 'CPI apparel',
    'CUSR0000SAM': 'CPI medical care',
    'CUSR0000SAE': 'CPI education communication',
}

for bad_id, search in searches.items():
    r = requests.get(
        f'https://api.stlouisfed.org/fred/series/search',
        params={'search_text': search, 'api_key': api_key, 'file_type': 'json', 'limit': 5}
    )
    data = r.json()
    print(f'--- {bad_id} ({search}) ---')
    for s in data.get('seriess', [])[:5]:
        print(f"  {s['id']:25s} | freq={s.get('frequency_short','?'):5s} | {s['title'][:70]}")
    print()
    time.sleep(0.5)
