import statsapi
import json
from datetime import date, timedelta

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

games.sort(
    key=lambda g: (
        not (
            g["winner_name"] == "Guardians"
            or
            g["loser_name"] == "Guardians"
        )
    )
)

today = date.today()

today_schedule = statsapi.schedule(
    start_date=today.strftime("%m/%d/%Y"),
    end_date=today.strftime("%m/%d/%Y")
)

today_games = []

for game in today_schedule:

    today_games.append({
    "away_name": nickname(game["away_name"]),
    "home_name": nickname(game["home_name"]),
    "game_time": game["game_datetime"]
})

today_games.sort(
    key=lambda g: (
        not (
            g["away_name"] == "Guardians"
            or
            g["home_name"] == "Guardians"
        ),
        g["game_time"]
    )
)

boxscores = {
    "games": games,
    "today_games": today_games
}



with open("boxscores.json", "w") as f:
    json.dump(boxscores, f, indent=2)

print(f"Created boxscores.json with {len(games)} games")
