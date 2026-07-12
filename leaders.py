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

def build_last_name_counts():

    counts = {}

    teams = statsapi.get(
        "teams",
        {"sportIds": 1}
    )["teams"]

    for team in teams:

        roster = statsapi.get(
            "team_roster",
            {
                "teamId": team["id"],
                "rosterType": "active"
            }
        )["roster"]

        counter = Counter()

        for player in roster:
            last = player["person"]["fullName"].split()[-1]
            counter[last] += 1

        counts[team["id"]] = counter

    return counts

LAST_NAME_COUNTS = build_last_name_counts()

def get_hitting_stats():

    data = statsapi.get(
        "stats",
        {
            "stats": "season",
            "group": "hitting",
            "season": SEASON,
            "sportIds": 1,
            "playerPool": "QUALIFIED",
            "limit": 500
        }
    )

    return data["stats"][0]["splits"]


hitters = get_hitting_stats()

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

    if LAST_NAME_COUNTS[team][last] == 1:
        return last

    return first[0] + last

al_hitters = [
    h for h in hitters
    if h["league"]["id"] == 103
]

nl_hitters = [
    h for h in hitters
    if h["league"]["id"] == 104
]

leaders = top12(al_hitters, "homeRuns")

for p in leaders:

    print(
        display_name(p),
        TEAM_ABBR[p["team"]["id"]],
        p["stat"]["homeRuns"]
    )
