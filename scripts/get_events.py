"""Schritt 3: Für jedes K.-o.-Spiel die Ereignisse (Tore, Wechsel, Karten) holen."""
import json
import time

import requests

from config import BASE_URL, EVENTS_DIR, FIXTURES_KO, get_headers

headers = get_headers()

# Den Ordner für die Events anlegen, falls er noch nicht existiert
EVENTS_DIR.mkdir(parents=True, exist_ok=True)

# Die gefilterten K.-o.-Spiele einlesen
with open(FIXTURES_KO, "r", encoding="utf-8") as f:
    ko_fixtures = json.load(f)



def ist_vollstaendig(dateipfad):
    """Prüft, ob für ein Spiel schon eine gültige Datei mit Events vorliegt."""
    if not dateipfad.exists():
        return False
    with open(dateipfad, "r", encoding="utf-8") as f:
        inhalt = json.load(f)
    # Eine gespeicherte Fehlerantwort hat eine leere "response"-Liste
    return bool(inhalt.get("response"))


fehlgeschlagen = []

for i, spiel in enumerate(ko_fixtures, start=1):
    fixture_id = spiel["fixture"]["id"]
    dateipfad = EVENTS_DIR / f"{fixture_id}.json"

    # Wenn schon eine gültige Datei existiert, haben wir das Spiel schon abgerufen
    # -> überspringen. So kann man das Skript nach einem Abbruch einfach noch einmal
    # starten. Dateien mit einer Fehlerantwort werden neu abgerufen.
    if ist_vollstaendig(dateipfad):
        print(f"[{i}/{len(ko_fixtures)}] {fixture_id} bereits vorhanden, übersprungen")
        continue

    # Anfrage für dieses eine Spiel
    params = {"fixture": fixture_id}
    response = requests.get(
        f"{BASE_URL}/fixtures/events", headers=headers, params=params, timeout=30
    )

    # Nur speichern, wenn die Antwort wirklich Daten enthält.
    # Sonst würde eine Fehlerantwort als Datei liegen bleiben und das Spiel
    # beim nächsten Lauf fälschlich übersprungen werden.
    try:
        data = response.json()
    except ValueError:
        data = {}

    if response.status_code != 200 or data.get("errors") or not data.get("response"):
        grund = data.get("errors") or "keine Daten in der Antwort"
        print(f"[{i}/{len(ko_fixtures)}] {fixture_id} FEHLER "
              f"(Statuscode {response.status_code}): {grund}")
        fehlgeschlagen.append(fixture_id)
    else:
        with open(dateipfad, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[{i}/{len(ko_fixtures)}] {fixture_id} gespeichert")

    # Kurze Pause, um das Anfragelimit der API nicht zu überschreiten
    time.sleep(7)

if fehlgeschlagen:
    print(f"\nFertig, aber {len(fehlgeschlagen)} Spiel(e) fehlen noch: {fehlgeschlagen}")
    print("Skript später noch einmal starten, vorhandene Spiele werden übersprungen.")
else:
    print("\nFertig! Alle Spiele sind vorhanden.")
