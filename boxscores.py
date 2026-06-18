import statsapi
import json
from datetime import date, timedelta

def nickname(team_name):
    return team_name.split()[-1]

yesterday = date.today() - timedelta(days=1)

schedule = statsapi.schedule(
    start_date=yesterday.strftime("%m/%d/%Y"),
    end_date=yesterday.strftime("%m/%d/%Y")
)

games = []

for game in schedule:

    if game["away_score"] > game["home_score"]:

        winner_name = nickname(game["away_name"])
        winner_score = game["away_score"]

        loser_name = nickname(game["home_name"])
        loser_score = game["home_score"]

    else:

        winner_name = nickname(game["home_name"])
        winner_score = game["home_score"]

        loser_name = nickname(game["away_name"])
        loser_score = game["away_score"]

    games.append({
        "gamePk": game["game_id"],

        "winner_name": winner_name,
        "winner_score": winner_score,

        "loser_name": loser_name,
        "loser_score": loser_score
})

boxscores = {
    "games": games
}

with open("boxscores.json", "w") as f:
    json.dump(boxscores, f, indent=2)

print(f"Created boxscores.json with {len(games)} games")
