import json
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo

import statsapi

SEASON = datetime.now().year

TEAM_ABBR = {
    108: "Laa",
    109: "Ari",
    110: "Bal",
    111: "Bos",
    112: "Chc",
    113: "Cin",
    114: "Cle",
    115: "Col",
    116: "Det",
    117: "Hou",
    118: "Kan",
    119: "Lad",
    120: "Wsh",
    121: "Nym",
    133: "Ath",
    134: "Pit",
    135: "Sdp",
    136: "Sea",
    137: "Sfg",
    138: "Stl",
    139: "Tbr",
    140: "Tex",
    141: "Tor",
    142: "Min",
    143: "Phi",
    144: "Atl",
    145: "Chw",
    146: "Mia",
    147: "Nyy",
    158: "Mil"
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
            "limit": 999
        }
    )

    return data["stats"][0]["splits"]

def get_pitching_stats():

    data = statsapi.get(
        "stats",
        {
            "stats": "season",
            "group": "pitching",
            "season": SEASON,
            "sportIds": 1,
            "playerPool": "ALL",
            "limit": 999
        }
    )

    return data["stats"][0]["splits"]

def get_team_games():

    standings = statsapi.get(
        "standings",
        {
            "leagueId": "103,104",
            "season": SEASON,
            "standingsTypes": "regularSeason"
        }
    )

    games = {}

    for record in standings["records"]:
        for team in record["teamRecords"]:
            games[team["team"]["id"]] = team["gamesPlayed"]

    return games

hitters = get_hitting_stats()

pitchers = get_pitching_stats()

TEAM_GAMES = get_team_games()

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

    if stat == "era":

        qualified = [
            p for p in players
            if (
                p["stat"]["era"] != "-.--"
                and float(p["stat"]["inningsPitched"]) >= TEAM_GAMES[p["team"]["id"]]
            )
        ]

        return sorted(
            qualified,
            key=lambda p: float(p["stat"]["era"])
        )[:12]

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

def format_batting_average_table(players):

    leaders = top12(players, "avg")

    results = []

    for p in leaders:

        results.append({
            "player": display_name(p),
            "team": TEAM_ABBR[p["team"]["id"]],
            "games": p["stat"]["gamesPlayed"],
            "ab": p["stat"]["atBats"],
            "runs": p["stat"]["runs"],
            "hits": p["stat"]["hits"],
            "avg": p["stat"]["avg"]
        })

    return results

LAST_NAME_COUNTS = build_last_name_counts(
    hitters + pitchers
)

al_hitters = [
    h for h in hitters
    if h["league"]["id"] == 103
]

nl_hitters = [
    h for h in hitters
    if h["league"]["id"] == 104
]

al_pitchers = [
    p for p in pitchers
    if p["league"]["id"] == 103
]

nl_pitchers = [
    p for p in pitchers
    if p["league"]["id"] == 104
]

qualified_al_hitters = [
    h for h in al_hitters
    if h["stat"]["plateAppearances"] >= TEAM_GAMES[h["team"]["id"]] * 3.1
]

qualified_nl_hitters = [
    h for h in nl_hitters
    if h["stat"]["plateAppearances"] >= TEAM_GAMES[h["team"]["id"]] * 3.1
]

leaders_json = {
    "last_updated": datetime.now(
        ZoneInfo("America/New_York")
    ).strftime("%Y-%m-%d %I:%M %p %Z"),

    "al": {
        "battingAverage": format_batting_average_table(qualified_al_hitters),
        "homeRuns": format_text_leaderboard(al_hitters, "homeRuns"),
        "rbi": format_text_leaderboard(al_hitters, "rbi"),
        "hits": format_text_leaderboard(al_hitters, "hits"),
        "runs": format_text_leaderboard(al_hitters, "runs"),
        "stolenBases": format_text_leaderboard(al_hitters, "stolenBases"),

        "era": format_text_leaderboard(al_pitchers, "era"),
        "wins": format_text_leaderboard(al_pitchers, "wins"),
        "strikeOuts": format_text_leaderboard(al_pitchers, "strikeOuts"),
        "saves": format_text_leaderboard(al_pitchers, "saves"),
        "holds": format_text_leaderboard(al_pitchers, "holds"),
    },

    "nl": {
        "battingAverage": format_batting_average_table(qualified_nl_hitters),
        "homeRuns": format_text_leaderboard(nl_hitters, "homeRuns"),
        "rbi": format_text_leaderboard(nl_hitters, "rbi"),
        "hits": format_text_leaderboard(nl_hitters, "hits"),
        "runs": format_text_leaderboard(nl_hitters, "runs"),
        "stolenBases": format_text_leaderboard(nl_hitters, "stolenBases"),

        "era": format_text_leaderboard(nl_pitchers, "era"),
        "wins": format_text_leaderboard(nl_pitchers, "wins"),
        "strikeOuts": format_text_leaderboard(nl_pitchers, "strikeOuts"),
        "saves": format_text_leaderboard(nl_pitchers, "saves"),
        "holds": format_text_leaderboard(nl_pitchers, "holds"),
    }
}

with open("leaders.json", "w") as f:
    json.dump(leaders_json, f, indent=2)

print("Created leaders.json")
