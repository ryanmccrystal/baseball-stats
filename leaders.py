import json
from collections import Counter
from datetime import datetime

import statsapi

SEASON = datetime.now().year

TEAM_ABBR = {
    108: "LAA",
    109: "ARI",
    110: "BAL",
    111: "BOS",
    112: "CHC",
    113: "CIN",
    114: "CLE",
    115: "COL",
    116: "DET",
    117: "HOU",
    118: "KCR",
    119: "LAD",
    120: "WSH",
    121: "NYM",
    133: "ATH",
    134: "PIT",
    135: "SDP",
    136: "SEA",
    137: "SFG",
    138: "STL",
    139: "TBR",
    140: "TEX",
    141: "TOR",
    142: "MIN",
    143: "PHI",
    144: "ATL",
    145: "CHW",
    146: "MIA",
    147: "NYY",
    158: "MIL"
}

def get_hitting_stats():

    data = statsapi.get(
        "stats",
        {
            "stats": "season",
            "group": "hitting",
            "season": SEASON,
            "sportIds": 1,
            "playerPool": "ALL",
            "limit": 500
        }
    )

    return data["stats"][0]["splits"]

hitters = get_hitting_stats()

def build_last_name_counts(players):

    counts = {}

    for p in players:

        team = p["team"]["id"]
        last = p["player"]["lastName"]
        first = p["player"]["firstName"]

        counts.setdefault(team, {})
        counts[team].setdefault(last, set())
        counts[team][last].add(first)

    return counts

def top12(players, stat):

    return sorted(
        players,
        key=lambda p: (
            float(p["stat"][stat])
            if stat == "avg"
            else int(p["stat"][stat])
        ),
        reverse=True
    )[:12]

def display_name(player):

    last = player["player"]["lastName"]
    first = player["player"]["firstName"]
    team = player["team"]["id"]

    if len(LAST_NAME_COUNTS[team][last]) > 1:
        return first[0] + last

    return last

def format_text_leaderboard(players, stat_key):

    leaders = top12(players, stat_key)

    results = []

    for p in leaders:

        results.append({
            "player": display_name(p),
            "team": TEAM_ABBR[p["team"]["id"]],
            "value": p["stat"][stat_key]
        })

    return results

LAST_NAME_COUNTS = build_last_name_counts(hitters)

al_hitters = [
    h for h in hitters
    if h["league"]["id"] == 103
]

nl_hitters = [
    h for h in hitters
    if h["league"]["id"] == 104
]


    return results

leaders_json = {
    "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "al": {
        "homeRuns": format_text_leaderboard(al_hitters, "homeRuns")
    }
}

with open("leaders.json", "w") as f:
    json.dump(leaders_json, f, indent=2)

print("Created leaders.json")
