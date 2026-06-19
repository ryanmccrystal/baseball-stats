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

def get_pitcher_stats(name):

    if not name:
        return None

    try:

        player_id = statsapi.lookup_player(
            name
        )[0]["id"]

        data = statsapi.player_stat_data(
            player_id,
            group="[pitching]",
            type="season"
        )

        stats = data["stats"][0]["stats"]

        return {
            "wins": stats["wins"],
            "losses": stats["losses"],
            "era": stats["era"],
            "k9": stats["strikeoutsPer9Inn"]
        }

    except:

        return None

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

    away_stats = get_pitcher_stats(
        game["away_probable_pitcher"]
    )

    home_stats = get_pitcher_stats(
        game["home_probable_pitcher"]
    )

    today_games.append({
        "away_name": nickname(game["away_name"]),
        "home_name": nickname(game["home_name"]),
        "game_time": game["game_datetime"],

        "away_pitcher":
            game["away_probable_pitcher"],

        "home_pitcher":
            game["home_probable_pitcher"],

        "away_stats": away_stats,
        "home_stats": home_stats
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

player_id = statsapi.lookup_player(
    "Kevin Gausman"
)[0]["id"]

print(
    statsapi.player_stat_data(
        player_id,
        group="[pitching]",
        type="season"
    )
)

with open("boxscores.json", "w") as f:
    json.dump(boxscores, f, indent=2)
