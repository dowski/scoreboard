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
CHALLENGE_PREFIX = "Manager challenge"
UMPIRE_REVIEW_PREFIX = "Umpire review"
DELAY_PREFIX = "Delay"
TRACKABLE_STATUSES = {IN_PROGRESS, WARMUP, DELAYED, DELAYED_START, REPLAY, REVIEW}
RESCHEDULE_DELAY = 10


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

    def track(self, scheduled_game, post_game_callback=None):
        """Call this method to track a game.

        The scheduled_game is an object that can be acquired calling
        Api.get_games(). They have a game_id attribute on them.

        While the game is ongoing, this method will reschedule itself every
        RESCHEDULE_DELAY seconds to update the display with live game data.

        Callers should be ready to handle a FetchError and possibly reschedule
        a call to this method if one occurs.

        Returns True if the game is trackable, False if it is not (typically
        the game is over or postponed or something).
        """
        return self._track_internal(scheduled_game, post_game_callback, internal_tracking=False)

    def track_with_retry(self, scheduled_game, post_game_callback=None):
        """Like track, but will retry on a network error.

        Doesn't raise FetchError, so you can't know if it failed or not - it
        will simply keep retrying.

        """
        return self._track_internal(scheduled_game, post_game_callback, internal_tracking=True)

    def _track_internal(self, scheduled_game, post_game_callback, internal_tracking=True):
        try:
            game_details = self.mlbapi.get_game_detail(scheduled_game.game_id)
        except FetchError as e:
            if not internal_tracking:
                raise e
            print("rescheduling GameTracker; error fetching due to {}".format(
                e.original_exception))
            self.jobs.enter(RESCHEDULE_DELAY, 0, self._track_internal, (scheduled_game, post_game_callback))
            # Assume the game is trackable until we know otherwise
            return True

        if _is_bottom_of_inning(game_details):
            inning = Inning.bottom.of(game_details.inning)
        else:
            inning = Inning.top.of(game_details.inning)
        game_state = GameState(
            inning=inning,
            score=Score(
                home=_get_safe_number(game_details.home_team_runs),
                away=_get_safe_number(game_details.away_team_runs)),
            balls=_get_safe_number(game_details.balls, 0),
            strikes=_get_safe_number(game_details.strikes, 0),
            outs=_get_safe_number(game_details.outs, 0))

        print("%s: %d, %s: %d, %s of %s (b:%d, s:%d, o:%d, runners:%r)" % (
            scheduled_game.home_team_name,
            game_state.score.home,
            scheduled_game.away_team_name,
            game_state.score.away,
            game_details.inning_state,
            game_state.inning.number,
            game_state.balls,
            game_state.strikes,
            game_state.outs,
            game_details.baserunners))

        render_state = game_state.derived_state
        self.display.set_away_runs(
            render_state.score.away,
            is_favorite_team=self.team in scheduled_game.away_team_name)
        self.display.set_home_runs(
            render_state.score.home,
            is_favorite_team=self.team in scheduled_game.home_team_name)
        self.display.set_inning(
            render_state.inning.number,
            is_bottom=render_state.inning.half == Inning.BOTTOM)
        self.display.set_inning_state(
            balls=render_state.balls,
            strikes=render_state.strikes,
            outs=render_state.outs)
        self.display.set_baserunners(game_details.baserunners)
        if self.is_trackable(render_state, game_details.status):
            self.jobs.enter(RESCHEDULE_DELAY, 0, self._track_internal, (scheduled_game, post_game_callback))
            return True
        if game_details.status in [GAME_OVER, FINAL] \
                or render_state.is_over:
            self.display.set_inning("F")
            self.display.set_baserunners(())
        print("game no longer trackable, status:", game_details.status)
        if internal_tracking and post_game_callback:
            post_game_callback()
        return False

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
