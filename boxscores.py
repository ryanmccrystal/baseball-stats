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
            "k9": f'{float(stats["strikeoutsPer9Inn"]):.1f}',

            "hand":
                "R" if data["pitch_hand"] == "Right"
                else "L"
        }

    except:

        return None

def get_team_record_in_starts(pitcher_name):

    player = statsapi.lookup_player(pitcher_name)

    if not player:
        return "--"

    player_id = player[0]["id"]

    data = statsapi.get(
        "people",
        {
            "personIds": player_id,
            "hydrate": "stats(group=[pitching],type=[gameLog])"
        }
    )

    starts = (
        data["people"][0]
        ["stats"][0]
        ["splits"]
    )

    starts = [
        s for s in starts
        if s["stat"]["gamesStarted"] == 1
    ]

    wins = sum(
        1 for start in starts
        if start["isWin"]
    )

    losses = len(starts) - wins

    return f"{wins}-{losses}"

print(
    "Cantillo starts:",
    get_team_record_in_starts(
        "Joey Cantillo"
    )
)

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

    away_pitcher = (
        game["away_probable_pitcher"]
        if game["away_probable_pitcher"]
        else "TBD"
    )

    home_pitcher = (
        game["home_probable_pitcher"]
        if game["home_probable_pitcher"]
        else "TBD"
    )

    away_stats = get_pitcher_stats(
        away_pitcher
    )

    home_stats = get_pitcher_stats(
        home_pitcher
    )

    if away_stats:
        away_stats["team_record"] = (
            get_team_record_in_starts(
                away_pitcher
            )
        )

    if home_stats:
        home_stats["team_record"] = (
            get_team_record_in_starts(
                home_pitcher
            )
        )

    today_games.append({
        "away_name": nickname(game["away_name"]),
        "home_name": nickname(game["home_name"]),
        "game_time": game["game_datetime"],

        "away_pitcher": away_pitcher,
        "home_pitcher": home_pitcher,

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
    "Joey Cantillo"
)[0]["id"]

gamelog = statsapi.get(
    "people",
    {
        "personIds": player_id,
        "hydrate": "stats(group=[pitching],type=[gameLog])"
    }
)

print(gamelog)

with open("boxscores.json", "w") as f:
    json.dump(boxscores, f, indent=2)
