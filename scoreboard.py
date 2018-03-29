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
        # hack the start time until my PR is accepted
        year, month, day = game.game_id.split('_')[:3]
        game_start_date = "/".join([year, month, day])
        start_time = datetime.datetime.strptime(
               " ".join([game_start_date,
                    game.game_start_time.replace(' ', '')]),
               "%Y/%m/%d %I:%M%p")
        if start_time <= now:
            game_details = mlbgame.overview(game.game_id)
            if game_details.status in TRACKABLE_STATUSES:
                track_game(scheduler, game.game_id, display)
        else:
            wait_game = (start_time - datetime.datetime.now()).seconds
            print ("Tracking for today's game (%s) will start at "
                    "%s (%d seconds from now)") % (
                            game.game_id, _format_time(start_time), wait_game)
            scheduler.enter(wait_game, 0, track_game,
                    (scheduler, game.game_id, display))
    next_day = (now + datetime.timedelta(days=1)).replace(
            hour=8, minute=0, second=0, microsecond=0)
    wait_tomorrow = (next_day - datetime.datetime.now()).total_seconds()
    print "Checking tomorrow's schedule at %s (%d seconds from now)" % (
            _format_time(next_day), wait_tomorrow)
    scheduler.enter(wait_tomorrow, 0, handle_day, (scheduler, display))

def track_game(scheduler, game_id, display):
    game_details = mlbgame.overview(game_id)
    print "%s: %d, %s: %d, %s of %d" % (game_details.home_team_name,
            game_details.home_team_runs,
            game_details.away_team_name,
            game_details.away_team_runs,
            game_details.inning_state,
            game_details.inning)
    display.set_top_score(_get_safe_number(game_details.away_team_runs))
    display.set_bottom_score(_get_safe_number(game_details.home_team_runs))
    display.set_inning(_get_safe_number(game_details.inning))
    if game_details.status in TRACKABLE_STATUSES:
        scheduler.enter(30, 0, track_game, (scheduler, game_id, display))

def _get_safe_number(value):
    return value if value != '' else 0

def _format_time(dt):
    return dt.time().strftime("%I:%M%p")

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

