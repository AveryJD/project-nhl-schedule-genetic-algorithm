# Imports
import json
from collections import defaultdict


TEAMS = {
    # Eastern Conference
    # Atlantic Division
    "BOS": "Atlantic",
    "BUF": "Atlantic",
    "DET": "Atlantic",
    "FLA": "Atlantic",
    "MTL": "Atlantic",
    "OTT": "Atlantic",
    "TBL": "Atlantic",
    "TOR": "Atlantic",

    # Metropolitan Division
    "CAR": "Metropolitan",
    "CBJ": "Metropolitan",
    "NJD": "Metropolitan",
    "NYI": "Metropolitan",
    "NYR": "Metropolitan",
    "PHI": "Metropolitan",
    "PIT": "Metropolitan",
    "WSH": "Metropolitan",

    # Western Conference
    # Central Division
    "CHI": "Central",
    "COL": "Central",
    "DAL": "Central",
    "MIN": "Central",
    "NSH": "Central",
    "STL": "Central",
    "UTA": "Central",
    "WPG": "Central",

    # Pacific Division
    "ANA": "Pacific",
    "CGY": "Pacific",
    "EDM": "Pacific",
    "LAK": "Pacific",
    "SJS": "Pacific",
    "SEA": "Pacific",
    "VAN": "Pacific",
    "VGK": "Pacific"
}


CONFERENCES = {
    "Eastern": ["Atlantic", "Metropolitan"],
    "Western": ["Central", "Pacific"]
}

# Build lookup tables
division_to_teams = defaultdict(list)
for team, division in TEAMS.items():
    division_to_teams[division].append(team)

# Initialize schedule list
schedule = []


for home_team in TEAMS:
    home_div = TEAMS[home_team]
    home_conf = next(conf for conf, divs in CONFERENCES.items() if home_div in divs)

    # Generate games against same conference, same division teams (3 home games against 7 other teams)
    for away_team in division_to_teams[home_div]:
        if away_team != home_team:
            for _ in range(2):
                schedule.append((home_team, away_team))

    # Generate games against same conference, other division teams (1 or 2 home games against 8 other teams)
    same_conf_other_divs = [d for d in CONFERENCES[home_conf] if d != home_div]
    for d in same_conf_other_divs:
        opponents = division_to_teams[d]
        # assign first 4 teams 2 home games, next 4 teams 1 home game
        for i, away_team in enumerate(opponents):
            home_games = 2 if i < 4 else 1
            for _ in range(home_games):
                schedule.append((home_team, away_team))

    # Generate games against other conference teams (1 home game against 16 other teams)
    other_conf_divs = [d for c, divs in CONFERENCES.items() if c != home_conf for d in divs]
    for d in other_conf_divs:
        for away_team in division_to_teams[d]:
            schedule.append((home_team, away_team))


# Make and save JSON file of all games
schedule_dict = {str(i): [home, away] for i, (home, away) in enumerate(schedule)}

with open("nhl_all_games.json", "w") as f:
    json.dump(schedule_dict, f, indent=2)
