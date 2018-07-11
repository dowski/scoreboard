from .errors import FetchError
from .gamestate import GameState, Inning, Score


IN_PROGRESS = "In Progress"
WARMUP = "Warmup"
FINAL = "Final"
CANCELLED = "Cancelled"
DELAYED = "Delayed"
DELAYED_START = "Delayed Start"
REPLAY = "Replay"
REVIEW = "Review"
GAME_OVER = "Game Over"
FINAL = "Final"
CHALLENGE_PREFIX = "Manager challenge:"
UMPIRE_REVIEW_PREFIX = "Umpire review:"
DELAY_PREFIX = "Delay"
TRACKABLE_STATUSES = set([
    IN_PROGRESS, WARMUP, DELAYED, DELAYED_START, REPLAY, REVIEW])
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
            print("rescheduling tracker; error fetching due to {}".format(
                    e.original_exception))
            self.jobs.enter(RESCHEDULE_DELAY, 0, self.track, (game_id,))
            return

        if _is_bottom_of_inning(game_details):
            inning = Inning.bottom.of(_get_safe_number(game_details.inning))
        else:
            inning = Inning.top.of(_get_safe_number(game_details.inning))
        game_state = GameState(
                inning=inning,
                score=Score(
                    home=_get_safe_number(game_details.home_team_runs),
                    away=_get_safe_number(game_details.away_team_runs)),
                balls=_get_safe_number(game_details.balls, 0),
                strikes=_get_safe_number(game_details.strikes, 0),
                outs=_get_safe_number(game_details.outs, 0))

        print("%s: %d, %s: %d, %s of %d (b:%d, s:%d, o:%d)" % (
                game_details.home_team_name,
                game_state.score.home,
                game_details.away_team_name,
                game_state.score.away,
                game_details.inning_state,
                game_state.inning.number,
                game_state.balls,
                game_state.strikes,
                game_state.outs))

        render_state = game_state.derived_state
        self.display.set_away_runs(
                _get_number_or_error_string(render_state.score.away),
                is_favorite_team=self.team == game_details.away_team_name)
        self.display.set_home_runs(
                _get_number_or_error_string(render_state.score.home),
                is_favorite_team=self.team == game_details.home_team_name)
        self.display.set_inning(
                _get_number_or_error_string(render_state.inning.number),
                is_bottom=render_state.inning.half == Inning.BOTTOM)
        self.display.set_inning_state(
                balls=render_state.balls,
                strikes=render_state.strikes,
                outs=render_state.outs)
        if self.is_trackable(render_state, game_details.status):
            self.jobs.enter(RESCHEDULE_DELAY, 0, self.track, (game_id,))
        else:
            if game_details.status in [GAME_OVER, FINAL] \
                    or render_state.is_over:
                self.display.set_inning("F")
            print("game no longer trackable, status:", game_details.status)

    @staticmethod
    def is_trackable(game_state, status):
        return not game_state.is_over and (
                status in TRACKABLE_STATUSES
                or status.startswith(CHALLENGE_PREFIX)
                or status.startswith(UMPIRE_REVIEW_PREFIX)
                or status.startswith(DELAY_PREFIX))

def _is_bottom_of_inning(game_details):
    return game_details.inning_state.lower() in ["bottom", "end"]

def _get_safe_number(value, default=-1):
    return value if value != '' else default

def _get_number_or_error_string(value):
    return value if value >= 0 else '-'
