

import json
import utils
import matplotlib.pyplot as plt
import calendar
from datetime import datetime


# Load the saved best schedule
best_schedule_json = open('schedule_info/best_schedule.json')
BEST_SCHEDULE = json.load(best_schedule_json)

games_json = open('schedule_info/nhl_all_games.json')
ALL_GAMES = json.load(games_json)

# The schedule's start and finish dates
SCHEDULE_START_DATE = datetime(2025, 10, 4)
SCHEDULE_END_DATE = datetime(2026, 4, 15)

# List of all NHL teams
ALL_TEAMS = ["BOS", "BUF", "DET", "FLA", "MTL", "OTT", "TBL", "TOR",
             "CAR", "CBJ", "NJD", "NYI", "NYR", "PHI", "PIT", "WSH",
             "CHI", "COL", "DAL", "MIN", "NSH", "STL", "UTA", "WPG",
             "ANA", "CGY", "EDM", "LAK", "SJS", "SEA", "VGK", "VAN"]


def team_schedule_calendar_visualization(team_schedule, team):

    # Organize games by month
    games_by_month = {}
    for home, away, date_str in team_schedule:
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        month = date_obj.month
        year = date_obj.year
        day = date_obj.day
        if (year, month) not in games_by_month:
            games_by_month[(year, month)] = {}
        games_by_month[(year, month)][day] = f"vs {away}" if home == team else f"@ {home}"

    # List of months in season order
    season_months = [(2025, m) for m in range(10, 13)] + [(2026, m) for m in range(1, 5)]

    # Create subplots (one per month)
    fig, axes = plt.subplots(2, 4, figsize=(24, 10))
    axes = axes.flatten()

    for idx, (year, month) in enumerate(season_months):
        ax = axes[idx]
        ax.set_title(f"{calendar.month_name[month]} {year}")
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 6)
        ax.axis("off")

        cal = calendar.Calendar(firstweekday=6)  # Sunday start
        month_days = cal.monthdayscalendar(year, month)

        for week_idx, week in enumerate(month_days):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue
                y = 5 - week_idx
                ax.add_patch(plt.Rectangle((day_idx, y), 1, 1, edgecolor='black', facecolor='white'))
                ax.text(day_idx + 0.05, y + 0.7, str(day), fontsize=9, fontweight='bold')
                if (year, month) in games_by_month and day in games_by_month[(year, month)]:
                    game_text = games_by_month[(year, month)][day]
                    color = 'blue' if 'vs' in game_text else 'red'
                    ax.text(day_idx + 0.05, y + 0.35, game_text, fontsize=8, color=color)

    # Hide unused subplot (2x4 → 8, we have 7 months)
    axes[-1].axis('off')

    plt.suptitle(f"{team} 2025-2026 Season Schedule", fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(f'visualizations/calendars/{team}_schedule.png')
    plt.close()



# Create the calendar for all teams
for team in ALL_TEAMS:
    team_schedule = utils.get_single_team_schedule(BEST_SCHEDULE, ALL_GAMES, team, SCHEDULE_START_DATE)
    team_schedule_calendar_visualization(team_schedule, team)