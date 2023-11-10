import requests as req

login_headers={
    "Content-Type": "application/x-www-form-urlencoded", 
}

# SPOTIPY_CLIENT_ID = '0387ebd733aa4a8e97ab976f87422cf1'
# SPOTIPY_CLIENT_SECRET = '0fbdb2b2366c4d44b01a7fb28c882de0'

SPOTIPY_CLIENT_ID = 'dfa8b23916c140f5b7c7572da25c4734'
SPOTIPY_CLIENT_SECRET = 'e65a6c357d80435fb629f41677abff3f'

login_data = {
    "grant_type": "client_credentials",
    "client_id": SPOTIPY_CLIENT_ID,
    'client_secret': SPOTIPY_CLIENT_SECRET
}

res = req.post('https://accounts.spotify.com/api/token', headers=login_headers, data=login_data)
token = res.json()['access_token']

req = req.get(f'https://api.spotify.com/v1/recommendations?seed_tracks=4um6CPDIxnNWSEbj3LJQhQ', headers={'Authorization': f'Bearer {token}'})

print(req.headers, req.text)