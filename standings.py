import json
import statsapi

standings = statsapi.get(
    "standings",
    {
        "leagueId": "103,104",
        "season": 2026,
        "standingsTypes": "regularSeason"
    }
)

with open("standings.json", "w") as f:
    json.dump(standings, f, indent=2)

print("Created standings.json")
