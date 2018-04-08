from mlb import FetchError


IN_PROGRESS = "In Progress"
WARMUP = "Warmup"
FINAL = "Final"
CANCELLED = "Cancelled"
DELAYED = "Delayed"
DELAYED_START = "Delayed Start"
CHALLENGE = "Manager Challenge"
REPLAY = "Replay"
REVIEW = "Review"
GAME_OVER = "Game Over"
TRACKABLE_STATUSES = set([
    IN_PROGRESS, WARMUP, DELAYED, DELAYED_START, CHALLENGE, REPLAY, REVIEW])
RESCHEDULE_DELAY = 30


class GameTracker(object):
    """Tracks an individual game and renders info on a scoreboard display."""

    def __init__(self, team, jobs, mlbapi, display):
        """Creates a new GameTracker instance.

        The team argument is the name of the team for which we are tracking
        scores. The jobs argument should be a sched.scheduler instance (or
        compatible object). The mlbapi argument should be a mlb.Api instance.
        The display should be a DisplayController.

        """
        self.team = team
        self.jobs = jobs
        self.mlbapi = mlbapi
        self.display = display

    def track(self, game_id):
        """Call this method to track a game.

        The game_id is a string that can be acquired from the objects
        returned from Api.get_games(). They have a game_id attribute on them.

        The game should be in a trackable state (call is_trackable to
        determine that) when calling this method. Otherwise it might
        not track anything.

        While the game is ongoing, this method will reschedule itself every
        30 seconds to update the display with live game data.

        """
        try:
            game_details = self.mlbapi.get_game_detail(game_id)
        except FetchError as e:
            print "rescheduling after error fetching due to", e
            self.jobs.enter(RESCHEDULE_DELAY, 0, self.track, (game_id,))
            return
        print "%s: %d, %s: %d, %s of %d" % (game_details.home_team_name,
                game_details.home_team_runs,
                game_details.away_team_name,
                game_details.away_team_runs,
                game_details.inning_state,
                game_details.inning)

        # Sets the away team score
        self.display.set_top_score(
                _get_safe_number(game_details.away_team_runs),
                is_favorite_team=self.team == game_details.away_team_name)
        # Sets the home team score
        self.display.set_bottom_score(
                _get_safe_number(game_details.home_team_runs),
                is_favorite_team=self.team == game_details.home_team_name)
        # Sets the current inning
        self.display.set_inning(_get_safe_number(game_details.inning),
                is_bottom=_is_bottom_of_inning(game_details))

        if self.is_trackable(game_details.status):
            self.jobs.enter(RESCHEDULE_DELAY, 0, self.track, (game_id,))
        else:
            if game_details.status == GAME_OVER:
                self.display.set_inning("F")
            print "game no longer trackable, status:", game_details.status

    @staticmethod
    def is_trackable(status):
        return status in TRACKABLE_STATUSES

def _is_bottom_of_inning(game_details):
    return game_details.inning_state.lower() in ["bottom", "end"]

def _get_safe_number(value):
    return value if value != '' else 0
