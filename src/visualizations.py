
# Imports
import json
import matplotlib.pyplot as plt
import calendar
import datetime


# ====================LOAD SCHEDULE INFORMATION====================
# Load the saved best schedule
best_schedule_json = open('results_genetic_algorithm/best_schedule.json')
BEST_SCHEDULE = json.load(best_schedule_json)

# Load the game IDs
games_json = open('schedule_info/nhl_all_games.json')
ALL_GAMES = json.load(games_json)

# Get fitness data
fitness_json = open('results_genetic_algorithm/fitness_results.json')
fitness_data = json.load(fitness_json)
GENERATION_BEST_FITNESS = fitness_data['generation_best_fitnesses']
GENERATION_AVERAGE_FITNESS = fitness_data['generation_average_fitnesses']

# List of all NHL teams
ALL_TEAMS = ["BOS", "BUF", "DET", "FLA", "MTL", "OTT", "TBL", "TOR",
             "CAR", "CBJ", "NJD", "NYI", "NYR", "PHI", "PIT", "WSH",
             "CHI", "COL", "DAL", "MIN", "NSH", "STL", "UTA", "WPG",
             "ANA", "CGY", "EDM", "LAK", "SJS", "SEA", "VGK", "VAN"]


# ====================DATE CONSTANTS====================
# The schedule's start and end dates
START_DATE = datetime.date(2026, 10, 7)
END_DATE = datetime.date(2027, 4, 16)

# Invalid days
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


# ========================================PLOT BEST VS AVERAGE FITNESSES FUNCTION========================================
def plot_best_vs_average_fitness(generation_best_fitness: list[float], 
                                 generation_average_fitness: list[float], 
                                 generation_to_start_at: int = 0) -> None:
    """
    
    """

    best_fitness_subset = generation_best_fitness[generation_to_start_at:]
    average_fitness_subset = generation_average_fitness[generation_to_start_at:]

    generations = range(generation_to_start_at, generation_to_start_at + len(best_fitness_subset))

    # Plot best vs average fitness
    plt.figure(figsize=(10, 5))
    plt.plot(generations, best_fitness_subset, label='Generation Best Fitness')
    plt.plot(generations, average_fitness_subset, label='Generation Average Fitness')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title(f'Genetic Algorithm Fitness Over Generations (Starting at Generation {generation_to_start_at})')
    plt.legend()
    plt.savefig(f'results_genetic_algorithm/fitness_over_generations_{generation_to_start_at}.png',  bbox_inches='tight')
    plt.close()


# ========================================CREATE CALENDARS FUNCTIONS========================================
def league_schedule_calendar_visualization(full_schedule : list[list[int]] = BEST_SCHEDULE,
                                           all_games: dict = ALL_GAMES,
                                           start_date: datetime.date = START_DATE, 
                                           end_date: datetime.date = END_DATE,  
                                           invalid_dates: set[datetime.date] = INVALID_DATES) -> None:
    """
    Visualize the entire league's schedule on a multi-month calendar, showing up to 6 games per day or the number of games if greater than 6.
    

    """
    
    #Map games to dates
    games_by_date = {}
    
    for day_index, game_id_list in enumerate(full_schedule):
        game_date = start_date + datetime.timedelta(days=day_index)
        
        if game_date not in games_by_date:
            games_by_date[game_date] = []

        for game_id in game_id_list:
            game_id_str = str(game_id)
            
            if game_id_str in all_games:
                home, away = all_games[game_id_str]
                games_by_date[game_date].append(f"{home} vs {away}")
            else:
                games_by_date[game_date].append(f"Game {game_id} (ID not found)")


    # Setup the plot 
    season_months = [(2026, m) for m in range(10, 13)] + [(2027, m) for m in range(1, 5)]

    cal = calendar.Calendar(firstweekday=6) 

    fig, axes = plt.subplots(2, 4, figsize=(28, 10)) 
    axes = axes.flatten()

    for idx, (year, month) in enumerate(season_months):
        ax = axes[idx]
        ax.set_title(f"{calendar.month_name[month]} {year}", fontsize=16, fontweight='bold')
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 6) 
        ax.axis("off")

        month_days = cal.monthdayscalendar(year, month)
        
        # Iterate and plot
        for week_idx, week in enumerate(month_days):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue
                
                y = 5 - week_idx 

                current_date = datetime.date(year, month, day)

                # Shade invalid dates
                if current_date in invalid_dates or current_date < start_date or current_date > end_date:
                    facecolor = (255/255, 180/255, 180/255)
                else:
                    facecolor = 'white'

                # Add the day block and number
                ax.add_patch(plt.Rectangle((day_idx, y), 1, 1, edgecolor='black', facecolor=facecolor))
                ax.text(day_idx + 0.05, y + 0.8, str(day), fontsize=10, fontweight='bold', color='black')

                # Add game text for games on the current day
                if current_date in games_by_date:
                    games = games_by_date[current_date]
                    num_games = len(games)
                    
                    # If more than 6 games are on a day, show the number of games (to not crowd the block)
                    if num_games <= 6:
                        # List up to MAX_GAMES_TO_LIST
                        y_offset = 0.65 
                        
                        for game_text in games:
                            ax.text(day_idx + 0.05, y + y_offset, game_text, fontsize=6, color='black', weight='bold')
                            y_offset -= 0.12
                    else:
                        # Show game count
                        ax.text(day_idx + 0.5, y + 0.4, 
                                f"{num_games} Games", 
                                ha='center', va='center', 
                                fontsize=10, color='black', weight='bold')

    # Hide unused month
    axes[-1].axis('off')

    plt.suptitle("Entire 2026-2027 Season Schedule", fontsize=24, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95]) 
    plt.savefig('calendars/_entire_schedule.png')
    plt.close()


