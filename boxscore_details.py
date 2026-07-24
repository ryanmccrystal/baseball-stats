import json
from datetime import datetime, timedelta

import requests
import statsapi

yesterday = datetime.now() - timedelta(days=1)

schedule = statsapi.schedule(
    start_date=yesterday.strftime("%m/%d/%Y"),
    end_date=yesterday.strftime("%m/%d/%Y")
)

print("Schedule retrieved")

output = {
    "last_updated": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
    "games": []
}

FINAL_STATUSES = {
    "Final",
    "Game Over",
    "Completed Early"
}

def nickname(team_name):

    names = {
        "Arizona Diamondbacks": "DBacks",
        "Atlanta Braves": "Braves",
        "Baltimore Orioles": "Orioles",
        "Boston Red Sox": "Red Sox",
        "Chicago Cubs": "Cubs",
        "Chicago White Sox": "White Sox",
        "Cincinnati Reds": "Reds",
        "Cleveland Guardians": "Guardians",
        "Colorado Rockies": "Rockies",
        "Detroit Tigers": "Tigers",
        "Houston Astros": "Astros",
        "Kansas City Royals": "Royals",
        "Los Angeles Angels": "Angels",
        "Los Angeles Dodgers": "Dodgers",
        "Miami Marlins": "Marlins",
        "Milwaukee Brewers": "Brewers",
        "Minnesota Twins": "Twins",
        "New York Mets": "Mets",
        "New York Yankees": "Yankees",
        "Athletics": "Athletics",
        "Philadelphia Phillies": "Phillies",
        "Pittsburgh Pirates": "Pirates",
        "San Diego Padres": "Padres",
        "San Francisco Giants": "Giants",
        "Seattle Mariners": "Mariners",
        "St. Louis Cardinals": "Cardinals",
        "Tampa Bay Rays": "Rays",
        "Texas Rangers": "Rangers",
        "Toronto Blue Jays": "Blue Jays",
        "Washington Nationals": "Nationals"
    }

    return names.get(team_name, team_name)

def split_team_name(full_name):

    special_cases = {
        "Boston Red Sox": ("Boston", "Red Sox"),
        "Chicago White Sox": ("Chicago", "White Sox"),
        "Toronto Blue Jays": ("Toronto", "Blue Jays")
    }

    if full_name in special_cases:
        return special_cases[full_name]

    parts = full_name.split()

    city = " ".join(parts[:-1])
    nickname = parts[-1]

    return city, nickname

def extract_boxscore_note(boxscore, label):

    for line in boxscore.splitlines():

        line = line.strip()

        if line.startswith(f"{label}:"):

            note = line[len(label) + 1:].strip().rstrip(".")

            if label == "Umpires":
                note = (
                    note.replace("HP:", "HP")
                        .replace("1B:", "1B")
                        .replace("2B:", "2B")
                        .replace("3B:", "3B")
                )

            return note

    return ""

