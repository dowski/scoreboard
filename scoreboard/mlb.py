import signal
import urllib2

import mlbgame
from .errors import FetchError


# The number of seconds the code will wait for a response from the MLB API
# before raising a FetchError.
GAME_FETCH_TIMEOUT = 10


class Api(object):
    """A lightweight interface to the MLB API."""

    def get_games(self, date, team):
        """Returns a list of games for a team on a given date.

        The date should be a datetime instance and the team name should be a
        capitalized string name (e.g. "Indians").

        """
        try:
            signal.alarm(GAME_FETCH_TIMEOUT)
            todays_games = mlbgame.day(date.year, date.month, date.day,
                    home=team, away=team)
            signal.alarm(0)
            return todays_games
        except (urllib2.URLError, _Timeout) as e:
            raise FetchError()

    def get_game_detail(self, game_id):
        """Returns detailed information about a game.

        The game_id is a string that can be found in the game_id attribute of
        objects returned from the get_games method.

        """
        try:
            signal.alarm(GAME_FETCH_TIMEOUT)
            game_details = mlbgame.overview(game_id)
            signal.alarm(0)
            return game_details
        except (urllib2.URLError, _Timeout) as e:
            raise FetchError()

    @staticmethod
    def install_alarm_handler():
        """Enables timeout handling when talking to the MLB API.

        This method should be called once at the start of a program to ensure
        timeout handling is correctly configured.

        """
        def handle_alarm(ignored, alsoignored):
            raise _Timeout()
        signal.signal(signal.SIGALRM, handle_alarm)

class _Timeout(Exception):
    pass
