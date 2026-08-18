import requests
import json
import os
import time

API_KEY = "Dein_API_KEY_hier"
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-apisports-key": API_KEY
}

# Den Ordner für die Events anlegen, falls er noch nicht existiert
os.makedirs("../data/events", exist_ok=True)

# Die gefilterten K.o.-Spiele einlesen
with open("../data/fixtures_ko.json", "r", encoding="utf-8") as f:
    ko_fixtures = json.load(f)

for i, spiel in enumerate(ko_fixtures, start=1):
    fixture_id = spiel["fixture"]["id"]
    dateipfad = f"../data/events/{fixture_id}.json"

    # Wenn die Datei schon existiert, haben wir das Spiel schon abgerufen -> überspringen
    if os.path.exists(dateipfad):
        print(f"[{i}/{len(ko_fixtures)}] {fixture_id} bereits vorhanden, übersprungen")
        continue

    # Anfrage für dieses eine Spiel
    params = {"fixture": fixture_id}
    response = requests.get(f"{BASE_URL}/fixtures/events", headers=headers, params=params)
    data = response.json()

    with open(dateipfad, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[{i}/{len(ko_fixtures)}] {fixture_id} gespeichert (Statuscode {response.status_code})")

    # Kurze Pause, um die API nicht zu überlasten
    time.sleep(7)

print("Fertig!")