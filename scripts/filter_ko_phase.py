"""Schritt 2: Aus allen Saisonspielen nur die K.-o.-Phase behalten."""
import json

from config import FIXTURES_KO, FIXTURES_RAW

with open(FIXTURES_RAW, "r", encoding="utf-8") as f:
    data = json.load(f)

fixtures = data["response"]

# Nur diese Runden wollen wir behalten
ko_runden = ["Round of 16", "Quarter-finals", "Semi-finals", "Final"]

# Liste, in die wir die passenden Spiele einsammeln
ko_fixtures = []

for spiel in fixtures:
    if spiel["league"]["round"] in ko_runden:
        ko_fixtures.append(spiel)

print("Anzahl K.-o.-Spiele:", len(ko_fixtures))

# Nur die gefilterten Spiele speichern (nicht die ganze Saison)
with open(FIXTURES_KO, "w", encoding="utf-8") as f:
    json.dump(ko_fixtures, f, ensure_ascii=False, indent=2)

print("Gespeichert unter", FIXTURES_KO)
