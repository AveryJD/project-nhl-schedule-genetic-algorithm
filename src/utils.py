
# Imports
import math
import random
import json
import datetime
from collections import defaultdict


# ====================LOAD SCHEDULE INFORMATION====================
games_json = open('schedule_info/nhl_all_games.json')
ALL_GAMES = json.load(games_json)

locations_json = open('schedule_info/arena_locations.json')
ARENA_LOCATIONS = json.load(locations_json)


# ====================DATE CONSTANTS====================
# Set the start and end date of the schedule
START_DATE = datetime.date(2026, 10, 7)         # October 7, 2026
END_DATE = datetime.date(2027, 4, 16)           # April 16, 2027

# Set days that NHL games can not be scheduled on
INVALID_DATES = set()
INVALID_DATES.add(datetime.date(2026, 11, 26))  # American Thanksgiving
INVALID_DATES.add(datetime.date(2026, 12, 24))  # Christmas Eve
INVALID_DATES.add(datetime.date(2026, 12, 25))  # Christmas Day
INVALID_DATES.add(datetime.date(2026, 12, 26))  # Boxing Day

INVALID_DATES.add( datetime.date(2027, 2, 7))   # February bye week
INVALID_DATES.add( datetime.date(2027, 2, 8))
INVALID_DATES.add( datetime.date(2027, 2, 9))
INVALID_DATES.add( datetime.date(2027, 2, 10))
INVALID_DATES.add( datetime.date(2027, 2, 11))
INVALID_DATES.add( datetime.date(2027, 2, 12))
INVALID_DATES.add( datetime.date(2027, 2, 13))


# ====================FITNESS_WEIGHTS====================
FITNESS_WEIGHTS = {
    'GAME_REST_WEIGHT': 0.40,
    'HOME_AWAY_WEIGHT': 0.50,
    'TRAVEL_WEIGHT': 0.10
}


