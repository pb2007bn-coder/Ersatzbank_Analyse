import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Design-Stil setzen
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 11})

# Daten einlesen
csv_path = "../data/processed/events_clean.csv"
df = pd.read_csv(csv_path)

output_dir = "../reports/figures"
os.makedirs(output_dir, exist_ok=True)

# Datensätze trennen
df_subst = df[df['event_type'] == 'subst'].copy()
df_goals = df[df['event_type'] == 'Goal'].copy()

print("==================================================")
print("     DEUTLICH ERWEITERTE ERSATZBANK-ANALYSE       ")
print("==================================================\n")

# ----------------------------------------------------
# 1. BASIS-METRIKEN & DURCHSCHNITTE
# ----------------------------------------------------
total_subst = len(df_subst)
avg_minute = df_subst['minute'].mean()
median_minute = df_subst['minute'].median()

print("--- 1. ZEITPUNKTE DER EINWECHSLUNGEN ---")
print(f"Gesamtzahl Einwechslungen:      {total_subst}")
print(f"Durchschnittliche Minute:       {avg_minute:.1f}. Minute")
print(f"Median-Einwechselminute:        {median_minute:.0f}. Minute")

# Phasen-Aufteilung
early_subs = len(df_subst[df_subst['minute'] < 45])
half_time_subs = len(df_subst[df_subst['minute'] == 45])
late_subs = len(df_subst[(df_subst['minute'] > 45) & (df_subst['minute'] <= 75)])
clutch_subs = len(df_subst[df_subst['minute'] > 75])

print(f"\nPhasen-Aufteilung der Wechsel:")
print(f"  • Erste Halbzeit (<45. Min):  {early_subs} ({early_subs/total_subst*100:.1f}%)")
print(f"  • Halbzeitpause (45. Min):    {half_time_subs} ({half_time_subs/total_subst*100:.1f}%)")
print(f"  • Phase 2 (46.-75. Min):       {late_subs} ({late_subs/total_subst*100:.1f}%)")
print(f"  • Schlussphase (>75. Min):     {clutch_subs} ({clutch_subs/total_subst*100:.1f}%)\n")

# ----------------------------------------------------
# 2. JOKER-TORE (Eingewechselte Spieler)
# ----------------------------------------------------
# Eingewechselte Spieler identifizieren
subbed_in_players = set(df_subst['assist_or_in'].dropna().unique())

# Prüfen, welche Torschützen vorher eingewechselt wurden
joker_goals = df_goals[df_goals['player_name'].isin(subbed_in_players)]

print("--- 2. JOKER-TORE ANALYSE ---")
print(f"Gesamtzahl Tore in K.o.-Phase:  {len(df_goals)}")
print(f"Tore durch Joker (Ersatzbank):  {len(joker_goals)} ({len(joker_goals)/len(df_goals)*100:.1f}% aller Tore)")

if len(joker_goals) > 0:
    print("\nDie Torschützen von der Ersatzbank:")
    for idx, row in joker_goals.iterrows():
        print(f"  • {row['player_name']} ({row['team_name']}) in Minute {row['minute']}")

# ----------------------------------------------------
# 3. GRAFIK 1: Detail-Verteilung der Wechselminuten
# ----------------------------------------------------
plt.figure(figsize=(10, 5))
sns.histplot(df_subst['minute'], bins=18, kde=True, color='#1f77b4')
plt.title("Auswechsel-Zeitpunkte in der UCL K.o.-Phase", fontsize=14, fontweight='bold')
plt.xlabel("Spielminute")
plt.ylabel("Anzahl Einwechslungen")
plt.axvline(avg_minute, color='red', linestyle='--', label=f'Durchschnitt ({avg_minute:.1f}. Min)')
plt.axvline(45, color='grey', linestyle=':', label='Halbzeit (45. Min)')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "wechsel_zeitpunkte.png"), dpi=300)
plt.close()

# ----------------------------------------------------
# 4. GRAFIK 2: Wechsel-Aktivität pro Team (Ranking)
# ----------------------------------------------------
team_subs = df_subst['team_name'].value_counts().head(10)

plt.figure(figsize=(10, 5))
sns.barplot(x=team_subs.values, y=team_subs.index, palette="Blues_r")
plt.title("Top 10 Teams mit den meisten Einwechslungen", fontsize=14, fontweight='bold')
plt.xlabel("Anzahl Einwechslungen")
plt.ylabel("Team")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "top_teams_wechsel.png"), dpi=300)
plt.close()

print("\nAnalyse abgeschlossen! Neue Grafiken in 'reports/figures/' gespeichert.")