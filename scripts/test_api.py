"""Prüft, ob der API-Key funktioniert (kostet keine Anfragen aus dem Tageslimit)."""
import requests

from config import BASE_URL, get_headers

# Anfrage an den /status-Endpoint: zeigt Account-Infos und das Tageslimit
response = requests.get(f"{BASE_URL}/status", headers=get_headers(), timeout=30)

# Den Statuscode ausgeben (200 = alles ok)
print("Statuscode:", response.status_code)

# Die Antwort als JSON ausgeben
print(response.json())
