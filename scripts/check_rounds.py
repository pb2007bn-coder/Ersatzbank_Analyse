"""Hilfsskript: zeigt, welche Rundennamen in den Rohdaten vorkommen."""
import json

from config import FIXTURES_RAW

# Die gespeicherte Datei wieder einlesen
with open(FIXTURES_RAW, "r", encoding="utf-8") as f:
    data = json.load(f)

# Alle Spiele stehen in der Liste "response"
fixtures = data["response"]

# Ein "Set" sammelt automatisch nur einzigartige Werte (keine Duplikate)
rounds = set()

for spiel in fixtures:
    runde = spiel["league"]["round"]
    rounds.add(runde)

# Alle gefundenen, einzigartigen Rundennamen ausgeben
for r in sorted(rounds):
    print(r)
