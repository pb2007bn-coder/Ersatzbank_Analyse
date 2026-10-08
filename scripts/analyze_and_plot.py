"""Schritt 6: Auswertung mit Pandas und zwei Diagramme mit Matplotlib."""
import matplotlib

matplotlib.use("Agg")  # Diagramme nur als Datei speichern, kein Fenster öffnen
import matplotlib.pyplot as plt
import pandas as pd

from config import EVENTS_CSV, FIGURES_DIR, FIXTURES_CSV

# Farben für die Diagramme
BLAU = "#2a78d6"
TEXT = "#0b0b0b"
TEXT_GRAU = "#52514e"
ACHSE = "#c3c2b7"
GITTER = "#e1e0d9"
HINTERGRUND = "#fcfcfb"

plt.rcParams.update({
    "font.size": 11,
    "text.color": TEXT,
    "axes.labelcolor": TEXT_GRAU,
    "xtick.color": TEXT_GRAU,
    "ytick.color": TEXT_GRAU,
    "axes.edgecolor": ACHSE,
    "figure.facecolor": HINTERGRUND,
    "axes.facecolor": HINTERGRUND,
    "savefig.facecolor": HINTERGRUND,
})

# Daten einlesen
df = pd.read_csv(EVENTS_CSV)
df_fixtures = pd.read_csv(FIXTURES_CSV)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Nur Spiele, für die Event-Daten vorliegen
df_spiele = df_fixtures[df_fixtures["has_events"] == 1]
anzahl_spiele = len(df_spiele)

# Datensätze trennen
df_subst = df[df["event_type"] == "subst"].copy()
df_goals = df[df["event_type"] == "Goal"].copy()

print("==================================================")
print("             ERSATZBANK-ANALYSE                   ")
print("==================================================\n")
print(f"Ausgewertete Spiele: {anzahl_spiele} von {len(df_fixtures)} K.-o.-Spielen")
fehlend = df_fixtures[df_fixtures["has_events"] == 0]
for _, row in fehlend.iterrows():
    print(f"  Fehlt: {row['round']}, {row['home_team']} - {row['away_team']}")

# ----------------------------------------------------
# 1. ZEITPUNKTE DER EINWECHSLUNGEN
# ----------------------------------------------------
total_subst = len(df_subst)
avg_minute = df_subst["minute"].mean()
median_minute = df_subst["minute"].median()

print("\n--- 1. ZEITPUNKTE DER EINWECHSLUNGEN ---")
print(f"Gesamtzahl Einwechslungen:      {total_subst}")
print(f"Durchschnittliche Minute:       {avg_minute:.1f}. Minute")
print(f"Median-Einwechselminute:        {median_minute:.0f}. Minute")

# Phasen-Aufteilung. Die API führt Wechsel in der Halbzeitpause als Minute 46.
phasen = {
    "Erste Halbzeit (bis 45. Min)": (df_subst["minute"] <= 45).sum(),
    "Zur Halbzeit (46. Min)": (df_subst["minute"] == 46).sum(),
    "47. bis 75. Min": df_subst["minute"].between(47, 75).sum(),
    "Schlussphase (ab 76. Min)": (df_subst["minute"] >= 76).sum(),
}
print("\nPhasen-Aufteilung der Wechsel:")
for name, anzahl in phasen.items():
    print(f"  • {name:<30} {anzahl:>3} ({anzahl / total_subst * 100:.1f}%)")

# ----------------------------------------------------
# 2. JOKER-TORE
# ----------------------------------------------------
# Ein Joker-Tor ist ein Tor von einem Spieler, der IM SELBEN SPIEL vorher
# eingewechselt wurde. Es reicht nicht, nur die Namen zu vergleichen: Ein Spieler
# kann in einem Spiel Joker sein und im nächsten von Beginn an spielen.

# Hilfsspalte: Zeitpunkt als eine Zahl (Minute 90+3 wird zu 9003)
df_subst["zeit_wechsel"] = df_subst["minute"] * 100 + df_subst["extra_minute"].fillna(0)
df_goals["zeit_tor"] = df_goals["minute"] * 100 + df_goals["extra_minute"].fillna(0)

# Jedes Tor mit dem Wechsel verknüpfen, bei dem der Torschütze reinkam
# (gleiches Spiel, gleiches Team, gleicher Spieler)
einwechslungen = df_subst[["fixture_id", "team_name", "assist_or_in", "minute", "zeit_wechsel"]]
einwechslungen = einwechslungen.rename(
    columns={"assist_or_in": "player_name", "minute": "eingewechselt"}
)
tore_mit_wechsel = df_goals.merge(
    einwechslungen, on=["fixture_id", "team_name", "player_name"], how="inner"
)
joker_goals = tore_mit_wechsel[tore_mit_wechsel["zeit_wechsel"] <= tore_mit_wechsel["zeit_tor"]]

anteil_tore = len(joker_goals) / len(df_goals) * 100

print("\n--- 2. JOKER-TORE ---")
print(f"Gesamtzahl Tore:                {len(df_goals)}")
print(f"Tore durch Joker:               {len(joker_goals)} ({anteil_tore:.1f}% aller Tore)")
print("\nDie Joker-Tore im Einzelnen:")
for _, row in joker_goals.iterrows():
    print(f"  • {row['player_name']} ({row['team_name']}): eingewechselt in Minute "
          f"{row['eingewechselt']}, Tor in Minute {row['minute']}")

