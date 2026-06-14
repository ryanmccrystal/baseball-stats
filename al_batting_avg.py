import statsapi
import json

AL_TEAMS = {
    "BAL", "BOS", "NYY", "TB", "TOR",
    "CLE", "CWS", "DET", "KC", "MIN",
    "HOU", "LAA", "ATH", "SEA", "TEX"
}

teams = statsapi.get("teams", {"sportId": 1})["teams"]
team_lookup = {team["name"]: team["abbreviation"] for team in teams}


def get_leaders(category, top_n=10):
    leaders = statsapi.get(
        "stats_leaders",
        {
            "leaderCategories": category,
            "statGroup": "hitting",
            "leaderGameTypes": "R",
            "limit": 100
        }
    )

    results = []

    for player in leaders["leagueLeaders"][0]["leaders"]:

        team_name = player["team"]["name"]
        team_abbr = team_lookup.get(team_name, team_name)

        if team_abbr not in AL_TEAMS:
            continue

        results.append({
            "name": player["person"]["fullName"],
            "team": team_abbr,
            "value": player["value"]
        })

    return results[:top_n]

def get_pitching_leaders(category, top_n=10):

    leaders = statsapi.get(
        "stats_leaders",
        {
            "leaderCategories": category,
            "statGroup": "pitching",
            "leaderGameTypes": "R",
            "limit": 100
        }
    )

    results = []

    for player in leaders["leagueLeaders"][0]["leaders"]:

        team_name = player["team"]["name"]
        team_abbr = team_lookup.get(team_name, team_name)

        if team_abbr not in AL_TEAMS:
            continue

        results.append({
            "name": player["person"]["fullName"],
            "team": team_abbr,
            "value": player["value"]
        })

    return results[:top_n]

def get_xbh_leaders(top_n=10):

    doubles = get_leaders("doubles", 100)
    triples = get_leaders("triples", 100)
    homers = get_leaders("homeRuns", 100)

    players = {}

    for leaderboard in [doubles, triples, homers]:

        for player in leaderboard:

            key = player["name"]

            if key not in players:
                players[key] = {
                    "name": player["name"],
                    "team": player["team"],
                    "xbh": 0
                }

            players[key]["xbh"] += int(player["value"])

    results = list(players.values())

    results.sort(
        key=lambda x: x["xbh"],
        reverse=True
    )

    return [
        {
            "name": p["name"],
            "team": p["team"],
            "value": str(p["xbh"])
        }
        for p in results[:top_n]
    ]

leaderboards = {
    "hitting": {
        "batting_avg": get_leaders("battingAverage"),
        "home_runs": get_leaders("homeRuns"),
        "rbi": get_leaders("runsBattedIn"),
        "stolen_bases": get_leaders("stolenBases"),
        "obp": get_leaders("onBasePercentage"),
        "slg": get_leaders("sluggingPercentage"),
        "ops": get_leaders("ops"),
        "runs": get_leaders("runs"),
        "hits": get_leaders("hits"),
        "doubles": get_leaders("doubles"),
        "triples": get_leaders("triples"),
        "xbh": get_xbh_leaders()
    },

   "pitching": {
    "era": get_pitching_leaders("earnedRunAverage"),
    "wins": get_pitching_leaders("wins"),
    "strikeouts": get_pitching_leaders("strikeOuts"),
    "whip": get_pitching_leaders("whip"),
    "innings": get_pitching_leaders("inningsPitched"),
    "saves": get_pitching_leaders("saves")
}

with open("leaderboards.json", "w") as f:
    json.dump(leaderboards, f, indent=2)
