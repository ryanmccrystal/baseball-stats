import os
import zipfile
import requests
import pandas as pd
import csv

def load_chadwick_register():

    dfs = []

    for letter in "0123456789abcdef":

        url = (
            "https://raw.githubusercontent.com/"
            "chadwickbureau/register/master/"
            f"data/people-{letter}.csv"
        )

        print(f"Loading people-{letter}.csv")

        dfs.append(
            pd.read_csv(url, low_memory=False)
        )

    return pd.concat(
        dfs,
        ignore_index=True
    )

print("\nLoading Chadwick Register...\n")

register = load_chadwick_register()

canonical_name = {}

for _, row in register.iterrows():

    retro_id = row["key_retro"]

    if pd.isna(retro_id):
        continue

    canonical_name[retro_id] = (
        f"{row['name_first']} "
        f"{row['name_last']}"
    )

DATA_DIR = "data"

os.makedirs(DATA_DIR, exist_ok=True)

event_files = []

for year in range(1910, 2026):

    zip_file = os.path.join(
        DATA_DIR,
        f"{year}eve.zip"
    )

    year_dir = os.path.join(
        DATA_DIR,
        str(year)
    )

    if not os.path.exists(zip_file):

        print(f"Downloading {year}...")

        url = (
            f"https://www.retrosheet.org/"
            f"events/{year}eve.zip"
        )

        r = requests.get(url)

        if r.status_code != 200:
            print(f"Skipping {year}")
            continue

        with open(zip_file, "wb") as f:
            f.write(r.content)

    os.makedirs(year_dir, exist_ok=True)

    with zipfile.ZipFile(zip_file, "r") as z:
        z.extractall(year_dir)

    for file in os.listdir(year_dir):

        if (
            file.endswith(".EVA")
            or file.endswith(".EVN")
        ):

            event_files.append(
                os.path.join(
                    year_dir,
                    file
                )
            )

print(
    f"Found {len(event_files)} event files"
)

MIN_STREAK = 5

all_pa = []

for event_file in event_files:

    current_date = None
    current_game_id = None
    visteam = None
    hometeam = None

    with open(event_file, encoding="latin-1") as f:

        for raw_line in f:

            line = raw_line.strip()

            if line.startswith("id,"):
                current_game_id = line.split(",")[1]
                continue

            if line.startswith("info,date,"):
                current_date = line.split(",")[2]
                continue

            if line.startswith("info,visteam,"):
                visteam = line.split(",")[2]
                continue

            if line.startswith("info,hometeam,"):
                hometeam = line.split(",")[2]
                continue

            if not line.startswith("play,"):
                continue

            fields = line.split(",")

            batting_team = fields[2]
            batter_id = fields[3]
            event = fields[6]

            team_abbr = (
                visteam
                if batting_team == "0"
                else hometeam
            )

            if team_abbr != "CLE":
                continue

            all_pa.append({
                "date": current_date,
                "game_id": current_game_id,
                "batter_id": batter_id,
                "event": event
            })

print(
    f"\nCollected {len(all_pa)} Cleveland plate appearances"
)

all_pa.sort(
    key=lambda x: (
        x["date"],
        x["game_id"]
    )
)

print("\nBartolo after sorting:\n")

for pa in all_pa:

    if pa["batter_id"] == "colob001":

        print(
            pa["date"],
            pa["event"]
        )

results = []

active_streaks = {}
start_date = {}
start_game = {}

for pa in all_pa:

    batter_id = pa["batter_id"]
    event = pa["event"]

    # No Play does not affect streaks
    if event == "NP":
        continue

    if event.startswith("K"):

        if batter_id not in active_streaks:

            active_streaks[batter_id] = 1

            start_date[batter_id] = pa["date"]

            start_game[batter_id] = pa["game_id"]

        else:

            active_streaks[batter_id] += 1

    else:

        if (
            batter_id in active_streaks
            and active_streaks[batter_id] >= MIN_STREAK
        ):

            results.append({
                "player": canonical_name.get(
                    batter_id,
                    batter_id
                ),
                "streak": active_streaks[batter_id],
                "start_date": start_date[batter_id],
                "end_date": pa["date"],
                "start_game": start_game[batter_id],
                "end_game": pa["game_id"]
            })

        active_streaks.pop(
            batter_id,
            None
        )

        start_date.pop(
            batter_id,
            None
        )

        start_game.pop(
            batter_id,
            None
        )

for batter_id, streak in active_streaks.items():

    if streak >= MIN_STREAK:

        results.append({
            "player": canonical_name.get(
                batter_id,
                batter_id
            ),
            "streak": streak,
            "start_date": start_date[batter_id],
            "end_date": start_date[batter_id],
            "start_game": start_game[batter_id],
            "end_game": start_game[batter_id]
        })

results.sort(
    key=lambda x: x["streak"],
    reverse=True
)

print("\nTop Strikeout Streaks:\n")

for row in results[:50]:

    print(
        f"{row['player']} | "
        f"{row['streak']} | "
        f"{row['start_date']} -> "
        f"{row['end_date']}"
    )