# ====================DISTANCE FUNCTIONS====================
def calc_distance(current_location: tuple[float, float], traveling_location: tuple[float, float]) -> float:
    """
    Calculate the distance between two latitude and longitude coordinates using the Haversine formula.

    :param current_location: (latitude, longitude) tuple for the first location
    :param traveling_location: (latitude, longitude) tuple for the second location
    :return distance: the distance between the coordinates (in kilometers)
    """

    # Unwrap the latitude and longitude coords
    lat_one, lon_one = current_location
    lat_two, lon_two = traveling_location

    # Earth's radius (in km)
    radius = 6371 

    # Calculate the distance with the Haversine formula
    lat_distance = math.radians(lat_two - lat_one)
    lon_distance = math.radians(lon_two - lon_one)
    a = (math.sin(lat_distance / 2) ** 2 +
         math.cos(math.radians(lat_one)) *
         math.cos(math.radians(lat_two)) *
         math.sin(lon_distance / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c

    return distance


def make_distance_matrix(arena_locations: dict = ARENA_LOCATIONS) -> list[list[float]]:
    """
    Create a matrix of distances between all team arenas.

    :param arena_locations: dictionay mapping team abbreviations to latitude and longitude coordinates
    :return distance_matrix: a list of lists where distance_matrix[i][j] is the distance between team i and team j in kilometers
    """

    #  Get a list of all the teams
    all_teams = list(arena_locations.keys())
    # Initialize the distance matrix
    distance_matrix = []

    for team_one in all_teams:
        # For each team get their latitude and longitude coordinates and initialize a list for distances from the team
        team_one_location = (arena_locations[team_one]["lat"], arena_locations[team_one]["lon"])
        team_one_distances = []
        for team_two in all_teams:
            # For each team get their latitude and longitude coordinates
            team_two_location = (arena_locations[team_two]["lat"], arena_locations[team_two]["lon"])
            # Calculate the distance between the two teams and add it to team one's distance list
            distance = calc_distance(team_one_location, team_two_location)
            team_one_distances.append(distance)
        # Add team one's distance list to the matrix
        distance_matrix.append(team_one_distances)

    return distance_matrix


# ====================FITNESS FUNCTIONS====================
def team_schedule_fitness(team_schedule: list[tuple[str, str]], distance_matrix: list[list[float]], team_index: int, team_list: list[str], fitness_weights: dict = FITNESS_WEIGHTS) -> float:
    """
    Calculates a fitness score for a single team's schedule.
    Penalties related to rest/game day balance, home/away balance, and travel distance are added and then each component is weighted.
    A lower score indicates a better schedule.

    :param team_schedule: a list of tuples, where each tuple is (home_team, away_team, game_date) representing the games played by this specific team
    :param distance_matrix: a matrix containing the travel distance between all NHL arenas
    :param team_index: the index of the current team in the `team_list` (used to locate its city in the distance matrix)
    :param team_list: a list of all NHL team abbreviations
    :param fitness_weights: a dictionary containing the weight factors for each fitness component
    :return fitness: a float representing the total weighted fitness score for the team.
    """

    # Unpack weight parameters
    game_rest_weight = fitness_weights['GAME_REST_WEIGHT']
    home_away_weight = fitness_weights['HOME_AWAY_WEIGHT']
    travel_weight = fitness_weights['TRAVEL_WEIGHT']


    # Optimizing rest time
    game_rest_fitness = 0
    for i in range(len(team_schedule) - 1):
        current_day = team_schedule[i][2]
        next_day = team_schedule[i + 1][2]
        day_gap = (next_day - current_day).days - 1

        # Apply penalties based on how many rest days are between games
        if day_gap == 0:
            game_rest_fitness += 1
        elif day_gap == 1:
            game_rest_fitness +=  0
        elif day_gap == 2:
            game_rest_fitness += 1
        elif day_gap == 3:
            game_rest_fitness += 3
        elif day_gap >= 4:
            game_rest_fitness += 10

    # Penalize when games are played three days in a row
    for i in range(len(team_schedule) - 2):
        day_one, day_two, day_three = team_schedule[i][2], team_schedule[i+1][2], team_schedule[i+2][2]
        # If three consecutive games only have day gaps of one, it means back-to-back-to-back is occuring
        if (day_two - day_one).days == 1 and (day_three - day_two).days == 1:
            game_rest_fitness += 10_000


    # Optimizing home/away streak balance
    home_away_fitness = 0
    # Start with a streak of 1 for the first game
    streak = 1
    # Determine if the first game is a home game for the team
    last_home = team_schedule[0][0] == team_list[team_index]
    for i in range(1, len(team_schedule)):
        current_home = team_schedule[i][0] == team_list[team_index]
        # If the home/away status didn't change, increment the streak number
        if current_home == last_home:
            streak += 1
        # If the home/away status did change, check the streak we just ended
        else:
            # Apply penalties based on how long the streaks are
            if streak == 1:
                home_away_fitness += 5
            elif 2 <= streak <= 3:
                home_away_fitness += 2
            elif 4 <= streak <= 5:
                home_away_fitness += 1
            elif 6 <= streak <= 7:
                home_away_fitness += 5
            else:
                home_away_fitness += 10

            streak = 1
            last_home = current_home


    # Minimizing travel distance
    travel_fitness = 0
    for game_one_index in range(len(team_schedule) - 1):
            
        # Determine location 1 (the home city of the current game)
        current_game_home_team = team_schedule[game_one_index][0]
        if current_game_home_team == team_list[team_index]:
            location_one = team_index
        else:
            location_one = team_list.index(current_game_home_team)

        # Find the next game entry
        game_two_index = game_one_index + 1
        while game_two_index < len(team_schedule) and not team_schedule[game_two_index]:
            game_two_index += 1
            
        # If the end of the schedule is reached, break
        if game_two_index >= len(team_schedule):
            break
            
        # Determine location 2 (the home city of the next game)
        next_game_home_team = team_schedule[game_two_index][0]
        if next_game_home_team == team_list[team_index]:
            location_two = team_index
        else:
            location_two = team_list.index(next_game_home_team)
            
        # Add the travel distance of the two locations from the distance matrix
        travel_fitness += distance_matrix[location_one][location_two]


    # Calculate total team fiitness
    fitness = (game_rest_fitness * game_rest_weight) + (home_away_fitness * home_away_weight) + (travel_fitness * travel_weight)

    return fitness


def total_schedule_fitness(schedule: list[list[int]], distance_matrix: list[list[float]], games: dict = ALL_GAMES, arena_locations: dict = ARENA_LOCATIONS, start_date: datetime.date = START_DATE) -> float:
    """
    Calculates the total fitness of an entire NHL schedule by summing the fitness of all teams.

    :param schedule: a list of lists of integers where each inner list contains game IDs scheduled for that day
    :param distance_matrix: a matrix containing the travel distance between all NHL arenas
    :param games: a dictionary mapping game_ids to the teams playing in them ([home_team, away_team])
    :param arena_locations: a dictionary mapping team_names to arena locations ({"lat": float, "lon": float})
    :param start_date: a datetime.date object of the schedule's start date
    :return total_fitness: the total fitness score of the schedule
    :return each_team_fitness: a dictionary of each team's fitness score
    """

    team_list = list(arena_locations.keys())

    # Build each team's individual schedules
    team_schedules = defaultdict(list)
    for day_offset, games_today in enumerate(schedule):
        current_day = start_date + datetime.timedelta(days=day_offset)
        if games_today != None:
            for game_id in games_today:
                home, away = games[str(game_id)]
                team_schedules[home].append((home, away, current_day))
                team_schedules[away].append((home, away, current_day))

    total_fitness = 0
    each_team_fitness = {}
    # For every team's schedule, add it's fitness to the total and to a dictionary
    for team in team_list:
        index = team_list.index(team)
        current_team_schedule_fitness = team_schedule_fitness(team_schedules[team], distance_matrix, index, team_list)
        total_fitness += current_team_schedule_fitness
        each_team_fitness[team] = round(current_team_schedule_fitness, 2)

    return total_fitness, each_team_fitness


def evaluate_population(population: list[list[int]], distance_matrix: list[list[float]]) -> list[float]:
    """
    Evaluate the fitness of each chromosome in the population.

    :param population: a list of schedule chromosomes
    :return population_evaluation: a list of each chromosme's fitness
    """
    population_evaluation = []
    # Calculate the fitness for every chromosome in the population
    for chromosome in population:
        total_chromosome_fitness, _ = total_schedule_fitness(chromosome, distance_matrix)
        population_evaluation.append(total_chromosome_fitness)
    return population_evaluation


# ====================HELPER FUNCTIONS FOR GENETIC ALGORITHM OPERATORS====================
def get_date_from_index(day_index: int, start_date: datetime.date = START_DATE):
    """
    Get the datetime.date object for a given day index.

    :param day_index: an integer representing an index of a day list in a schedule list
    :param start_date: a datetime.date object of the schedule's start date
    :return date: the datetime.date object of the game index
    """
    date = start_date + datetime.timedelta(days=day_index)
    return date


def get_day_teams(day_list: list[int], game_to_exclude: int, games: dict = ALL_GAMES):
    """
    Get a set of teams playing on a day, excluding the teams that are playing in a game that will be removed.

    :param day_list: a list of integers representing the game IDs in a day
    :param game_to_exclude: an integer of the game ID to not include
    :param games: a dictionary mapping game_ids to the teams playing in them ([home_team, away_team])
    :return teams: a set containing the teams playing in the day (not including the teams that played in the game that was excluded)
    """
    teams = set()
    # Add the teams from the game IDs in the day list to a set (excluding the game to exclude)
    for game_id in day_list:
        if game_id != game_to_exclude:
            home, away = games[str(game_id)]
            teams.add(home)
            teams.add(away)
    return teams


def get_game_teams(game_id: int, games: dict = ALL_GAMES) -> list[str]:
    """
    Get the home and away team for a game ID.

    :param game_id: an integer of the game ID to get the teams for
    :param games: a dictionary mapping game_ids to the teams playing in them ([home_team, away_team])
    :return teams: a list of strings of the teams playing in the given game ID
    """
    teams = games[str(game_id)]
    return teams


# ====================GENETIC ALGORITHM OPERATORS====================
def generate_initial_schedule(games: dict = ALL_GAMES, start_date: datetime.date = START_DATE, end_date: datetime.date = END_DATE, invalid_dates: set[datetime.date] = INVALID_DATES) -> list[list[int]]:
    """
    Generate an initial randomized NHL schedule.
    The schedule is represented as a list of lists of integers. The inner lists represent days and the integers represent game IDs.
    No team plays more than once per day and games are not scheduled on invalid dates.

    :param games: a dictionary mapping game_ids to the teams playing in them ([home_team, away_team])
    :param start_date: a datetime.date object of the schedule's start date
    :param end_date: a datetime.date object of the schedule's end date
    :param invalid_dates: a set of datetime.date objects of dates that should not have games scheduled on them
    :return schedule: the generated schedule represented as a list of lists of integers
    """

    total_days = (end_date - start_date).days + 1

    # Create an empty schedule for all days
    schedule = []
    for _ in range(total_days):
        schedule.append([])

    # Map day index to actual date
    day_to_date = [start_date + datetime.timedelta(days=i) for i in range(total_days)]

    # Make a set for each day to track which teams play
    teams_playing = [set() for _ in range(total_days)]

    # Shuffle games for randomness
    all_game_ids = list(map(int, games.keys()))
    random.shuffle(all_game_ids)

    # Place each game into a day
    for game_id in all_game_ids:

        # Get the home and away team for the game
        home_team, away_team = games[str(game_id)]

        # Randomly shuffle the order of game day indicies to try
        day_indices = list(range(total_days))
        random.shuffle(day_indices)

        # Go through each day until a a valid game day is found (not an invalid day and both teams don't already play in a game that day)
        for day_id in day_indices:
            # Check if the day is valid
            if day_to_date[day_id] in invalid_dates:
                continue
            # Check if the day already has one of the teams playing
            if home_team not in teams_playing[day_id] and away_team not in teams_playing[day_id]:
                # Add the game to the schedule on the found day and track that the two teams are playing on that day
                schedule[day_id].append(game_id)
                teams_playing[day_id].update([home_team, away_team])
                break

    return schedule


def tournament_selection(population: list[list[list[int]]], population_fitness, tournament_size) -> list[list[list[int]]]:
    """
    Tournament selection selects the schedules to move on to the next generation.
    A tournament size number of schedules are chosen and the one with the lowest fitness moves on to the mating pool.
    Repeat until the mating pool reaches the population size.

    :param population: a list of schedules which are represented as as a list of lists of integers
    :param population_fitness: a list of corresponding fitness scores for the population
    :param tournament_size: the number of schedules chosen for each tournament round
    :return mating_pool: the list containing the winning schedules
    """
    mating_pool = []
    population_size = len(population)

    # Fill the mating pool with copies of tournament selection winners until the mating pool reaches the population size.
    for _ in range(population_size):
        indices = random.sample(range(population_size), k=tournament_size)
        winner_index = min(indices, key=lambda index: population_fitness[index])
        mating_pool.append(population[winner_index][:])
        
    return mating_pool


def apply_order_crossover(schedule_one: list[list[int]], schedule_two: list[list[int]], start_date: datetime.date = START_DATE, invalid_dates: set[datetime.date] = INVALID_DATES) -> list[list[int]]:
    """
    Applies order Crossover to two schedules.
    Order crossover maintains a slice of games from one schedule while filling the remaining spots with games from the other.

    :param schedule_one: the schedule to maintain the slice from
    :param schedule_two: the schedule to get the dates in new order from
    :param start_date: a datetime.date object of the schedule's start date
    :param invalid_dates: a set of datetime.date objects of dates that should not have games scheduled on them
    :return child_schedule: the schedule resulting from the order crossover
    """

    # The game_to_day_map maps the flattened index (0, 1, 2...) to its day index (0, 0, 1, 1, 2...)
    game_to_day_map = {}
    day_index = 0
    flat_index = 0

    # Flatten schedule 1 and build the game index to day map
    flat_schedule_one = []
    for day in schedule_one:
        for game_id in day:
            flat_schedule_one.append(game_id)
            game_to_day_map[flat_index] = day_index
            flat_index += 1
        day_index += 1

    # Flatten schedule 2
    flat_schedule_two = []
    for day in schedule_two:
        for game_id in day:
            flat_schedule_two.append(game_id)

    schedule_len = len(flat_schedule_one)

    # Pick the crossover slice 
    max_attempts = 5
    slice_start = -1
    slice_end = -1
    valid_slice_found = False

    for attempt in range(max_attempts):
        # Randomly pick slice indices
        slice_start, slice_end = sorted(random.sample(range(schedule_len), 2))
        
        # Determine the range of days covered by the game slice
        start_day_index = game_to_day_map[slice_start]
        end_day_index = game_to_day_map[slice_end]
        
        # Check if any day in the range is an invalid date
        range_is_invalid = False
        for current_day_index in range(start_day_index, end_day_index + 1):
            current_date = start_date + datetime.timedelta(days=current_day_index)
            if current_date in invalid_dates:
                range_is_invalid = True
                break
        
        if not range_is_invalid:
            valid_slice_found = True
            break

    # Abort if slice selection failed
    if not valid_slice_found:
        return schedule_one


    # Initialize the child schedule as an list of Nones
    flat_child_schedule = [None] * schedule_len

    # Copy the slice from schedule one
    schedule_one_slice = flat_schedule_one[slice_start:slice_end+1]
    flat_child_schedule[slice_start:slice_end+1] = schedule_one_slice
    # Identify games that were not in the chedule one slice
    schedule_one_slice_games = set(schedule_one_slice)
    # Get the games from schedule two in order, excluding those in the slice of schedule one
    schedule_two_fillers = (g for g in flat_schedule_two if g not in schedule_one_slice_games)
    # Find the positions in the child schedule that need filling
    fill_positions = (i for i, g in enumerate(flat_child_schedule) if g is None)
    # Fill the remaining positions using schedule two's games in relative order
    for i, g in zip(fill_positions, schedule_two_fillers):
        flat_child_schedule[i] = g

    # Reconstruct the schedule as the list of lists
    child_schedule = []
    flat_index = 0
    
    # Use the structure (day lengths) of schedule_one
    for day_list in schedule_one:
        day_len = len(day_list)
        # Extract the slice of the flat child schedule for this day
        day_games = flat_child_schedule[flat_index : flat_index + day_len]
        # Filter out any remaining None values
        child_schedule.append([g for g in day_games if g is not None])
        flat_index += day_len

    return child_schedule


def game_swap_mutation(schedule: list[list[int]], games: dict = ALL_GAMES, start_date: datetime.date = START_DATE, invalid_dates: set[datetime.date] = INVALID_DATES) -> list[list[int]]:
    """
    Applies a game swap mutation to a schedule.
    Chooses two random days, choses a random game from each day, and swaps their positions.

    :param schedule: the schedule to apply the mutation to
    :param games: a dictionary mapping game_ids to the teams playing in them ([home_team, away_team])
    :param start_date: a datetime.date object of the schedule's start date
    :param invalid_dates: a set of datetime.date objects of dates that should not have games scheduled on them
    :return schedule: the schedule resulting from the mutation
    """
    schedule_len = len(schedule)

    # If mutation is not sucessful after 5 attmepts, abort
    max_attempts = 5
    attempts = 0
    mutation_successful = False
    while attempts < max_attempts and not mutation_successful:
        # Select two random days indicies
        day_one_index, day_two_index = random.sample(range(schedule_len), 2)
        
        # Check if both days are valid dates
        date_one = get_date_from_index(day_one_index, start_date)
        date_two = get_date_from_index(day_two_index, start_date)
        if date_one in invalid_dates or date_two in invalid_dates:
            attempts += 1
            continue

        # Get the list of games from each day
        day_one_games = schedule[day_one_index]
        day_two_games = schedule[day_two_index]
        
        # If day 1 has games and day 2 has games, move one game from day 1 to 2 and one game from 2 to 1
        if day_one_games and day_two_games:
            game_one_index = random.randrange(len(day_one_games))
            game_two_index = random.randrange(len(day_two_games))
            game_one_id = day_one_games[game_one_index]
            game_two_id = day_two_games[game_two_index]
            
            home_one, away_one = get_game_teams(game_one_id)
            home_two, away_two = get_game_teams(game_two_id)
            
            # Get the teams playing on each day (excluding the teams that are playing in the game that would be swapped out)
            teams_one_remaining = get_day_teams(day_one_games, game_to_exclude=game_one_id, games=games)
            teams_two_remaining = get_day_teams(day_two_games, game_to_exclude=game_two_id, games=games)
            
            # Check to make sure no team is playing twice in a day after the swap
            valid_day_one = home_two not in teams_one_remaining and away_two not in teams_one_remaining
            valid_day_two = home_one not in teams_two_remaining and away_one not in teams_two_remaining

            if valid_day_one and valid_day_two:
                # Perform the swap
                schedule[day_one_index][game_one_index] = game_two_id
                schedule[day_two_index][game_two_index] = game_one_id
                mutation_successful = True
        
        # If day 1 has games and day 2 does not, move one game from day 1 to 2
        elif day_one_games and not day_two_games:
            game_one_index = random.randrange(len(day_one_games))
            game_one_id = day_one_games[game_one_index]
            
            # Perform the swap
            game_id = schedule[day_one_index].pop(game_one_index)
            schedule[day_two_index].append(game_id)
            mutation_successful = True
        
        # If day 1 has no games and day 2 does, move one game from day 2 to 1
        elif not day_one_games and day_two_games:
            game_two_index = random.randrange(len(day_two_games))
            game_two_id = day_two_games[game_two_index]

            # Perform the swap
            game_id = schedule[day_two_index].pop(game_two_index)
            schedule[day_one_index].append(game_id)
            mutation_successful = True

        # If day 1 has no games and day 2 has no games, select new dates
        else:
            attempts += 1

    return schedule


def day_swap_mutation(schedule: list[list[int]], start_date: datetime.date = START_DATE, invalid_dates: set[datetime.date] = INVALID_DATES) -> list[list[int]]:
    """
    Applies a day swap mutation to a schedule.
    Chooses two random days, and swaps their positions.

    :param schedule: the schedule to apply the mutation to
    :param start_date: a datetime.date object of the schedule's start date
    :param invalid_dates: a set of datetime.date objects of dates that should not have games scheduled on them
    :return schedule: the schedule resulting from the mutation
    """
    schedule_len = len(schedule)

    # If mutation is not sucessful after 5 attmepts, abort
    max_attempts = 5
    attempt = 0
    mutation_successful = False
    while attempt < max_attempts and not mutation_successful:
        # Choose two random day indices to swap
        day_one_index, day_two_index = random.sample(range(schedule_len), 2)
        
        # Get the actual datetime dates for the chosen indices
        date_one = get_date_from_index(day_one_index, start_date)
        date_two = get_date_from_index(day_two_index, start_date)
        
        # Check if both days are valid dates
        if date_one not in invalid_dates and date_two not in invalid_dates:
            # Swap the days
            schedule[day_one_index], schedule[day_two_index] = schedule[day_two_index], schedule[day_one_index]
            mutation_successful = True
        # If at least one of the days is an incvalid date, select new dates
        else:
            attempt += 1

    return schedule


def day_inversion_mutation(schedule: list[list[int]], start_date: datetime.date = START_DATE, invalid_dates: set[datetime.date] = INVALID_DATES) -> list[list[int]]:
    """
    Applies a day inversion mutation to a schedule.
    Chooses two random days, and inverts the order of the range from the two selected days.

    :param schedule: the schedule to apply the mutation to
    :param start_date: a datetime.date object of the schedule's start date
    :param invalid_dates: a set of datetime.date objects of dates that should not have games scheduled on them
    :return schedule: the schedule resulting from the mutation
    """
    schedule_len = len(schedule)

    # If mutation is not sucessful after 5 attmepts, abort
    max_attempts = 5
    attempt = 0
    mutation_successful = False
    while attempt < max_attempts and not mutation_successful:
        # Choose two random day indices for the range
        start_day_index, end_day_index = sorted(random.sample(range(schedule_len), 2))
        
        # Check if the range contains any invalid dates
        range_is_invalid = False
        for day_index in range(start_day_index, end_day_index + 1):
            current_date = get_date_from_index(day_index, start_date)
            if current_date in invalid_dates:
                range_is_invalid = True
                break
        
        # If the range does not include invalid days
        if not range_is_invalid:
            # Invert the range order
            schedule[start_day_index:end_day_index+1] = schedule[start_day_index:end_day_index+1][::-1] # Use slice notation for in-place reversal
            mutation_successful = True
        # If an invalid day is in the range, select a new date range
        else:
            attempt += 1

    return schedule


def apply_mutation(schedule: list[list[int]], no_day_inversion) -> list[list[int]]:
    """
    Applies one of three mutations to a schedule.
    Randomly picks one of a game swap mutation, a day swap mutation, or a day inversion mutation to a schedule.
    
    :param schedule: the schedule to apply the mutation to
    :param no_day_inversion: a boolean value that signifies if a day inversion is one of the mutations
    :return schedule: the schedule resulting from the mutation
    """
    mutation_decider = random.random()
    # If the day inversion mutation is not an option, randomly pick and apply either a game swap or a day swap mutation
    if no_day_inversion:
        if mutation_decider <= (1/2):
            schedule = game_swap_mutation(schedule)
        else:
            schedule = day_swap_mutation(schedule)
    # Randomly pick and apply either a game swap, day swap mutation, or day inversion mutation
    else:
        if mutation_decider <= (1/3):
            schedule = game_swap_mutation(schedule)
        elif (1/3) < mutation_decider <= (2/3):
            schedule = day_swap_mutation(schedule)
        else:
            schedule = day_inversion_mutation(schedule)

    return schedule


def apply_elitism(mating_pool: list[list[list[int]]], mating_pool_fitnesses: list[float], best_chromosome: list[list[int]]) -> list[list[list[int]]]:
    """
    Replace the worst schedule in mating pool with the given best schedule from the previous population.
    
    :param mating_pool: the mating pool which is a list of schedules
    :param mating_pool_fitnesses: a list of coresponding fitness values to each schedule in the mating pool
    :param best_chromosome: the best schedule of the previous generation
    :return mating_pool: the mating pool with the worst schedule replaced by the best schedule
    """
    # Find the worst schedule and replace it with the given best schedule
    worst_index = mating_pool_fitnesses.index(max(mating_pool_fitnesses))
    mating_pool[worst_index] = best_chromosome

    return mating_pool
