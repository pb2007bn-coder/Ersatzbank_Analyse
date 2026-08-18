import requests
import json

API_KEY = "ea52795b547a87c2fe1a8470f14b76c7"
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-apisports-key": API_KEY
}

# Parameter für die Anfrage: welche Liga, welche Saison
params = {
    "league": 2,      # 2 = UEFA Champions League
    "season": 2022     # Saison 2022/23
}

# Anfrage an den /fixtures-Endpoint
response = requests.get(f"{BASE_URL}/fixtures", headers=headers, params=params)

print("Statuscode:", response.status_code)

data = response.json()
print("Anzahl Spiele gefunden:", data["results"])

# Die kompletten Rohdaten als JSON-Datei speichern
with open("../data/fixtures_raw.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Gespeichert unter data/fixtures_raw.json")