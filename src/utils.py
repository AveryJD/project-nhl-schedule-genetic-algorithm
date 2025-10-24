
# Imports
import math
import random
import datetime
from collections import defaultdict

# Set the starting year of the schedule
SCHEDULE_START_YEAR = 2026
start_date = datetime.date(SCHEDULE_START_YEAR, 10, 7)


# ====================DISTANCE FUNCTIONS====================
def calc_distance(current_location: tuple[float, float], traveling_location: tuple[float, float]) -> float:
    """
    Calculate the distance between two latitude and longitude coordinates using the Haversine formula.

    :param current_location: (latitude, longitude) tuple for the first location
    :param traveling_location: (latitude, longitude) tuple for the second location
    :return: distance between the coordinates (in kilometers)
    """

    # Unwrap the latitude and longitude coords
    lat_one, lon_one = current_location
    lat_two, lon_two = traveling_location
    # Earth's radius in km
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


def make_distance_matrix(arena_locations: dict) -> list[list[float]]:
    """
    Create a matrix of distances between all team arenas.

    :param arena_locations: dictionay mapping team abbreviations to latitude and longitude coordinates
    :return: list where [i][j] is the distance between team i and team j in kilometers
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


# ====================SCHEDULE FUNCTIONS====================
def generate_initial_schedule(games: dict, start_year=SCHEDULE_START_YEAR) -> list[list[int]]:
    """
    Generate an initial randomized NHL schedule.

    Each inner list represents one day in the season and contains game IDs for that day.
    No team plays more than once per day.
    Games are skipped on invalid dates (holidays, Olympic break, etc.).

    :param games: dict mapping game_id (as string) to [home_team, away_team]
    :return: 2D list of integers representing the full season schedule
    """

    end_year = start_year + 1
    start_date = datetime.date(start_year, 10, 7)
    end_date = datetime.date(end_year, 4, 15)

    total_days = (end_date - start_date).days + 1

    # Determine days that NHL games can not be scheduled on
    invalid_dates = set()
    invalid_dates.add(datetime.date(start_year, 11, 26))  # American Thanksgiving
    invalid_dates.add(datetime.date(start_year, 12, 24))  # Christmas Eve
    invalid_dates.add(datetime.date(start_year, 12, 25))  # Christmas
    invalid_dates.add(datetime.date(start_year, 12, 26))  # Boxing Day (if Boxing Day falls on a Saturday, then Dec. 23 is the day with no games)
    invalid_dates.add(datetime.date(end_year, 2, 14))     # Super Bowl Sunday

    all_star_start = datetime.date(end_year, 2, 8)        # February break ~ 2 weeks (Olympics, four nations, All star)
    all_star_end = datetime.date(end_year, 2, 21)
    for i in range((all_star_end - all_star_start).days + 1):
        invalid_dates.add(all_star_start + datetime.timedelta(days=i))

    # Create an empty schedule for all days
    schedule = [[] for _ in range(total_days)]

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


def get_single_team_schedule(full_schedule: list[list[int]], games: dict, team: str, start_date=start_date) -> list[tuple[str, str, datetime.date]]:
    """
    Extract the schedule for a single team from the full season schedule.

    :param full_schedule: list of lists; each inner list contains game IDs scheduled for that day
    :param games: dict mapping game_id -> [home_team, away_team]
    :param team_id: abbreviation of the team to extract
    :param start_date: date of the first day in the schedule
    :return: list of (home_team, away_team, game_date) tuples for this team in chronological order
    """
    team_schedule = []

    for day_offset, games_today in enumerate(full_schedule):
        current_day = start_date + datetime.timedelta(days=day_offset)
        if games_today != None:
            for game_id in games_today:
                home_team, away_team = games[str(game_id)]
                if team == home_team or team == away_team:
                    team_schedule.append((home_team, away_team, current_day.strftime('%d/%m/%Y')))

    return team_schedule


# ====================FITNESS FUNCTIONS====================
def team_schedule_fitness(team_schedule: list[tuple[str, str]], dist_matrix: list[list[float]], team_index: int, team_list: list[str]) -> float:
    fitness = 0

    # Weight parameters
    REST_WEIGHT = 0.90
    STREAK_WEIGHT = 0.09
    TRAVEL_WEIGHT = 0.01

    # Optimizing rest time 
    for i in range(len(team_schedule) - 1):
        current_day = team_schedule[i][2]
        next_day = team_schedule[i + 1][2]
        day_gap = (next_day - current_day).days

        if day_gap == 1:
            # 1 day between games (back-to-back)
            fitness -= REST_WEIGHT * 1
        elif day_gap == 2:
            fitness -= REST_WEIGHT * 4
        elif day_gap >= 3:
            fitness -= REST_WEIGHT * 3
        elif day_gap >= 4:
            fitness -= REST_WEIGHT * 1
        else:
            fitness += REST_WEIGHT * 1000

    # Optimizing home/away streak balance
    streak = 1
    last_home = team_schedule[0][0] == team_list[team_index]
    for i in range(1, len(team_schedule)):
        current_home = team_schedule[i][0] == team_list[team_index]
        if current_home == last_home:
            streak += 1
        else:
            if streak > 4:
                fitness -= STREAK_WEIGHT * (streak - 3)
            else:
                fitness += STREAK_WEIGHT
            streak = 1
            last_home = current_home

    # Minimizing travel distance
    for i in range(len(team_schedule) - 1):
        if not team_schedule[i]:
            continue
        loc1 = team_index if team_schedule[i][0] == team_list[team_index] else team_list.index(team_schedule[i][0])
        j = i + 1
        while j < len(team_schedule) and not team_schedule[j]:
            j += 1
        if j >= len(team_schedule):
            break
        loc2 = team_index if team_schedule[j][0] == team_list[team_index] else team_list.index(team_schedule[j][0])
        fitness += TRAVEL_WEIGHT * dist_matrix[loc1][loc2]

    # Avoid more that 2 games in a row
    for i in range(len(team_schedule) - 2):
        day1, day2, day3 = team_schedule[i][2], team_schedule[i+1][2], team_schedule[i+2][2]
        if (day2 - day1).days == 1 and (day3 - day2).days == 1:
            fitness += 10_000

    return fitness



def total_schedule_fitness(schedule: list[list[int]], games: dict, arena_locations: dict, distance_matrix) -> float:
    """
    Calculates the total fitness of an entire NHL schedule by summing the fitness of all teams.

    :param schedule: list of lists; each inner list contains game IDs scheduled for that day
    :param games: dict mapping game_id -> [home_team, away_team]
    :param arena_locations: dict mapping team_name -> {"lat": float, "lon": float}
    :return: total fitness score (higher = better schedule)
    """

    team_list = list(arena_locations.keys())

    # Build per-team schedules
    team_schedules = defaultdict(list)
    start_date = datetime.date(2025, 10, 4)
    for day_offset, games_today in enumerate(schedule):
        current_day = start_date + datetime.timedelta(days=day_offset)
        if games_today != None:
            for game_id in games_today:
                home, away = games[str(game_id)]
                team_schedules[home].append((home, away, current_day))
                team_schedules[away].append((home, away, current_day))

    total_fitness = 0
    for team in team_list:
        idx = team_list.index(team)
        total_fitness += team_schedule_fitness(team_schedules[team], distance_matrix, idx, team_list)

    return total_fitness


def evaluate_population(population: list[list[int]], games: dict, arena_locations: dict, distance_matrix) -> list[float]:
    """
    Evaluate the fitness of each chromosome in the population.

    :param population: 
    :return: 
    """
    population_evaluation = []
    # Calculate the fitness for every chromosome in the population
    for chromosome in population:
        population_evaluation.append(total_schedule_fitness(chromosome, games, arena_locations, distance_matrix))
    return population_evaluation


# ====================GP OPERATORS====================
def tournament_selection(population, population_fitness, tournament_size):
    mating_pool = []
    population_size = len(population)

    for _ in range(population_size):
        indices = random.sample(range(population_size), k=tournament_size)
        winner_index = min(indices, key=lambda idx: population_fitness[idx])
        mating_pool.append(population[winner_index][:])
    return mating_pool


def apply_order_crossover(parent1, parent2):
    size = len(parent1)
    child = [None] * size

    # Random slice
    start, end = sorted(random.sample(range(size), 2))
    child[start:end] = parent1[start:end]

    # Fill remaining from parent2
    ptr = end
    for gene in parent2:
        if gene not in child:
            if ptr >= size:
                ptr = 0
            child[ptr] = gene
            ptr += 1

    return child


def swap_game_mutation(schedule, games):
    """Swap two games on different days if it doesn't cause a team to play twice a day."""
    total_days = len(schedule)
    day1, day2 = random.sample(range(total_days), 2)
    if not schedule[day1] or not schedule[day2]:
        return schedule  # nothing to swap
    
    game1 = random.choice(schedule[day1])
    game2 = random.choice(schedule[day2])

    home1, away1 = games[str(game1)]
    home2, away2 = games[str(game2)]

    # Check if swap is valid
    teams_day1 = {games[str(g)][0] for g in schedule[day1]} | {games[str(g)][1] for g in schedule[day1]}
    teams_day2 = {games[str(g)][0] for g in schedule[day2]} | {games[str(g)][1] for g in schedule[day2]}
    
    if (home2 not in teams_day1 and away2 not in teams_day1) and (home1 not in teams_day2 and away1 not in teams_day2):
        idx1 = schedule[day1].index(game1)
        idx2 = schedule[day2].index(game2)
        schedule[day1][idx1], schedule[day2][idx2] = game2, game1

    return schedule


def swap_day_mutation(schedule):
    """Swap the games of two entire days."""
    day1, day2 = random.sample(range(len(schedule)), 2)
    schedule[day1], schedule[day2] = schedule[day2], schedule[day1]
    return schedule


def day_inversion_mutation(schedule):
    """Pick two random days and invert the order of the days between them."""
    start, end = sorted(random.sample(range(len(schedule)), 2))
    schedule[start:end+1] = reversed(schedule[start:end+1])
    return schedule


def apply_mutation(schedule, games, mutation_rate):
    """Apply one of the three mutations based on a ratio."""
    if random.random() < mutation_rate:
        if random.random() < 0.5:
            # Apply swap mutation (randomly game or day)
            if random.random() < 0.5:
                schedule = swap_game_mutation(schedule, games)
            else:
                schedule = swap_day_mutation(schedule)
        else:
            # Apply inversion mutation
            schedule = day_inversion_mutation(schedule)
    return schedule


def apply_elitism(mating_pool, mating_pool_fitnesses, best_chromosome):
    # Replace worst in mating pool
    worst_idx = mating_pool_fitnesses.index(max(mating_pool_fitnesses))
    mating_pool[worst_idx] = best_chromosome

    return mating_pool


