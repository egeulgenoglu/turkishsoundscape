import requests
import re
import json

r = requests.get(
    'https://everynoise.com/research.cgi?mode=genre&name=turkce+drill',
    headers={'User-Agent': 'Mozilla/5.0'}
)

# Token'ı bul
match = re.search(r"Bearer ([A-Za-z0-9\-_]+)", r.text)
token = match.group(1)
print(f"Token: {token[:30]}...")

# Every Noise'un kendi API'sini dene
endpoints = [
    "https://everynoise.com/api/genre?name=turkce+drill",
    "https://everynoise.com/api/artists?genre=turkce+drill",
    "https://everynoise.com/api/genre/turkce+drill",
]

for url in endpoints:
    r2 = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Authorization': f'Bearer {token}'
    })
    print(f"\n{url}")
    print(f"Status: {r2.status_code}")
    print(r2.text[:300])