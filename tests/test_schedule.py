import datetime
import pytest

import dateutil.tz
from mock import MagicMock, ANY

from scoreboard import schedule
from scoreboard.data import ScheduledGame, GameDetails
from scoreboard.schedule import NEXT_GAME_DELAY
from scoreboard.tracker import GameTracker, IN_PROGRESS, WARMUP, RESCHEDULE_DELAY

TEAM = "Guardians"

NOT_STARTED_GAME_DETAILS = GameDetails(
    inning=None,
    home_team_runs=0,
    away_team_runs=0,
    balls=0,
    strikes=0,
    outs=0,
    status=WARMUP,
    inning_state='top',
    baserunners=())

IN_PROGRESS_GAME_DETAILS = GameDetails(
    inning=1,
    home_team_runs=0,
    away_team_runs=0,
    balls=0,
    strikes=0,
    outs=0,
    status=IN_PROGRESS,
    inning_state='top',
    baserunners=())

FINAL_GAME_DETAILS = GameDetails(
    inning=9,
    home_team_runs=2,
    away_team_runs=0,
    balls=0,
    strikes=0,
    outs=0,
    status=IN_PROGRESS,
    inning_state='bottom',
    baserunners=())


def test_games_in_future_schedules_the_earliest_start_game_upon_running():
    jobs = MagicMock()
    display = MagicMock()
    mlbapi = MagicMock()
    tracker = GameTracker(TEAM, jobs, mlbapi, display)
    now = datetime.datetime.now(dateutil.tz.UTC)
    games = [
        ScheduledGame(game_id="a", start_time=now + datetime.timedelta(minutes=10),
                      home_team_name=TEAM, away_team_name="White Sox"),
        # Setup the second game so it starts sooner
        ScheduledGame(game_id="b", start_time=now + datetime.timedelta(minutes=5),
                      home_team_name=TEAM, away_team_name="White Sox"),
    ]
    mlbapi.get_games.return_value = games
    mlbapi.get_game_detail.return_value = NOT_STARTED_GAME_DETAILS
    scheduler = schedule.GameScheduler(jobs, TEAM, tracker, mlbapi)
    scheduler.run()
    jobs.enter.assert_any_call(ANY, 0, tracker.track_with_retry, (games[1],),
                               {'post_game_callback': scheduler.check_for_additional_game})
    with pytest.raises(AssertionError):
        jobs.enter.assert_any_call(ANY, 0, tracker.track_with_retry, (games[0],))


def test_game_in_progress_gets_tracked_immediately():
    jobs = MagicMock()
    display = MagicMock()
    mlbapi = MagicMock()
    tracker = GameTracker(TEAM, jobs, mlbapi, display)
    now = datetime.datetime.now(dateutil.tz.UTC)
    games = [
        ScheduledGame(game_id="a", start_time=now + datetime.timedelta(minutes=10),
                      home_team_name=TEAM, away_team_name="White Sox"),
        # Setup the second game so it has already started
        ScheduledGame(game_id="b", start_time=now - datetime.timedelta(minutes=5),
                      home_team_name=TEAM, away_team_name="White Sox"),
    ]
    mlbapi.get_games.return_value = games
    mlbapi.get_game_detail.return_value = IN_PROGRESS_GAME_DETAILS
    scheduler = schedule.GameScheduler(jobs, TEAM, tracker, mlbapi)
    scheduler.run()
    jobs.enter.assert_any_call(RESCHEDULE_DELAY, 0, tracker._track_internal,
                               (games[1], scheduler.check_for_additional_game))
    with pytest.raises(AssertionError):
        jobs.enter.assert_any_call(ANY, 0, ANY, (games[0],))


def test_first_game_complete_schedules_next_game():
    jobs = MagicMock()
    display = MagicMock()
    mlbapi = MagicMock()
    tracker = GameTracker(TEAM, jobs, mlbapi, display)
    now = datetime.datetime.now(dateutil.tz.UTC)
    games = [
        ScheduledGame(game_id="a", start_time=now + datetime.timedelta(minutes=10),
                      home_team_name=TEAM, away_team_name="White Sox"),
        # Setup the second game so it has already started
        ScheduledGame(game_id="b", start_time=now - datetime.timedelta(minutes=5),
                      home_team_name=TEAM, away_team_name="White Sox"),
    ]
    mlbapi.get_games.return_value = games

    def _vary_game_detail(*args, **kwargs):
        if args[0] == "a":
            return NOT_STARTED_GAME_DETAILS
        if args[0] == "b":
            return FINAL_GAME_DETAILS
        raise ValueError("unhandled args: %s" % args)

    mlbapi.get_game_detail.side_effect = _vary_game_detail
    scheduler = schedule.GameScheduler(jobs, TEAM, tracker, mlbapi)
    scheduler.run()
    jobs.enter.assert_any_call(ANY, 0, tracker.track_with_retry, (games[0],),
                               {'post_game_callback': scheduler.check_for_additional_game})
    with pytest.raises(AssertionError):
        jobs.enter.assert_any_call(ANY, 0, ANY, (games[1],))


def test_first_game_complete_already_does_not_call_post_game_callback():
    jobs = MagicMock()
    display = MagicMock()
    mlbapi = MagicMock()
    tracker = GameTracker(TEAM, jobs, mlbapi, display)
    now = datetime.datetime.now(dateutil.tz.UTC)
    games = [
        ScheduledGame(game_id="a", start_time=now + datetime.timedelta(minutes=10),
                      home_team_name=TEAM, away_team_name="White Sox"),
        # Setup the second game so it has already started
        ScheduledGame(game_id="b", start_time=now - datetime.timedelta(minutes=5),
                      home_team_name=TEAM, away_team_name="White Sox"),
    ]
    mlbapi.get_games.return_value = games

    def _vary_game_detail(*args, **kwargs):
        if args[0] == "a":
            return NOT_STARTED_GAME_DETAILS
        if args[0] == "b":
            return FINAL_GAME_DETAILS
        raise ValueError("unhandled args: %s" % args)

    mlbapi.get_game_detail.side_effect = _vary_game_detail
    scheduler = schedule.GameScheduler(jobs, TEAM, tracker, mlbapi)
    scheduler.run()
    with pytest.raises(AssertionError):
        jobs.enter.assert_any_call(NEXT_GAME_DELAY, 0, scheduler._track_todays_games, ())


def test_check_for_additional_games_schedules_game_tracking():
    jobs = MagicMock()
    display = MagicMock()
    mlbapi = MagicMock()
    tracker = GameTracker(TEAM, jobs, mlbapi, display)
    scheduler = schedule.GameScheduler(jobs, TEAM, tracker, mlbapi)
    scheduler.check_for_additional_game()
    jobs.enter.assert_any_call(NEXT_GAME_DELAY, 0, scheduler._track_todays_games, ())
