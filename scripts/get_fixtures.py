"""Schritt 1: Alle Spiele der Champions-League-Saison 2022/23 von der API holen."""
import json

import requests

from config import BASE_URL, DATA_DIR, FIXTURES_RAW, get_headers

# Parameter für die Anfrage: welche Liga, welche Saison
params = {
    "league": 2,      # 2 = UEFA Champions League
    "season": 2022,   # Saison 2022/23
}

# Anfrage an den /fixtures-Endpoint
response = requests.get(
    f"{BASE_URL}/fixtures", headers=get_headers(), params=params, timeout=30
)
print("Statuscode:", response.status_code)

data = response.json()

# Die API antwortet auch bei Fehlern (z. B. Tageslimit erreicht) mit Statuscode 200
# und schreibt den Grund in das Feld "errors". Deshalb beides prüfen.
if response.status_code != 200 or data.get("errors"):
    raise SystemExit(f"Abruf fehlgeschlagen: {data.get('errors')}")

print("Anzahl Spiele gefunden:", data["results"])

# Die kompletten Rohdaten als JSON-Datei speichern
DATA_DIR.mkdir(parents=True, exist_ok=True)
with open(FIXTURES_RAW, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Gespeichert unter", FIXTURES_RAW)
