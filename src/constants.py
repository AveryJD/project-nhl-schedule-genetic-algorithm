
# Imports
import datetime


# ====================GENETIC ALGORITHM HYPERPARAMETERS====================
# Hyperparameters used for a full production run (see schedule_ga.py)
HYPERPARAMETERS = {
    'POPULATION_SIZE': 500, # Must be even (due to crossover)
    'GENERATIONS': 20_000,
    'STAGNANT_GENERATIONS': 1_000,

    'TOURNAMENT_SIZE': 3,
    'CROSSOVER_RATE': 0.40,
    'MUTATION_RATE': 0.40,
    'ELITISM': True,
}

# The frequency of generations to print progress updates
UPDATE_FREQUENCY = 100


# ====================HYPERPARAMETER TESTING CONSTANTS====================
# Baseline hyperparameters held fixed while sweeping one at a time (see hyperparameter_testing.py)
DEFAULT_HYPERPARAMETERS = {
    'POPULATION_SIZE': 50,
    'GENERATIONS': 300,
    'STAGNANT_GENERATIONS': 1000,
    'TOURNAMENT_SIZE': 3,
    'CROSSOVER_RATE': 0.50,
    'MUTATION_RATE': 0.30,
    'ELITISM': True,
}

# The testing hyperparameters and their values to test
TEST_HYPERPARAMETERS = {
    'TOURNAMENT_SIZE':[2, 3, 4, 5],
    'CROSSOVER_RATE': [0.30, 0.40, 0.50, 0.60, 0.70],
    'MUTATION_RATE': [0.10, 0.20, 0.30, 0.40, 0.50, 0.60],
    'ELITISM': [True, False],
}

# Number of runs per hyperparameter value
STATISTICAL_RUNS = 50


# ====================FITNESS WEIGHTS====================
# Fixed weights controlling the trade-off between the soft fitness components (rest/game day balance, home/away balance, travel distance).
FITNESS_WEIGHTS = {
    'REST_WEIGHT': 1.0,
    'HOME_AWAY_WEIGHT': 1.0,
    'TRAVEL_WEIGHT': 0.01,
}


# ====================SEASON DATE CONSTANTS====================
# The start and end date of the schedule
START_DATE = datetime.date(2026, 10, 7)         # October 7, 2026
END_DATE = datetime.date(2027, 4, 16)           # April 16, 2027

# Days that NHL games can not be scheduled on
INVALID_DATES = set()
INVALID_DATES.add(datetime.date(2026, 11, 26))  # American Thanksgiving
INVALID_DATES.add(datetime.date(2026, 12, 24))  # Christmas Eve
INVALID_DATES.add(datetime.date(2026, 12, 25))  # Christmas Day
INVALID_DATES.add(datetime.date(2026, 12, 26))  # Boxing Day

INVALID_DATES.add(datetime.date(2027, 2, 7))    # February bye week
INVALID_DATES.add(datetime.date(2027, 2, 8))
INVALID_DATES.add(datetime.date(2027, 2, 9))
INVALID_DATES.add(datetime.date(2027, 2, 10))
INVALID_DATES.add(datetime.date(2027, 2, 11))
INVALID_DATES.add(datetime.date(2027, 2, 12))
INVALID_DATES.add(datetime.date(2027, 2, 13))


# ====================TEAM CONSTANTS====================
# Maps each team abbreviation to its division
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

# Maps each conference to its divisions
CONFERENCES = {
    'Eastern': ['Atlantic', 'Metropolitan'],
    'Western': ['Central', 'Pacific']
}

# List of all NHL team abbreviations
ALL_TEAMS = ["BOS", "BUF", "DET", "FLA", "MTL", "OTT", "TBL", "TOR",
             "CAR", "CBJ", "NJD", "NYI", "NYR", "PHI", "PIT", "WSH",
             "CHI", "COL", "DAL", "MIN", "NSH", "STL", "UTA", "WPG",
             "ANA", "CGY", "EDM", "LAK", "SJS", "SEA", "VGK", "VAN"]


