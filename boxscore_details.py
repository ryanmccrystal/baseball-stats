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

    # Existing formatted box score
    boxscore = statsapi.boxscore(gamePk)

    # Direct MLB API box score
    response = requests.get(
        f"https://statsapi.mlb.com/api/v1/game/{gamePk}/boxscore"
    )

    boxscore_json = response.json()

    print("\n========== FIRST BATTER ==========")

    first_player_id = boxscore_json["teams"]["away"]["batters"][0]

    print(first_player_id)

    print(json.dumps(
        boxscore_json["teams"]["away"]["players"][f"ID{first_player_id}"],
        indent=2
    ))

print("==================================\n")

    # Stop after the first game so we don't flood the console.
    break


print("Done.")
