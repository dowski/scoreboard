import datetime

from mlb import FetchError


TIMEOUT_DELAY = 10


class GameScheduler(object):
    """Schedules the tracking of games each day."""

    def __init__(self, jobs, team, tracker, mlbapi):
        """Creates a new GameScheduler instance.

        The jobs argument should be a sched.scheduler instance (or compatible
        object). The team should be the string name of a team (e.g.
        "Indians"). The tracker should be a GameTracker for observing live
        games.

        """
        self.jobs = jobs
        self.team = team
        self.tracker = tracker
        self.mlbapi = mlbapi

    def run(self):
        """The main entry point for running the scoreboard.

        One call to this method will schedule daily tracking of games
        throughout the season. It will make one call when started to find out
        if there are any games on that day and it will also reschedule itself
        to be run on the next day (and so on).

        If games are found for a day, a GameTracker will be invoked when the
        starts (or if it is in-progress) to render progress of the game on the
        scoreboard.

        """
        now = datetime.datetime.now()
        try:
            todays_games = self.mlbapi.get_games(now, self.team)
        except FetchError as e:
            print "failed to fetch games - will try again"
            self.jobs.enter(TIMEOUT_DELAY, 0, self.run, ())
            return
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
                # game already started
                try:
                    game_details = self.mlbapi.get_game_detail(game.game_id)
                    if self.tracker.is_trackable(game_details.status):
                        self.tracker.track(game.game_id)
                except FetchError as e:
                    print "failed to fetch games - will try again"
                    self.jobs.enter(TIMEOUT_DELAY, 0, self.run, ())
                    return
            else:
                wait_game = (start_time - datetime.datetime.now()).seconds
                print ("Tracking for today's game (%s) will start at "
                        "%s (%d seconds from now)") % (
                                game.game_id, _format_time(start_time), wait_game)
                self.jobs.enter(wait_game, 0, self.tracker.track, (game.game_id,))
        next_day = (now + datetime.timedelta(days=1)).replace(
                hour=8, minute=0, second=0, microsecond=0)
        wait_tomorrow = (next_day - datetime.datetime.now()).total_seconds()
        print "Checking tomorrow's schedule at %s (%d seconds from now)" % (
                _format_time(next_day), wait_tomorrow)
        self.jobs.enter(wait_tomorrow, 0, self.run, ())

def _format_time(dt):
    return dt.time().strftime("%I:%M%p")
