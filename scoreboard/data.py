import datetime

from collections import namedtuple


GameDetails = namedtuple('GameDetails', [
    'inning',
    'home_team_runs',
    'away_team_runs',
    'balls',
    'strikes',
    'outs',
    'status',
    'inning_state',
    'baserunners',
    ])

ScheduledGame = namedtuple('ScheduledGame', [
    'game_id',
    'start_time',
    'home_team_name',
    'away_team_name',
    ])

