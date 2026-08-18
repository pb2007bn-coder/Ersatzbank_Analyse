import requests

# Dein API-Key von api-sports.io (den ersetzt du mit deinem echten Key)
API_KEY = "ea52795b547a87c2fe1a8470f14b76c7"

# Die Basis-Adresse der API
BASE_URL = "https://v3.football.api-sports.io"

# Header: so "identifiziert" sich dein Skript bei der API
headers = {
    "x-apisports-key": API_KEY
}

# Anfrage an den /status-Endpoint (zeigt dir Account-Infos, kostet keine Anfragen)
response = requests.get(f"{BASE_URL}/status", headers=headers)

# Den Statuscode ausgeben (200 = alles ok)
print("Statuscode:", response.status_code)

# Die Antwort als JSON ausgeben
print(response.json())