# ----------------------------------------------------
# 3. VERGLEICH MIT DER SPIELZEIT (Überschlag)
# ----------------------------------------------------
# 13 % der Tore sagen wenig, solange man nicht weiß, wie lange Joker auf dem
# Platz standen. Überschlag: Jeder Joker spielt von seiner Einwechslung bis
# Minute 90. Nachspielzeit und Platzverweise werden nicht berücksichtigt.
minuten_joker = (90 - df_subst["minute"]).clip(lower=0).sum()
minuten_gesamt = anzahl_spiele * 22 * 90
minuten_startelf = minuten_gesamt - minuten_joker
anteil_spielzeit = minuten_joker / minuten_gesamt * 100

tore_startelf = len(df_goals) - len(joker_goals)
tore_pro_90_joker = len(joker_goals) / minuten_joker * 90
tore_pro_90_startelf = tore_startelf / minuten_startelf * 90

print("\n--- 3. VERGLEICH MIT DER SPIELZEIT (Überschlag) ---")
print(f"Anteil der Joker an der Spielzeit:   {anteil_spielzeit:.1f}%")
print(f"Anteil der Joker an den Toren:       {anteil_tore:.1f}%")
print(f"Tore pro 90 Minuten, Joker:          {tore_pro_90_joker:.2f}")
print(f"Tore pro 90 Minuten, Startelf:       {tore_pro_90_startelf:.2f}")
print(f"Faktor:                              {tore_pro_90_joker / tore_pro_90_startelf:.1f}")

# ----------------------------------------------------
# 4. WECHSEL PRO SPIEL JE TEAM
# ----------------------------------------------------
# Teams, die weiter kommen, haben mehr Spiele. Deshalb pro Spiel rechnen.
spiele_pro_team = pd.concat([df_spiele["home_team"], df_spiele["away_team"]]).value_counts()
wechsel_pro_team = df_subst["team_name"].value_counts()

df_teams = pd.DataFrame({"spiele": spiele_pro_team, "wechsel": wechsel_pro_team}).fillna(0)
df_teams["wechsel_pro_spiel"] = df_teams["wechsel"] / df_teams["spiele"]
df_teams = df_teams.sort_values("wechsel_pro_spiel", ascending=False)

print("\n--- 4. WECHSEL PRO SPIEL JE TEAM ---")
for team, row in df_teams.iterrows():
    print(f"  • {team:<22} {row['wechsel_pro_spiel']:.2f}  "
          f"({row['wechsel']:.0f} Wechsel in {row['spiele']:.0f} Spielen)")

# ----------------------------------------------------
# 5. GRAFIK 1: Verteilung der Wechselminuten
# ----------------------------------------------------
# 5-Minuten-Blöcke: 1-5, 6-10, ..., 86-90 (Nachspielzeit zählt zu Minute 90)
bins = [x + 0.5 for x in range(0, 91, 5)]

fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(df_subst["minute"], bins=bins, color=BLAU, rwidth=0.88, zorder=2)

ax.set_title(f"Wann wird gewechselt? {total_subst} Einwechslungen in {anzahl_spiele} K.-o.-Spielen",
             fontsize=14, fontweight="bold", loc="left", pad=14)
ax.set_xlabel("Spielminute (5-Minuten-Blöcke)")
ax.set_ylabel("Anzahl Einwechslungen")
ax.set_xticks(range(0, 91, 15))
ax.set_xlim(0, 91)
ax.grid(axis="y", color=GITTER, linewidth=1, zorder=1)
ax.set_axisbelow(True)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(length=0)

# Zwei Bezugslinien mit Beschriftung direkt an der Linie
oben = ax.get_ylim()[1]
ax.axvline(45.5, color=ACHSE, linewidth=1, zorder=1)
ax.text(44.5, oben * 0.95, "Halbzeit", ha="right", va="top", color=TEXT_GRAU)
ax.axvline(median_minute, color=TEXT, linewidth=1, zorder=3)
ax.text(median_minute - 1, oben * 0.95, f"Median: {median_minute:.0f}. Minute",
        ha="right", va="top", color=TEXT)

fig.tight_layout()
fig.savefig(FIGURES_DIR / "wechsel_zeitpunkte.png", dpi=300)
plt.close(fig)

# ----------------------------------------------------
# 6. GRAFIK 2: Wechsel pro Spiel je Team
# ----------------------------------------------------
df_plot = df_teams.sort_values("wechsel_pro_spiel")  # größter Wert steht oben
beschriftung = [f"{team} ({spiele:.0f} Spiele)" for team, spiele in df_plot["spiele"].items()]

fig, ax = plt.subplots(figsize=(10, 6.5))
balken = ax.barh(beschriftung, df_plot["wechsel_pro_spiel"], height=0.6, color=BLAU, zorder=2)

ax.set_title("Wechsel pro Spiel je Team",
             fontsize=14, fontweight="bold", loc="left", pad=14)
ax.set_xlabel("Einwechslungen pro Spiel (erlaubt sind 5)")
ax.set_xlim(0, 5.4)
ax.grid(axis="x", color=GITTER, linewidth=1, zorder=1)
ax.set_axisbelow(True)
ax.spines[["top", "right", "bottom"]].set_visible(False)
ax.tick_params(length=0)

# Wert an das Ende jedes Balkens schreiben
for rechteck, wert in zip(balken, df_plot["wechsel_pro_spiel"]):
    ax.text(wert + 0.06, rechteck.get_y() + rechteck.get_height() / 2,
            f"{wert:.1f}".replace(".", ","), va="center", color=TEXT)

fig.tight_layout()
fig.savefig(FIGURES_DIR / "wechsel_pro_spiel.png", dpi=300)
plt.close(fig)

print(f"\nAnalyse abgeschlossen! Grafiken in '{FIGURES_DIR}' gespeichert.")
