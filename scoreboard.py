import datetime
import sched
import time

import mlbgame

try:
    from board.display import DisplayController
except ImportError:
    class DisplayController:
        def on(self):
            pass
        def off(self):
            pass
        def set_top_score(self, runs):
            pass
        def set_bottom_score(self, runs):
            pass
        def set_inning(self, inning):
            pass


DEFAULT_TEAM = "Indians"
IN_PROGRESS = "In Progress"
WARMUP = "Warmup"
FINAL = "Final"
CANCELLED = "Cancelled"
DELAYED = "Delayed"
DELAYED_START = "Delayed Start"
TRACKABLE_STATUSES = set([IN_PROGRESS, WARMUP, DELAYED, DELAYED_START])


def handle_day(scheduler, display, team):
    now = datetime.datetime.now()
    todays_games = mlbgame.day(now.year, now.month, now.day,
            home=team, away=team)
    print "%d games today" % len(todays_games)
    for game in todays_games:
        if game.date <= now:
            game_details = mlbgame.overview(game.game_id)
            if game_details.status in TRACKABLE_STATUSES:
                track_game(scheduler, game.game_id, display)
        else:
            schedule_tracking(scheduler, game.game_id)
    next_day = (now + datetime.timedelta(days=1)).replace(
            hour=8, minute=0, second=0, microsecond=0)
    wait_seconds = (next_day - datetime.datetime.now()).seconds
    print "Scheduling for %s tomorrow (%d seconds from now)" % (
            next_day, wait_seconds)
    scheduler.enter(wait_seconds, 0, handle_day, (scheduler, display))

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
    import sys
    if len(sys.argv) > 1:
        team = sys.argv[1]
    else:
        team = DEFAULT_TEAM
    print "Starting %s scoreboard" % team
    display = DisplayController()
    display.on()
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(0, 0, handle_day, (scheduler, display, team))
    try:
        scheduler.run()
    finally:
        display.off()

