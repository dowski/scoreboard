import datetime
import sched
import time

import mlbgame

from board.display import DisplayController


INDIANS = "Indians"
IN_PROGRESS = "In Progress"
WARMUP = "Warmup"
FINAL = "Final"
CANCELLED = "Cancelled"
DELAYED = "Delayed"
DELAYED_START = "Delayed Start"
TRACKABLE_STATUSES = set([IN_PROGRESS, WARMUP, DELAYED, DELAYED_START])


def handle_day(scheduler, display):
    now = datetime.datetime.now()
    todays_games = mlbgame.day(now.year, now.month, now.day,
            home=INDIANS, away=INDIANS)
    for game in todays_games:
        if game.date <= now:
            game_details = mlbgame.overview(game.game_id)
            if game_details.status in TRACKABLE_STATUSES:
                track_game(scheduler, game.game_id, display)
        else:
            schedule_tracking(scheduler, game.game_id)

def track_game(scheduler, game_id, display):
    game_details = mlbgame.overview(game_id)
    print "%s: %d, %s: %d, %s of %d" % (game_details.home_team_name,
            game_details.home_team_runs,
            game_details.away_team_name,
            game_details.away_team_runs,
            game_details.inning_state,
            game_details.inning)
    display.set_top_score(game_details.away_team_runs)
    display.set_bottom_score(game_details.home_team_runs)
    display.set_inning(game_details.inning)
    if game_details.status in TRACKABLE_STATUSES:
        scheduler.enter(30, 0, track_game, (scheduler, game_id, display))

def schedule_tracking(scheduler, game_id):
    print "Can't schedule tracking yet"
    pass

if __name__ == '__main__':
    display = DisplayController()
    display.on()
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(0, 0, handle_day, (scheduler, display))
    try:
        scheduler.run()
    finally:
        display.off()

