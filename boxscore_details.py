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

for game in schedule:

    gamePk = game["game_id"]

    linescore = statsapi.get(
        "game_linescore",
        {
            "gamePk": gamePk
        }
    )

    away = linescore["teams"]["away"]
    home = linescore["teams"]["home"]

    away_innings = []
    home_innings = []

    for inning in linescore["innings"]:
        away_innings.append(inning["away"]["runs"])
        home_innings.append(inning["home"]["runs"])

    output["games"].append({

        "headline": f'{game["away_name"].upper()} {away["runs"]}, '
                f'{game["home_name"].upper()} {home["runs"]}',

        "away": {
            "city": game["away_name"],
            "nickname": game["away_team"],
            "innings": away_innings,
            "runs": away["runs"],
            "hits": away["hits"],
            "errors": away["errors"]
        },

        "home": {
            "city": game["home_name"],
            "nickname": game["home_team"],
            "innings": home_innings,
            "runs": home["runs"],
            "hits": home["hits"],
            "errors": home["errors"]
        }

    })

print("Writing JSON...")

with open("boxscore_details.json", "w") as f:
    json.dump(output, f, indent=2)
