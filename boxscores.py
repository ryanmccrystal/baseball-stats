import statsapi
import json
from datetime import date, timedelta

yesterday = date.today() - timedelta(days=1)

schedule = statsapi.schedule(
    start_date=yesterday.strftime("%m/%d/%Y"),
    end_date=yesterday.strftime("%m/%d/%Y")
)

games = []

for game in schedule:

    games.append({
        "gamePk": game["game_id"],

        "away": game["away_id"],
        "away_name": game["away_name"],
        "away_score": game["away_score"],

        "home": game["home_id"],
        "home_name": game["home_name"],
        "home_score": game["home_score"]
    })

boxscores = {
    "games": games
}

with open("boxscores.json", "w") as f:
    json.dump(boxscores, f, indent=2)

print(f"Created boxscores.json with {len(games)} games")