def get_single_team_schedule(full_schedule: list[list[int]], 
                             team: str, 
                             games: dict = ALL_GAMES, 
                             start_date=START_DATE) -> list[tuple[str, str, datetime.date]]:
    """
    Extract the schedule for a single team from the full season schedule.

    :param full_schedule: list of lists; each inner list contains game IDs scheduled for that day
    :param games: dict mapping game_id -> [home_team, away_team]
    :param team: abbreviation of the team to extract
    :param start_date: date of the first day in the schedule
    :return: list of (home_team, away_team, game_date) tuples for this team in chronological order
    """
    team_schedule = []

    for day_offset, games_today in enumerate(full_schedule):
        current_day = start_date + datetime.timedelta(days=day_offset)
        if games_today:
            for game_id in games_today:
                home_team, away_team = games[str(game_id)]
                if team in [home_team, away_team]:
                    team_schedule.append((home_team, away_team, current_day))

    return team_schedule


def team_schedule_calendar_visualization(team_schedule: list[list[int]], team: str) -> None:
    """
    Visualize a team's schedule on a calendar.


    """
    # Organize games by month
    games_by_month = {}
    for home, away, game_date in team_schedule:
        month = game_date.month
        year = game_date.year
        day = game_date.day
        if (year, month) not in games_by_month:
            games_by_month[(year, month)] = {}
        games_by_month[(year, month)][day] = f"vs {away}" if home == team else f"@ {home}"


    season_months = [(2026, m) for m in range(10, 13)] + [(2027, m) for m in range(1, 5)]

    cal = calendar.Calendar(firstweekday=6) 

    fig, axes = plt.subplots(2, 4, figsize=(28, 10))
    axes = axes.flatten()

    for idx, (year, month) in enumerate(season_months):
        ax = axes[idx]
        ax.set_title(f"{calendar.month_name[month]} {year}", fontsize=16, fontweight='bold')
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 6)
        ax.axis("off")

        month_days = cal.monthdayscalendar(year, month)

        # Iterate and plot
        for week_idx, week in enumerate(month_days):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue

                y = 5 - week_idx

                current_date = datetime.datetime(year, month, day).date()

                # Shade invalid dates
                if current_date in INVALID_DATES or current_date < START_DATE or current_date > END_DATE:
                    facecolor = (255/255, 180/255, 180/255)
                else:
                    facecolor = 'white'

                # Add the day block and number
                ax.add_patch(plt.Rectangle((day_idx, y), 1, 1, edgecolor='black', facecolor=facecolor))
                ax.text(day_idx + 0.05, y + 0.8, str(day), fontsize=10, fontweight='bold', color='black')

                # Add game text if there's a game on the current day
                if (year, month) in games_by_month and day in games_by_month[(year, month)]:
                    game_text = games_by_month[(year, month)][day]
                    color = 'blue' if 'vs' in game_text else 'red'
                    ax.text(day_idx + 0.05, y + 0.35, game_text, fontsize=12, color=color, weight='bold')

    # Hide unused month
    axes[-1].axis('off')

    plt.suptitle(f"{team} 2026-2027 Season Schedule", fontsize=24, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(f'calendars/{team}_schedule.png')
    plt.close()


# ========================================CREATE VISUALIZATIONS========================================
if __name__ == "__main__":

    # Create the best vs average fitnesses plots
    plot_best_vs_average_fitness(GENERATION_BEST_FITNESS, GENERATION_AVERAGE_FITNESS)
    plot_best_vs_average_fitness(GENERATION_BEST_FITNESS, GENERATION_AVERAGE_FITNESS, 1000)

    # Create a calendar for the entire schedule
    league_schedule_calendar_visualization()

    # Create a calendar for each team's schedule
    for team in ALL_TEAMS:
        team_schedule = get_single_team_schedule(BEST_SCHEDULE, team)
        team_schedule_calendar_visualization(team_schedule, team)
