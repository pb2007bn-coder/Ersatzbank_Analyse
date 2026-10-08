"""Schritt 5: SQLite-Datenbank mit zwei Tabellen bauen und per SQL auswerten."""
import sqlite3

import pandas as pd

from config import DB_PATH, EVENTS_CSV, FIXTURES_CSV

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# 1. Verbindung zur SQLite-Datenbank herstellen (Datei wird automatisch erstellt)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== ERSTELLE SQLITE DATENBANK & TABELLEN ===")

# 2. Tabellen mit explizitem DDL (CREATE TABLE) anlegen.
#    Erst löschen, damit das Skript beliebig oft laufen kann.
cursor.execute("DROP TABLE IF EXISTS events")
cursor.execute("DROP TABLE IF EXISTS fixtures")

cursor.execute("""
CREATE TABLE fixtures (
    fixture_id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    round TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    home_goals INTEGER,
    away_goals INTEGER,
    has_events INTEGER NOT NULL          -- 1 = Event-Daten vorhanden, 0 = fehlen
);
""")

cursor.execute("""
CREATE TABLE events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id INTEGER NOT NULL REFERENCES fixtures(fixture_id),
    minute INTEGER,
    extra_minute INTEGER,                -- Nachspielzeit, sonst NULL
    team_name TEXT NOT NULL,
    player_name TEXT,                    -- Tor: Schütze / Wechsel: geht raus
    assist_or_in TEXT,                   -- Tor: Vorlage / Wechsel: kommt rein
    event_type TEXT NOT NULL,            -- 'Goal' oder 'subst'
    detail TEXT
);
""")
print("-> Tabellen 'fixtures' und 'events' angelegt.")

# 3. CSV-Daten einlesen und in die SQL-Tabellen einfügen
df_fixtures = pd.read_csv(FIXTURES_CSV)
df_events = pd.read_csv(EVENTS_CSV)

df_fixtures.to_sql("fixtures", conn, if_exists="append", index=False)
df_events.to_sql("events", conn, if_exists="append", index=False)
print(f"-> {len(df_fixtures)} Spiele und {len(df_events)} Events importiert.")

# ----------------------------------------------------
# 4. SQL-ABFRAGEN
# ----------------------------------------------------
print("\n=== SQL QUERY AUSWERTUNGEN ===")

# Query 1: Kennzahlen zu den Wechseln (Aggregatfunktionen)
query_subs = """
SELECT
    COUNT(*) AS anzahl_wechsel,
    ROUND(AVG(minute), 1) AS avg_wechsel_minute,
    MIN(minute) AS fruehester_wechsel,
    MAX(minute) AS spaetester_wechsel
FROM events
WHERE event_type = 'subst';
"""
print("\n1. Wechsel-Statistik:")
print(pd.read_sql_query(query_subs, conn).to_string(index=False))

# Query 2: Top 5 Teams nach Toren (GROUP BY & ORDER BY)
query_teams = """
SELECT
    team_name,
    COUNT(*) AS tore_gesamt
FROM events
WHERE event_type = 'Goal'
GROUP BY team_name
ORDER BY tore_gesamt DESC
LIMIT 5;
"""
print("\n2. Top 5 Teams nach Toren:")
print(pd.read_sql_query(query_teams, conn).to_string(index=False))

# Query 3: Joker-Tore (Self-Join der Tabelle events)
# Ein Joker-Tor ist ein Tor von einem Spieler, der IM SELBEN SPIEL vorher
# eingewechselt wurde. Deshalb wird jedes Tor (g) mit den Wechseln (s) desselben
# Spiels und Teams verknüpft, bei denen der Torschütze der reinkommende Spieler ist.
query_joker = """
SELECT
    f.round AS runde,
    f.home_team || ' - ' || f.away_team AS spiel,
    g.player_name AS torschuetze,
    g.team_name AS team,
    s.minute AS eingewechselt,
    g.minute AS tor_minute
FROM events g
JOIN events s
  ON  s.fixture_id   = g.fixture_id
  AND s.team_name    = g.team_name
  AND s.assist_or_in = g.player_name
  AND s.event_type   = 'subst'
JOIN fixtures f
  ON f.fixture_id = g.fixture_id
WHERE g.event_type = 'Goal'
  AND s.minute * 100 + COALESCE(s.extra_minute, 0)
      <= g.minute * 100 + COALESCE(g.extra_minute, 0)
ORDER BY f.date, g.minute;
"""
result_joker = pd.read_sql_query(query_joker, conn)
print(f"\n3. Joker-Tore ({len(result_joker)} gefunden):")
print(result_joker.to_string(index=False))

# Query 4: Wechsel pro Spiel je Team (Unterabfrage mit UNION ALL + JOIN)
# Teams, die weiter kommen, haben mehr Spiele. Für einen fairen Vergleich wird
# die Zahl der Wechsel deshalb durch die Zahl der ausgewerteten Spiele geteilt.
query_per_game = """
SELECT
    sp.team_name,
    sp.spiele,
    COUNT(e.event_id) AS wechsel,
    ROUND(1.0 * COUNT(e.event_id) / sp.spiele, 2) AS wechsel_pro_spiel
FROM (
    SELECT team_name, COUNT(*) AS spiele
    FROM (
        SELECT home_team AS team_name FROM fixtures WHERE has_events = 1
        UNION ALL
        SELECT away_team AS team_name FROM fixtures WHERE has_events = 1
    )
    GROUP BY team_name
) sp
LEFT JOIN events e
  ON e.team_name = sp.team_name AND e.event_type = 'subst'
GROUP BY sp.team_name, sp.spiele
ORDER BY wechsel_pro_spiel DESC;
"""
print("\n4. Wechsel pro Spiel je Team:")
print(pd.read_sql_query(query_per_game, conn).to_string(index=False))

# Änderungen speichern und Verbindung schließen
conn.commit()
conn.close()
print("\nDatenbank-Erstellung & SQL-Queries erfolgreich abgeschlossen!")
