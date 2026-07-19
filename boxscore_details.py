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

    away_batting = []

    away_players = boxscore_json["teams"]["away"]["players"]

    batters = []

    for player in away_players.values():

        batting_order = player.get("battingOrder")

        if batting_order is None:
            continue

        batters.append(player)

    batters.sort(key=lambda p: int(p["battingOrder"]))

    for player in batters:

        batting = player["stats"]["batting"]
        season = player["seasonStats"]["batting"]

        away_batting.append({

            "order": int(player["battingOrder"]),

            "name": player["person"]["boxscoreName"],
            "position": player["position"]["abbreviation"],

            "ab": batting["atBats"],
            "r": batting["runs"],
            "h": batting["hits"],
            "rbi": batting["rbi"],
            "bb": batting["baseOnBalls"],
            "k": batting["strikeOuts"],

            "avg": season["avg"]

        })

    away = linescore["teams"]["away"]
    home = linescore["teams"]["home"]

    print("AWAY:")
    print(json.dumps(away, indent=2))

    print("HOME:")
    print(json.dumps(home, indent=2))

    away_city = game["away_name"].replace(f" {nickname(game['away_name'])}", "")
    away_nickname = nickname(game["away_name"])

    home_city = game["home_name"].replace(f" {nickname(game['home_name'])}", "")
    home_nickname = nickname(game["home_name"])

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
            f"{away_nickname} {away['runs']}, "
            f"{home_nickname} {home['runs']}",

        "boxscore": boxscore,

        # Keep this for later—we'll start filling it in next.
        "away_batting": away_batting,

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
