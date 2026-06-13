import statsapi
import json

AL_TEAMS = {
    "BAL", "BOS", "NYY", "TB", "TOR",
    "CLE", "CWS", "DET", "KC", "MIN",
    "HOU", "LAA", "ATH", "SEA", "TEX"
}

teams = statsapi.get("teams", {"sportId": 1})["teams"]
team_lookup = {team["name"]: team["abbreviation"] for team in teams}

leaders = statsapi.get(
    "stats_leaders",
    {
        "leaderCategories": "battingAverage",
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
        "avg": player["value"]
    })

results = results[:10]

with open("al_batting_avg.json", "w") as f:
    json.dump(results, f, indent=2)
