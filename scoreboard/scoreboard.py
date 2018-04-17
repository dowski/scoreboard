import datetime
import sched
import time

import mlb
import schedule
import tracker


DEFAULT_TEAM = "Indians"


try:
    from board.display import DisplayController
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

    print "Starting %s scoreboard" % team
    display.on()
    jobs.enter(0, 0, game_scheduler.run, ())
    try:
        jobs.run()
    finally:
        display.off()

if __name__ == '__main__':
    import sys
    main(sys.argv)
