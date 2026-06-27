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

print(standings)
