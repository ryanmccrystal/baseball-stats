import json
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

leaders = statsapi.get(
    "stats_leaders",
    {
        "leaderCategories": "battingAverage",
        "season": SEASON,
        "statGroup": "hitting",
        "limit": 20
    }
)

print(json.dumps(leaders, indent=2))
