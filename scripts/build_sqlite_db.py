import sqlite3
import pandas as pd
import os

# Pfade definieren
csv_path = "../data/processed/events_clean.csv"
db_path = "../database/ucl_analysis.db"

os.makedirs("../database", exist_ok=True)

# 1. Verbindung zur SQLite-Datenbank herstellen (wird automatisch erstellt)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== ERSTELLE SQLITE DATENBANK & TABELLEN ===")

# 2. Tabellen mit explizitem DDL (CREATE TABLE) anlegen
cursor.execute("DROP TABLE IF EXISTS events")

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fixture_id TEXT NOT NULL,
    minute INTEGER,
    extra_minute INTEGER,
    team_name TEXT NOT NULL,
    player_name TEXT,
    assist_or_in TEXT,
    event_type TEXT NOT NULL,
    detail TEXT
);
""")

print("-> Tabelle 'events' mit CREATE TABLE erfolgreich angelegt.")

# 3. CSV-Daten einlesen und in die SQL-Tabelle einfügen
df = pd.read_csv(csv_path)

# Daten über pandas / sql in die erstelle Tabelle schreiben
df.to_sql("events", conn, if_exists="append", index=False)
print(f"-> {len(df)} Zeilen erfolgreich per INSERT in SQLite importiert.")

# ----------------------------------------------------
# 4. SQL QUERIES (Abfragen) AUSFÜHREN
# ----------------------------------------------------
print("\n=== SQL QUERY AUSWERTUNGEN ===")

# Query 1: Durchschnittliche Wechselminute & Anzahl Wechsel
query_subs = """
SELECT 
    COUNT(*) AS anzahl_wechsel,
    ROUND(AVG(minute), 1) AS avg_wechsel_minute,
    MIN(minute) AS fruehester_wechsel,
    MAX(minute) AS spaetester_wechsel
FROM events
WHERE event_type = 'subst';
"""
result_subs = pd.read_sql_query(query_subs, conn)
print("\n1. SQL-Abfrage: Wechsel-Statistiken:")
print(result_subs.to_string(index=False))

# Query 2: Top 5 Teams nach Anzahl der Tore per SQL GROUP BY
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
result_teams = pd.read_sql_query(query_teams, conn)
print("\n2. SQL-Abfrage: Top 5 Teams nach Toren (GROUP BY & ORDER BY):")
print(result_teams.to_string(index=False))

# Query 3: Joker-Tore via SQL JOIN / Subquery ermitteln
query_joker = """
SELECT 
    g.player_name,
    g.team_name,
    g.minute AS tor_minute
FROM events g
WHERE g.event_type = 'Goal'
  AND g.player_name IN (
      SELECT DISTINCT assist_or_in 
      FROM events 
      WHERE event_type = 'subst'
  )
ORDER BY g.minute DESC;
"""
result_joker = pd.read_sql_query(query_joker, conn)
print(f"\n3. SQL-Abfrage: Joker-Torschützen ({len(result_joker)} Tore gefunden):")
print(result_joker.head(5).to_string(index=False))

# Verbindung schließen
conn.close()
print("\nDatenbank-Erstellung & SQL-Queries erfolgreich abgeschlossen!")