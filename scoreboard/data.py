import datetime

from collections import namedtuple


GameDetails = namedtuple('GameDetails', [
    'inning',
    'home_team_runs',
    'away_team_runs',
    'balls',
    'strikes',
    'outs',
    'home_team_name',
    'away_team_name',
    'status',
    'inning_state',
    ])

ScheduledGame = namedtuple('ScheduledGame', [
    'game_id',
    'start_time',
    ])

