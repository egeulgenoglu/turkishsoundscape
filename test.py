import requests, base64, json

auth = base64.b64encode('2348db0864b4498ea20b6015473770b5:819a70f0160747a38818b21ca0f752e3'.encode()).decode()
r = requests.post('https://accounts.spotify.com/api/token', headers={'Authorization': 'Basic ' + auth}, data={'grant_type': 'client_credentials'})
token = r.json()['access_token']

r2 = requests.get('https://api.spotify.com/v1/search', 
    headers={'Authorization': f'Bearer {token}'}, 
    params={'q': 'The Sound of Turkish Pop', 'type': 'playlist', 'limit': 5})

print(json.dumps(r2.json(), indent=2, ensure_ascii=False)[:3000])