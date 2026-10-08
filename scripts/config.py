"""Gemeinsame Einstellungen für alle Skripte: Pfade und API-Zugang."""
import os
from pathlib import Path

# Projektordner = der Ordner über "scripts".
# Dadurch laufen die Skripte, egal aus welchem Ordner man sie startet.
PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "data"
EVENTS_DIR = DATA_DIR / "events"
PROCESSED_DIR = DATA_DIR / "processed"
FIXTURES_RAW = DATA_DIR / "fixtures_raw.json"
FIXTURES_KO = DATA_DIR / "fixtures_ko.json"
EVENTS_CSV = PROCESSED_DIR / "events_clean.csv"
FIXTURES_CSV = PROCESSED_DIR / "fixtures_clean.csv"
DB_PATH = PROJECT_DIR / "database" / "ucl_analysis.db"
FIGURES_DIR = PROJECT_DIR / "reports" / "figures"

BASE_URL = "https://v3.football.api-sports.io"


def get_headers():
    """Liest den API-Key aus der Umgebungsvariable API_FOOTBALL_KEY.

    Der Key steht absichtlich nicht im Code, damit er nicht auf GitHub landet.
    """
    api_key = os.environ.get("API_FOOTBALL_KEY")
    if not api_key:
        raise SystemExit(
            "Kein API-Key gefunden. Bitte die Umgebungsvariable "
            "API_FOOTBALL_KEY setzen (siehe README, Abschnitt 'Ausführen')."
        )
    return {"x-apisports-key": api_key}
