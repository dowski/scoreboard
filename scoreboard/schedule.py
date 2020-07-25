import datetime
import dateutil.tz

from .errors import FetchError


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
        try:
            todays_games = self.mlbapi.get_games(
                    datetime.date.today(), self.team)
        except FetchError as e:
            print(("rescheduling get_games after error fetching "
                    "due to {}").format(e.original_exception))
            self.jobs.enter(TIMEOUT_DELAY, 0, self.run, ())
            return
        print("%d games today" % len(todays_games))
        now = datetime.datetime.now(dateutil.tz.UTC)
        for game in todays_games:
            if game.start_time <= now:
                # game already started
                try:
                    self.mlbapi.get_game_detail(game.game_id)
                    self.tracker.track(game.game_id)
                except FetchError as e:
                    print(("rescheduling get_game_detail after error fetching "
                            "due to {}").format(e.original_exception))
                    self.jobs.enter(TIMEOUT_DELAY, 0, self.run, ())
                    return
            else:
                wait_game = (
                        game.start_time - datetime.datetime.now(
                            dateutil.tz.UTC)).seconds
                print(("Tracking for today's game (%s) will start at "
                        "%s (%d seconds from now)") % (
                                game.game_id, _format_time(game.start_time),
                                wait_game))
                self.jobs.enter(
                        wait_game, 0, self.tracker.track, (game.game_id,))
        # Naive timezone-less datetime instances are used here to check the schedule
        # at 8:00 AM local time the next day.
        next_day = (datetime.datetime.now()
                + datetime.timedelta(days=1)).replace(
                        hour=8, minute=0, second=0, microsecond=0)
        wait_tomorrow = (next_day - datetime.datetime.now()).total_seconds()
        print("Checking tomorrow's schedule at %s (%d seconds from now)" % (
                _format_time(next_day.replace(tzinfo=dateutil.tz.tzlocal())),
                    wait_tomorrow))
        self.jobs.enter(wait_tomorrow, 0, self.run, ())

def _format_time(dt):
    return dt.time().strftime("%I:%M%p")
