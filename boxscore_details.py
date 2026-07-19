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

def nickname(team_name):

    names = {
        "Arizona Diamondbacks": "DBacks",
        "Atlanta Braves": "Braves",
        "Baltimore Orioles": "Orioles",
        "Boston Red Sox": "Red Sox",
        "Chicago Cubs": "Cubs",
        "Chicago White Sox": "White Sox",
        "Cincinnati Reds": "Reds",
        "Cleveland Guardians": "Guardians",
        "Colorado Rockies": "Rockies",
        "Detroit Tigers": "Tigers",
        "Houston Astros": "Astros",
        "Kansas City Royals": "Royals",
        "Los Angeles Angels": "Angels",
        "Los Angeles Dodgers": "Dodgers",
        "Miami Marlins": "Marlins",
        "Milwaukee Brewers": "Brewers",
        "Minnesota Twins": "Twins",
        "New York Mets": "Mets",
        "New York Yankees": "Yankees",
        "Athletics": "Athletics",
        "Philadelphia Phillies": "Phillies",
        "Pittsburgh Pirates": "Pirates",
        "San Diego Padres": "Padres",
        "San Francisco Giants": "Giants",
        "Seattle Mariners": "Mariners",
        "St. Louis Cardinals": "Cardinals",
        "Tampa Bay Rays": "Rays",
        "Texas Rangers": "Rangers",
        "Toronto Blue Jays": "Blue Jays",
        "Washington Nationals": "Nationals"
    }

    return names.get(team_name, team_name)

def split_team_name(full_name):
    parts = full_name.split()
    city = " ".join(parts[:-1])
    nickname = parts[-1]
    return city, nickname


for game in schedule:

    print(game["away_name"], "at", game["home_name"])
    print("Status:", game["status"])
    print()

    print(f"\n{game['away_name']} at {game['home_name']}")

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

    if "runs" not in away or "runs" not in home:
        print("Skipping game - no runs available")
        print("Away:", away)
        print("Home:", home)
        continue

    away_runs = away["runs"]
    home_runs = home["runs"]
    
    output["games"].append({

        "headline":
            f"{away_nickname} {away_runs}, "
            f"{home_nickname} {home_runs}",

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
