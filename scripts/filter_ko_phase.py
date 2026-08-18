import json

with open("../data/fixtures_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

fixtures = data["response"]

# Nur diese Runden wollen wir behalten
ko_runden = ["Round of 16", "Quarter-finals", "Semi-finals", "Final"]

# Liste, in die wir die passenden Spiele einsammeln
ko_fixtures = []

for spiel in fixtures:
    if spiel["league"]["round"] in ko_runden:
        ko_fixtures.append(spiel)

print("Anzahl K.o.-Spiele:", len(ko_fixtures))

# Nur die gefilterten Spiele speichern (nicht die ganze Saison)
with open("../data/fixtures_ko.json", "w", encoding="utf-8") as f:
    json.dump(ko_fixtures, f, ensure_ascii=False, indent=2)

print("Gespeichert unter data/fixtures_ko.json")