for game in schedule:

    if game["status"] not in FINAL_STATUSES:

        away_city, away_nickname = split_team_name(game["away_name"])
        home_city, home_nickname = split_team_name(game["home_name"])

        status_map = {
            "Postponed": "ppd",
            "Cancelled": "canc"
        }

        display_status = status_map.get(
            game["status"],
            game["status"].lower()
        )

        output["games"].append({
            "status": game["status"],

            "games_display":
                f"{game['away_name']} at {game['home_name']} - {display_status}",

            "away": {
                "city": away_city,
                "nickname": away_nickname
            },

            "home": {
                "city": home_city,
                "nickname": home_nickname
            }
        })

        continue

    gamePk = game["game_id"]

    print(game["away_name"], "at", game["home_name"])
    print("Status:", game["status"])
    print()

    print(f"\n{game['away_name']} at {game['home_name']}")

    gamePk = game["game_id"]

    linescore = statsapi.get(
        "game_linescore",
        {
            "gamePk": gamePk
        }
    )

    # Structured MLB box score JSON (we'll use this next)
    response = requests.get(
        f"https://statsapi.mlb.com/api/v1/game/{gamePk}/boxscore"
    )

    boxscore_json = response.json()

    feed_response = requests.get(
        f"https://statsapi.mlb.com/api/v1.1/game/{gamePk}/feed/live"
    )
    
    feed_json = feed_response.json()
    
    notes = {
        "errors": [],
        "lob": None,
        "doubles": [],
        "triples": [],
        "home_runs": [],
        "stolen_bases": [],
        "caught_stealing": [],
        "gidp": [],
        "sac_hits": [],
        "sac_flies": []
    }

    game_info = {
        "wild_pitches": "",
        "intentional_walks": "",
        "hit_by_pitch": "",
        "umpires": "",
        "time": "",
        "attendance": ""
    }

    # Formatted box score text
    boxscore = statsapi.boxscore(gamePk)
    game_info["wild_pitches"] = extract_boxscore_note(boxscore, "WP")
    game_info["intentional_walks"] = extract_boxscore_note(boxscore, "IBB")
    game_info["hit_by_pitch"] = extract_boxscore_note(boxscore, "HBP")
    game_info["umpires"] = extract_boxscore_note(boxscore, "Umpires")

    game_data = feed_json["gameData"]

    game_info["time"] = game_data.get("gameInfo", {}).get("gameDurationMinutes")
    
    game_info["attendance"] = game_data.get("gameInfo", {}).get("attendance")

    # Format game time (minutes → H:MM)
    if game_info["time"]:
    
        minutes = int(game_info["time"])
    
        hours = minutes // 60
        mins = minutes % 60
    
        game_info["time"] = f"{hours}:{mins:02d}"
    
    # Format attendance with commas
    if game_info["attendance"]:
    
        game_info["attendance"] = f"{int(game_info['attendance']):,}"

    away_batting = []

    away_players = boxscore_json["teams"]["away"]["players"]

    batters = []

    for player in away_players.values():

        batting_order = player.get("battingOrder")

        if batting_order is None:
            continue

        batters.append(player)

    batters.sort(key=lambda p: int(p["battingOrder"]))

    for player in batters:

        batting = player["stats"]["batting"]
        season = player["seasonStats"]["batting"]

        away_batting.append({

            "order": int(player["battingOrder"]),

            "name": player["person"]["boxscoreName"],
            "position": player["position"]["abbreviation"],

            "ab": batting["atBats"],
            "r": batting["runs"],
            "h": batting["hits"],
            "rbi": batting["rbi"],
            "bb": batting["baseOnBalls"],
            "k": batting["strikeOuts"],

            "avg": season["avg"]

        })

    home_batting = []

    home_players = boxscore_json["teams"]["home"]["players"]

    batters = []

    for player in home_players.values():

        batting_order = player.get("battingOrder")

        if batting_order is None:
            continue

        batters.append(player)

    batters.sort(key=lambda p: int(p["battingOrder"]))

    for player in batters:

        batting = player["stats"]["batting"]
        season = player["seasonStats"]["batting"]

        home_batting.append({

            "order": int(player["battingOrder"]),

            "name": player["person"]["boxscoreName"],
            "position": player["position"]["abbreviation"],

            "ab": batting["atBats"],
            "r": batting["runs"],
            "h": batting["hits"],
            "rbi": batting["rbi"],
            "bb": batting["baseOnBalls"],
            "k": batting["strikeOuts"],

            "avg": season["avg"]

        })

    # -----------------------------
    # Build game notes
    # -----------------------------
    
    for side in ["away", "home"]:
    
        team = boxscore_json["teams"][side]
    
        team_name = nickname(team["team"]["name"])
    
        # Team LOB
        lob = team["teamStats"]["batting"].get("leftOnBase", 0)
    
        if notes["lob"] is None:
            notes["lob"] = {}
    
        notes["lob"][team_name] = lob
    
        for player in team["players"].values():
    
            stats = player.get("stats", {}).get("batting", {})
            season = player.get("seasonStats", {}).get("batting", {})

            fielding = player.get("stats", {}).get("fielding", {})
            season_fielding = player.get("seasonStats", {}).get("fielding", {})

            name = player["person"]["boxscoreName"]
    
            # Errors
            if fielding.get("errors", 0):
                notes["errors"].append(
                    f"{name} ({season_fielding.get('errors', fielding['errors'])})"
                )
    
            # Doubles
            if stats.get("doubles", 0):
                notes["doubles"].append(
                    f"{name} ({season['doubles']})"
                )
    
            # Triples
            if stats.get("triples", 0):
                notes["triples"].append(
                    f"{name} ({season['triples']})"
                )
    
            # Home Runs
            if stats.get("homeRuns", 0):
                notes["home_runs"].append(
                    f"{name} ({season['homeRuns']})"
                )
    
            # Stolen Bases
            if stats.get("stolenBases", 0):
                notes["stolen_bases"].append(
                    f"{name} ({season['stolenBases']})"
                )
    
            # Caught Stealing
            if stats.get("caughtStealing", 0):
    
                notes["caught_stealing"].append(
                    f"{name} ({season.get('caughtStealing', stats['caughtStealing'])})"
                )
    
            # GIDP
            if stats.get("groundIntoDoublePlay", 0):
                notes["gidp"].append(name)
    
            # Sacrifice Hits
            if stats.get("sacBunts", 0):
                notes["sac_hits"].append(name)
    
            # Sacrifice Flies
            if stats.get("sacFlies", 0):
                notes["sac_flies"].append(name)

    away = linescore["teams"]["away"]
    home = linescore["teams"]["home"]

    away_city, away_nickname = split_team_name(game["away_name"])
    home_city, home_nickname = split_team_name(game["home_name"])

    away_innings = []
    home_innings = []

    for inning in linescore["innings"]:

        away_innings.append(
            inning.get("away", {}).get("runs", 0)
        )

        home_innings.append(
            inning.get("home", {}).get("runs", 0)
        )

    if "runs" not in away or "runs" not in home:
        print("Skipping game - no runs available")
        print("Away:", away)
        print("Home:", home)
        continue

    away_runs = away["runs"]
    home_runs = home["runs"]
    
    if away_runs > home_runs:
        games_display = f"{away_nickname} {away_runs}, {home_nickname} {home_runs}"
    else:
        games_display = f"{home_nickname} {home_runs}, {away_nickname} {away_runs}"
    
    if game["status"] == "Completed Early":
        games_display += f" (F/{len(away_innings)})"
    
    elif game["status"] == "Suspended":
        games_display += " - susp"

    # -----------------------------
    # Away pitching
    # -----------------------------
    
    away_pitching = []
    
    away_pitchers = boxscore_json["teams"]["away"]["players"]
    
    pitchers = []

    for player in away_pitchers.values():
    
        if player.get("position", {}).get("abbreviation") != "P":
            continue
    
        pitching = player.get("stats", {}).get("pitching", {})
    
        if pitching.get("inningsPitched"):
    
            pitchers.append(player)
    
    pitchers.sort(key=lambda p: int(p["stats"]["pitching"]["battersFaced"]), reverse=True)
    
    for player in pitchers:
    
        pitching = player["stats"]["pitching"]
        season = player["seasonStats"]["pitching"]
    
        away_pitching.append({
    
            "name": player["person"]["boxscoreName"],
    
            "ip": pitching["inningsPitched"],
            "h": pitching["hits"],
            "r": pitching["runs"],
            "er": pitching["earnedRuns"],
            "bb": pitching["baseOnBalls"],
            "k": pitching["strikeOuts"],
            "np": pitching["numberOfPitches"],
    
            "era": season.get("era", "---")
    
        })
    
    # -----------------------------
    # Home pitching
    # -----------------------------
    
    home_pitching = []
    
    home_pitchers = boxscore_json["teams"]["home"]["players"]
    
    pitchers = []

    for player in home_pitchers.values():
    
        if player.get("position", {}).get("abbreviation") != "P":
            continue
    
        pitching = player.get("stats", {}).get("pitching", {})
    
        if pitching.get("inningsPitched"):
    
            pitchers.append(player)
    
    pitchers.sort(key=lambda p: int(p["stats"]["pitching"]["battersFaced"]), reverse=True)
    
    for player in pitchers:
    
        pitching = player["stats"]["pitching"]
        season = player["seasonStats"]["pitching"]
    
        home_pitching.append({
    
            "name": player["person"]["boxscoreName"],
    
            "ip": pitching["inningsPitched"],
            "h": pitching["hits"],
            "r": pitching["runs"],
            "er": pitching["earnedRuns"],
            "bb": pitching["baseOnBalls"],
            "k": pitching["strikeOuts"],
            "np": pitching["numberOfPitches"],
    
            "era": season.get("era", "---")
    
        })

    output["games"].append({

        "status": game["status"],

        "games_display": games_display,

        "headline": games_display,

        "boxscore": boxscore,

        # Keep this for later—we'll start filling it in next.
        "away_batting": away_batting,
        "home_batting": home_batting,
        "away_pitching": away_pitching,
        "home_pitching": home_pitching,

        "away": {
            "city": away_city,
            "nickname": away_nickname,
            "innings": away_innings,
            "runs": away["runs"],
            "hits": away["hits"],
            "errors": away["errors"]
        },

        "home": {
            "city": home_city,
            "nickname": home_nickname,
            "innings": home_innings,
            "runs": home["runs"],
            "hits": home["hits"],
            "errors": home["errors"]
        },

        "notes": notes,
        "game_info": game_info
        

    })

print("Writing JSON...")

with open("boxscore_details.json", "w") as f:
    json.dump(output, f, indent=2)

print("Done.")
