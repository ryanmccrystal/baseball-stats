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

    output["games"].append({
        "gamePk": gamePk,
        "linescore": linescore
    })

print("Writing JSON...")

with open("boxscore_details.json", "w") as f:
    json.dump(output, f, indent=2)
