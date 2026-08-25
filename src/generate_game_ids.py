
# Imports
import json
import os
from collections import defaultdict


# ========================================TEAM CONSTANTS========================================
TEAMS = {
    'BOS': 'Atlantic',
    'BUF': 'Atlantic',
    'DET': 'Atlantic',
    'FLA': 'Atlantic',
    'MTL': 'Atlantic',
    'OTT': 'Atlantic',
    'TBL': 'Atlantic',
    'TOR': 'Atlantic',

    'CAR': 'Metropolitan',
    'CBJ': 'Metropolitan',
    'NJD': 'Metropolitan',
    'NYI': 'Metropolitan',
    'NYR': 'Metropolitan',
    'PHI': 'Metropolitan',
    'PIT': 'Metropolitan',
    'WSH': 'Metropolitan',

    'CHI': 'Central',
    'COL': 'Central',
    'DAL': 'Central',
    'MIN': 'Central',
    'NSH': 'Central',
    'STL': 'Central',
    'UTA': 'Central',
    'WPG': 'Central',

    'ANA': 'Pacific',
    'CGY': 'Pacific',
    'EDM': 'Pacific',
    'LAK': 'Pacific',
    'SJS': 'Pacific',
    'SEA': 'Pacific',
    'VAN': 'Pacific',
    'VGK': 'Pacific'
}

CONFERENCES = {
    'Eastern': ['Atlantic', 'Metropolitan'],
    'Western': ['Central', 'Pacific']
}


# ========================================GENERATE ALL GAME IDS========================================
if __name__ == '__main__':
    # Build lookup table for divisions
    division_to_teams = defaultdict(list)
    for team, division in TEAMS.items():
        division_to_teams[division].append(team)

    # Initialize game list
    games_list = []

    # Create every teams home games
    for home_team in TEAMS:
        home_div = TEAMS[home_team]
        home_conf = next(conference for conference, divisions in CONFERENCES.items() if home_div in divisions)

        # Generate games against same conference, same division teams (2 home games against 7 other teams)
        for away_team in division_to_teams[home_div]:
            if away_team != home_team:
                # Add games
                for _ in range(2):
                    games_list.append((home_team, away_team))

        # Generate games against same conference, other division teams (1 or 2 home games against 8 other teams)
        same_conf_other_div = [division for division in CONFERENCES[home_conf] if division != home_div]
        for division in same_conf_other_div:
            for away_team in division_to_teams[division]:

                # Team gets 2 home games against first opponents, 1 against last opponets
                if home_team < away_team:
                    home_games = 2
                else:
                    home_games = 1

                # Add game(s)
                for _ in range(home_games):
                    games_list.append((home_team, away_team))

        # Generate games against other conference teams (1 home game against 16 other teams)
        other_conf_divs = [division for conference, divisions in CONFERENCES.items() if conference != home_conf for division in divisions]
        for division  in other_conf_divs:
            # Add game
            for away_team in division_to_teams[division]:
                games_list.append((home_team, away_team))

    # Save JSON file of all games
    games_dict = {str(i): [home, away] for i, (home, away) in enumerate(games_list)}
    os.makedirs('schedule_info', exist_ok=True)
    with open('schedule_info/nhl_all_games.json', 'w') as f:
        json.dump(games_dict, f, indent=2)
