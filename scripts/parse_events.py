"""Schritt 4: Aus den verschachtelten JSON-Dateien zwei saubere CSV-Tabellen bauen.

- fixtures_clean.csv: eine Zeile pro K.-o.-Spiel (Runde, Teams, Ergebnis)
- events_clean.csv:   eine Zeile pro Tor oder Wechsel
"""
import json

import pandas as pd

from config import EVENTS_CSV, EVENTS_DIR, FIXTURES_CSV, FIXTURES_KO, PROCESSED_DIR

# Die K.-o.-Spiele einlesen und nach Datum sortieren
with open(FIXTURES_KO, "r", encoding="utf-8") as f:
    ko_fixtures = json.load(f)

ko_fixtures.sort(key=lambda spiel: spiel["fixture"]["date"])

parsed_fixtures = []
parsed_events = []

for spiel in ko_fixtures:
    fixture_id = spiel["fixture"]["id"]
    runde = spiel["league"]["round"]

    # Event-Datei zu diesem Spiel laden, falls sie vorhanden und gültig ist
    events = []
    dateipfad = EVENTS_DIR / f"{fixture_id}.json"
    if dateipfad.exists():
        with open(dateipfad, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data.get("response"), list):
            events = data["response"]

    if not events:
        print(f"Hinweis: Für Spiel {fixture_id} ({runde}: "
              f"{spiel['teams']['home']['name']} - {spiel['teams']['away']['name']}) "
              "liegen keine Event-Daten vor. Es fehlt in der Auswertung.")

    parsed_fixtures.append({
        "fixture_id": fixture_id,
        "date": spiel["fixture"]["date"][:10],
        "round": runde,
        "home_team": spiel["teams"]["home"]["name"],
        "away_team": spiel["teams"]["away"]["name"],
        "home_goals": spiel["goals"]["home"],
        "away_goals": spiel["goals"]["away"],
        "has_events": 1 if events else 0,
    })

    for event in events:
        event_type = event.get("type")

        # Wir filtern gezielt nach Einwechslungen ('subst') und Toren ('Goal')
        if event_type in ["subst", "Goal"]:
            parsed_events.append({
                "fixture_id": fixture_id,
                "minute": event.get("time", {}).get("elapsed"),
                "extra_minute": event.get("time", {}).get("extra"),  # Nachspielzeit
                "team_name": event.get("team", {}).get("name"),
                # Bei Tor: Torschütze. Bei Wechsel: der Spieler, der rausgeht.
                "player_name": event.get("player", {}).get("name"),
                # Bei Tor: Vorlagengeber. Bei Wechsel: der Spieler, der reinkommt.
                "assist_or_in": event.get("assist", {}).get("name"),
                "event_type": event_type,
                "detail": event.get("detail"),
            })

# In Pandas DataFrames umwandeln und als CSV speichern
df_fixtures = pd.DataFrame(parsed_fixtures)
df_events = pd.DataFrame(parsed_events)

# Ganze Zahlen statt Kommazahlen, leere Nachspielzeit bleibt leer
df_events["extra_minute"] = df_events["extra_minute"].astype("Int64")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
df_fixtures.to_csv(FIXTURES_CSV, index=False, encoding="utf-8")
df_events.to_csv(EVENTS_CSV, index=False, encoding="utf-8")

print(f"{len(df_fixtures)} Spiele gespeichert in '{FIXTURES_CSV.name}' "
      f"({df_fixtures['has_events'].sum()} davon mit Event-Daten).")
print(f"{len(df_events)} relevante Events gespeichert in '{EVENTS_CSV.name}'.")
