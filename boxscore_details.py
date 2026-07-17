import json
from datetime import datetime, timedelta

import requests
import statsapi

yesterday = datetime.now() - timedelta(days=1)

schedule = statsapi.schedule(
    start_date=yesterday.strftime("%m/%d/%Y"),
    end_date=yesterday.strftime("%m/%d/%Y")
)

print("Schedule retrieved")

output = {
    "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
    "games": []
}


def split_team_name(full_name):
    parts = full_name.split()
    city = " ".join(parts[:-1])
    nickname = parts[-1]
    return city, nickname


for game in schedule:

    gamePk = game["game_id"]

    linescore = statsapi.get(
        "game_linescore",
        {
            "gamePk": gamePk
        }
    )

    # Formatted box score text
    boxscore = statsapi.boxscore(gamePk)

    # Structured MLB box score JSON (we'll use this next)
    response = requests.get(
        f"https://statsapi.mlb.com/api/v1/game/{gamePk}/boxscore"
    )

    boxscore_json = response.json()

    away = linescore["teams"]["away"]
    home = linescore["teams"]["home"]

    away_city, away_nickname = split_team_name(game["away_name"])
    home_city, home_nickname = split_team_name(game["home_name"])

    away_innings = []
    home_innings = []

    for inning in linescore["innings"]:

        away_innings.append(
            inning.get("away", {}).get("runs", 0)
        )

        home_innings.append(
            inning.get("home", {}).get("runs", 0)
        )

    output["games"].append({

        "headline":
            f"{away_nickname.upper()} {away['runs']}, "
            f"{home_nickname.upper()} {home['runs']}",

        "boxscore": boxscore,

        # Keep this for later—we'll start filling it in next.
        "boxscore_json": boxscore_json,

        "away": {
            "city": away_city,
            "nickname": away_nickname,
            "innings": away_innings,
            "runs": away["runs"],
            "hits": away["hits"],
            "errors": away["errors"]
        },

        "home": {
            "city": home_city,
            "nickname": home_nickname,
            "innings": home_innings,
            "runs": home["runs"],
            "hits": home["hits"],
            "errors": home["errors"]
        }

    })

print("Writing JSON...")

with open("boxscore_details.json", "w") as f:
    json.dump(output, f, indent=2)

print("Done.")
