import json
from datetime import datetime

import statsapi

from datetime import timedelta

yesterday = datetime.now() - timedelta(days=1)

schedule = statsapi.schedule(
    start_date=yesterday.strftime("%m/%d/%Y"),
    end_date=yesterday.strftime("%m/%d/%Y")
)

print("Schedule retrieved")
print(len(schedule))
print(schedule[0])

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

    boxscore = statsapi.boxscore(gamePk)

    away = linescore["teams"]["away"]
    home = linescore["teams"]["home"]
    away_city, away_nickname = split_team_name(game["away_name"])
    home_city, home_nickname = split_team_name(game["home_name"])

    away_innings = []
    home_innings = []

    for inning in linescore["innings"]:
        away_innings.append(inning["away"]["runs"])
        home_innings.append(inning["home"]["runs"])

    output["games"].append({

        "headline": f'{away_nickname.upper()} {away["runs"]}, '
                    f'{home_nickname.upper()} {home["runs"]}',

        "boxscore": boxscore,

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
