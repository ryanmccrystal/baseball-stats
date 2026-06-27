
# standings.py
#
# Production-ready MLB standings generator.
# Generates standings.json for use by the website.
#
# NOTE:
# This script assumes the `statsapi` package and the MLB Stats API
# endpoint structure discussed in our conversation.

import json
from datetime import datetime
import statsapi


def split_record(split_records, record_type):
    """Return W-L for a split record type (home, away, lastTen, oneRun)."""
    for rec in split_records:
        if rec.get("type") == record_type:
            return f'{rec["wins"]}-{rec["losses"]}'
    return "--"


def fmt_run_diff(value):
    if value is None:
        return "--"
    value = int(value)
    return f"+{value}" if value > 0 else str(value)


TEAM_NAMES = {
    108: ("Los Angeles", "Angels"),
    109: ("Arizona", "Diamondbacks"),
    110: ("Baltimore", "Orioles"),
    111: ("Boston", "Red Sox"),
    112: ("Chicago", "Cubs"),
    113: ("Cincinnati", "Reds"),
    114: ("Cleveland", "Guardians"),
    115: ("Colorado", "Rockies"),
    116: ("Detroit", "Tigers"),
    117: ("Houston", "Astros"),
    118: ("Kansas City", "Royals"),
    119: ("Los Angeles", "Dodgers"),
    120: ("Washington", "Nationals"),
    121: ("New York", "Mets"),
    133: ("Athletics", "Athletics"),
    134: ("Pittsburgh", "Pirates"),
    135: ("San Diego", "Padres"),
    136: ("Seattle", "Mariners"),
    137: ("San Francisco", "Giants"),
    138: ("St. Louis", "Cardinals"),
    139: ("Tampa Bay", "Rays"),
    140: ("Texas", "Rangers"),
    141: ("Toronto", "Blue Jays"),
    142: ("Minnesota", "Twins"),
    143: ("Philadelphia", "Phillies"),
    144: ("Atlanta", "Braves"),
    145: ("Chicago", "White Sox"),
    146: ("Miami", "Marlins"),
    147: ("New York", "Yankees"),
    158: ("Milwaukee", "Brewers"),
}


def city_and_nickname(team_id):
    return TEAM_NAMES[team_id]


raw = statsapi.get(
    "standings",
    {
        "leagueId": "103,104",
        "season": datetime.now().year,
        "standingsTypes": "regularSeason",
    },
)

div_map = {
    201: ("al", "east"),
    202: ("al", "central"),
    200: ("al", "west"),
    204: ("nl", "east"),
    205: ("nl", "central"),
    203: ("nl", "west"),
}

out = {
    "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "al": {"east": [], "central": [], "west": [], "wildcard": []},
    "nl": {"east": [], "central": [], "west": [], "wildcard": []},
}

wc = {"al": [], "nl": []}

for div in raw["records"]:
    div_id = div["division"]["id"]
    if div_id not in div_map:
        continue
    league_key, division_key = div_map[div_id]

    for t in div["teamRecords"]:
        city, nickname = city_and_nickname(t["team"]["id"])
        splits = t["records"]["splitRecords"]

        team = {
            "teamId": t["team"]["id"],
            "city": city,
            "nickname": nickname,
            "wins": t["wins"],
            "losses": t["losses"],
            "pct": t["winningPercentage"],
            "gb": t["gamesBack"],
            "last10": split_record(splits, "lastTen"),
            "streak": t["streak"]["streakCode"],
            "home": split_record(splits, "home"),
            "away": split_record(splits, "away"),
            "oneRun": split_record(splits, "oneRun"),
            "runDiff": fmt_run_diff(t["runDifferential"]),
        }

        out[league_key][division_key].append(team)

        if t["divisionRank"] != "1":
            wc[league_key].append({
                "city": city,
                "wins": t["wins"],
                "losses": t["losses"],
                "pct": t["winningPercentage"],
                "wcgb": t["wildCardGamesBack"],
            })

for lg in ("al", "nl"):
    wc[lg].sort(key=lambda x: (
        x["wcgb"] not in ("-", "+0.0"),
        float(str(x["wcgb"]).replace("+", "").replace("-", "0") or 0)
        if x["wcgb"] not in ("-", "+0.0") else -1
    ))
    out[lg]["wildcard"] = wc[lg]

with open("standings.json", "w") as f:
    json.dump(out, f, indent=2)

print("Created standings.json")
