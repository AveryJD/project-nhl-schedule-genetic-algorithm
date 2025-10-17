
# Imports
import math
import random
import datetime
import json


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



def generate_initial_schedule(games: dict) -> list[list[int]]:
    """
    Generate an initial randomized NHL schedule.

    Each inner list represents one day in the season and contains game IDs for that day.
    No team plays more than once per day.
    Games are skipped on invalid dates (holidays, Olympic break, etc.).

    :param games: dict mapping game_id (as string) to [home_team, away_team]
    :return: 2D list of integers representing the full season schedule
    """

    # Set schedule start and end dates (YYYY-MM-DD format)
    start_date = '2025-10-04'
    end_date = '2026-04-15'
    # Convert to value to date 
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    total_days = (end - start).days + 1

    # Determine days that NHL games can not be scheduled on
    invalid_dates = set()
    invalid_dates.add(datetime.date(2025, 11, 27))  # American Thanksgiving
    invalid_dates.add(datetime.date(2025, 12, 24))  # Christmas Eve
    invalid_dates.add(datetime.date(2025, 12, 25))  # Christmas
    invalid_dates.add(datetime.date(2025, 12, 26))  # Boxing Day
    invalid_dates.add(datetime.date(2026, 2, 8))    # Super Bowl Sunday
    
    # Olympic break (all-star break in other years)
    olympic_start = datetime.date(2026, 2, 6)
    olympic_end = datetime.date(2026, 2, 24)
    for i in range((olympic_end - olympic_start).days + 1):
        invalid_dates.add(olympic_start + datetime.timedelta(days=i))

    # Create an empty schedule for all days
    schedule = [[] for _ in range(total_days)]

    # Map day index to actual date
    day_to_date = [start + datetime.timedelta(days=i) for i in range(total_days)]

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




def team_schedule_fitness() -> float:
    # Fitness Function For a Team(team_schedule: list[int], dist_matrix: list[list[float]]):
    # Optimize rest time (number of games/days off in a row) (3 games in a row=very bad, two=good, one=great)
    # Optimize game streaks (number of home/away games in a row)
    # Optimize team travel (minimize total travel distance)

    # Track current team's location

    fitness = 0

    return fitness



def total_schedule_fitness() -> float:
    # Total Fitness Function (schedule: [list...]):
    # Break full schedule into individual team schedules
    # Calculate each team's schedule fitness function
    # Sum all teams fitness function

    fitness = 0
    return fitness


# Selection

# Crossover

# Mutation

# Elitism