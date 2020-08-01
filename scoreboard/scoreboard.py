import datetime
import sched
import sys
import time

from . import mlb
from . import schedule
from . import tracker


DEFAULT_TEAM = "Indians"


try:
    from .board.display import DisplayController
except ImportError:
    try:
        from .bigboard.display import DisplayController
    except ImportError:
        # The scoreboard hardware interface isn't available - stub it out
        class DisplayController:
            def on(self):
                pass
            def off(self):
                pass
            def set_away_runs(self, runs, is_favorite_team=False):
                pass
            def set_home_runs(self, runs, is_favorite_team=False):
                pass
            def set_inning(self, inning, is_bottom=False):
                pass
            def set_inning_state(self, balls, strikes, outs):
                pass
            def set_baserunners(self, baserunners):
                pass


def start():
    main(sys.argv)


def main(argv):
    if len(argv) > 1:
        team = argv[1]
    else:
        team = DEFAULT_TEAM

    mlb.Api.install_alarm_handler()
    jobs = sched.scheduler(time.time, time.sleep)
    display = DisplayController()
    api = mlb.Api()
    game_tracker = tracker.GameTracker(team, jobs, api, display)
    game_scheduler = schedule.GameScheduler(jobs, team, game_tracker, api)

    print("Starting %s scoreboard" % team)
    display.on()
    jobs.enter(0, 0, game_scheduler.run, ())
    try:
        jobs.run()
    finally:
        display.off()

if __name__ == '__main__':
    main(sys.argv)
