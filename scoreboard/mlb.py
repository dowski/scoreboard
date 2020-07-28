import dateutil.parser
import signal

try:
    from urllib2 import URLError
except ImportError:
    from urllib.error import URLError

from .errors import FetchError
from .data import ScheduledGame, GameDetails


# The number of seconds the code will wait for a response from the MLB API
# before raising a FetchError.
GAME_FETCH_TIMEOUT = 10
BASE_ORD_TO_NUMBER = {
    "first": 1,
    "second": 2,
    "third": 3
}


class Api(object):
    """A lightweight interface to the MLB API."""

    def get_games(self, date, team):
        """Returns a list of games for a team on a given date.

        The date should be a datetime instance and the team name should be a
        capitalized string name (e.g. "Indians").

        """
        import mlbgame
        try:
            signal.alarm(GAME_FETCH_TIMEOUT)
            raw_games = mlbgame.day(date.year, date.month, date.day,
                    home=team, away=team)
            todays_games = []
            for game in raw_games:
                # hack the start time until my PR is accepted
                year, month, day = game.game_id.split('_')[:3]
                game_start_date = "/".join([year, month, day])
                start_time = datetime.datetime.strptime(
                       " ".join([game_start_date,
                            game.game_start_time.replace(' ', '')]),
                       "%Y/%m/%d %I:%M%p")
                game.start_time = start_time
                todays_games.append(game)
            return todays_games
        except (URLError, _Timeout, ValueError) as e:
            # mlbgame returns ValueError for any HTTPError, so we treat it as
            # a retryable error here
            raise FetchError(e)
        finally:
            signal.alarm(0)

    def get_game_detail(self, game_id):
        """Returns detailed information about a game.

        The game_id is a string that can be found in the game_id attribute of
        objects returned from the get_games method.

        """
        import mlbgame
        try:
            signal.alarm(GAME_FETCH_TIMEOUT)
            game_details = mlbgame.overview(game_id)
            return game_details
        except (URLError, _Timeout, ValueError) as e:
            # mlbgame returns ValueError for any HTTPError, so we treat it as
            # a retryable error here
            raise FetchError(e)
        finally:
            signal.alarm(0)

    @staticmethod
    def install_alarm_handler():
        """Enables timeout handling when talking to the MLB API.

        This method should be called once at the start of a program to ensure
        timeout handling is correctly configured.

        """
        def handle_alarm(ignored, alsoignored):
            raise _Timeout()
        signal.signal(signal.SIGALRM, handle_alarm)

class Api2:
    def get_games(self, date, team_name):
        """Returns a list of games for a team on a given date.

        The date should be a datetime instance and the team name should be a
        capitalized string name (e.g. "Indians").

        """
        import statsapi
        response = statsapi.get('teams', {'sportId':1, 'leagueIds':'103, 104'})
        for team in response['teams']:
            if team['teamName'] == team_name:
                team_id = team['id']
                break
        else:
            raise RuntimeError("team not found:" + team_name)

        scheduled_games = []
        try:
            signal.alarm(GAME_FETCH_TIMEOUT)
            response = statsapi.get('schedule',
                    {'sportId':1, 'teamId':team_id, 'date':date.isoformat()})
            if not response['dates']:
                return []
            for gamedate in response['dates']:
                for game in gamedate['games']:
                    home_team_name=game['teams']['home']['team']['name']
                    away_team_name=game['teams']['away']['team']['name']
                    scheduled_games.append(
                            ScheduledGame(
                                game_id=game['gamePk'],
                                start_time=dateutil.parser.isoparse(
                                    game['gameDate']),
                                home_team_name=home_team_name,
                                away_team_name=away_team_name))

        except (URLError, _Timeout) as e:
            raise FetchError(e)
        finally:
            signal.alarm(0)
        return scheduled_games

    def get_game_detail(self, game_id):
        """Returns detailed information about a game.

        The game_id is a string that can be found in the game_id attribute of
        objects returned from the get_games method.

        """
        import statsapi
        try:
            signal.alarm(GAME_FETCH_TIMEOUT)
            response = statsapi.get('game', {'gamePk':game_id, 'fields':"gameData,teams,teamName,status,detailedState,liveData,linescore,home,away,runs,hits,errors,offense,outs,balls,strikes,first,second,third,currentInning,inningState"})
            gamedata = response['gameData']
            linescore = response['liveData']['linescore']
            return GameDetails(
                    inning = linescore.get('currentInning', None),
                    home_team_runs = linescore['teams']['home'].get('runs', 0),
                    away_team_runs = linescore['teams']['away'].get('runs', 0),
                    balls = linescore.get('balls', 0),
                    strikes = linescore.get('strikes', 0),
                    outs = linescore.get('outs', 0),
                    status = gamedata['status']['detailedState'],
                    inning_state = linescore.get('inningState', 'top'),
                    baserunners = tuple(
                        BASE_ORD_TO_NUMBER[v]
                        for v in linescore['offense'].keys()))
        except (URLError, _Timeout) as e:
            raise FetchError(e)
        finally:
            signal.alarm(0)

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
