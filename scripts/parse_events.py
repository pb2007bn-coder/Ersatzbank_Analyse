import json
import os
import pandas as pd

# Pfade definieren
events_dir = "../data/events"
processed_dir = "../data/processed"
parsed_events = []

# Alle gespeicherten Event-Dateien durchgehen
for filename in os.listdir(events_dir):
    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(events_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Prüfen, ob eine gültige API-Antwort vorliegt
    events = data.get("response", [])
    if not isinstance(events, list):
        continue

    fixture_id = filename.replace(".json", "")

    for event in events:
        event_type = event.get("type")
        
        # Wir filtern gezielt nach Einwechslungen ('subst') und Toren ('Goal')
        if event_type in ["subst", "Goal"]:
            parsed_events.append({
                "fixture_id": fixture_id,
                "minute": event.get("time", {}).get("elapsed"),
                "extra_minute": event.get("time", {}).get("extra"),
                "team_name": event.get("team", {}).get("name"),
                "player_name": event.get("player", {}).get("name"),
                "assist_or_in": event.get("assist", {}).get("name"),  # Bei Wechsel: reinkommender Spieler
                "event_type": event_type,
                "detail": event.get("detail")
            })

# In ein Pandas DataFrame umwandeln
df = pd.DataFrame(parsed_events)

# Ordner für aufbereitete Daten erstellen & als CSV speichern
os.makedirs(processed_dir, exist_ok=True)
output_path = os.path.join(processed_dir, "events_clean.csv")
df.to_csv(output_path, index=False, encoding="utf-8")

print(f"Erfolg! {len(df)} relevante Events extrahiert und in '{output_path}' gespeichert.")