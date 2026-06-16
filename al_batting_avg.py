import statsapi
import json
from datetime import datetime, timezone

AL_TEAMS = {
    "BAL", "BOS", "NYY", "TBR", "TOR",
    "CLE", "CWS", "DET", "KCR", "MIN",
    "HOU", "LAA", "ATH", "SEA", "TEX"
}

NL_TEAMS = {
    "ATL", "MIA", "NYM", "PHI", "WSH",
    "CHC", "CIN", "MIL", "PIT", "STL",
    "ARI", "COL", "LAD", "SDP", "SFG"
}

DIVISION_NAMES = {
    201: "AL East",
    202: "AL Central",
    200: "AL West",
    204: "NL East",
    205: "NL Central",
    203: "NL West"
}

teams = statsapi.get("teams", {"sportId": 1})["teams"]
team_lookup = {team["name"]: team["abbreviation"] for team in teams}

team_lookup.update({
    "Arizona Diamondbacks": "ARI",
    "San Francisco Giants": "SFG",
    "San Diego Padres": "SDP",
    "Kansas City Royals": "KCR",
    "Tampa Bay Rays": "TBR"
})


def get_leaders(category, league_teams, top_n=10):
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

        if team_abbr not in league_teams:
            continue

        results.append({
            "name": player["person"]["fullName"],
            "team": team_abbr,
            "value": player["value"]
        })

    return results[:top_n]

def get_pitching_leaders(category, league_teams, top_n=10):

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

        if team_abbr not in league_teams:
            continue

        results.append({
            "name": player["person"]["fullName"],
            "team": team_abbr,
            "value": player["value"]
        })

    return results[:top_n]

def get_xbh_leaders(league_teams, top_n=10):

    doubles = get_leaders("doubles", league_teams, 100)
    triples = get_leaders("triples", league_teams, 100)
    homers = get_leaders("homeRuns", league_teams, 100)

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

def get_standings():

    standings = statsapi.get(
        "standings",
        {
            "leagueId": "103,104"
        }
    )

    results = {}

    for division in standings["records"]:

        division_id = division["division"]["id"]
        division_name = DIVISION_NAMES[division_id]

        teams = []

        for team in division["teamRecords"]:

            print(team["team"])

            break

            teams.append({
                "team": team["team"]["abbreviation"],
                "wins": team["wins"],
                "losses": team["losses"],
                "gb": team["gamesBack"]
            })

        results[division_name] = teams

    return results

leaderboards = {
    "last_updated":
        datetime.now(timezone.utc)
        .strftime("%B %d, %Y %H:%M UTC"),
     "standings": get_standings(),

    "al": {

        "hitting": {
            "batting_avg": get_leaders("battingAverage", AL_TEAMS),
            "home_runs": get_leaders("homeRuns", AL_TEAMS),
            "rbi": get_leaders("runsBattedIn", AL_TEAMS),
            "stolen_bases": get_leaders("stolenBases", AL_TEAMS),
            "obp": get_leaders("onBasePercentage", AL_TEAMS),
            "slg": get_leaders("sluggingPercentage", AL_TEAMS),
            "ops": get_leaders("ops", AL_TEAMS),
            "runs": get_leaders("runs", AL_TEAMS),
            "hits": get_leaders("hits", AL_TEAMS),
            "doubles": get_leaders("doubles", AL_TEAMS),
            "triples": get_leaders("triples", AL_TEAMS),
            "xbh": get_xbh_leaders(AL_TEAMS)
        },

        "pitching": {
            "era": get_pitching_leaders("earnedRunAverage", AL_TEAMS),
            "wins": get_pitching_leaders("wins", AL_TEAMS),
            "strikeouts": get_pitching_leaders("strikeOuts", AL_TEAMS),
            "whip": get_pitching_leaders("whip", AL_TEAMS),
            "innings": get_pitching_leaders("inningsPitched", AL_TEAMS),
            "home_runs_allowed": get_pitching_leaders("homeRuns", AL_TEAMS),
            "saves": get_pitching_leaders("saves", AL_TEAMS),
            "holds": get_pitching_leaders("holds", AL_TEAMS)
        }
    },

    "nl": {

        "hitting": {
            "batting_avg": get_leaders("battingAverage", NL_TEAMS),
            "home_runs": get_leaders("homeRuns", NL_TEAMS),
            "rbi": get_leaders("runsBattedIn", NL_TEAMS),
            "stolen_bases": get_leaders("stolenBases", NL_TEAMS),
            "obp": get_leaders("onBasePercentage", NL_TEAMS),
            "slg": get_leaders("sluggingPercentage", NL_TEAMS),
            "ops": get_leaders("ops", NL_TEAMS),
            "runs": get_leaders("runs", NL_TEAMS),
            "hits": get_leaders("hits", NL_TEAMS),
            "doubles": get_leaders("doubles", NL_TEAMS),
            "triples": get_leaders("triples", NL_TEAMS),
            "xbh": get_xbh_leaders(NL_TEAMS)
        },

        "pitching": {
            "era": get_pitching_leaders("earnedRunAverage", NL_TEAMS),
            "wins": get_pitching_leaders("wins", NL_TEAMS),
            "strikeouts": get_pitching_leaders("strikeOuts", NL_TEAMS),
            "whip": get_pitching_leaders("whip", NL_TEAMS),
            "innings": get_pitching_leaders("inningsPitched", NL_TEAMS),
            "home_runs_allowed": get_pitching_leaders("homeRuns", NL_TEAMS),
            "saves": get_pitching_leaders("saves", NL_TEAMS),
            "holds": get_pitching_leaders("holds", NL_TEAMS)
        }
    }
}

with open("leaderboards.json", "w") as f:
    json.dump(leaderboards, f, indent=2)
