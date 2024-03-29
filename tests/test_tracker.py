import datetime

from mock import MagicMock, ANY

from scoreboard import tracker
from scoreboard.data import ScheduledGame
from scoreboard.errors import FetchError


def test_creating_GameTracker_succeeds():
    game_tracker = tracker.GameTracker(*get_deps())


def test_track_with_retry_immediate_network_error_reschedules_and_returns():
    team, jobs, mlbapi, display = get_deps()
    mlbapi.get_game_detail.side_effect = FetchError(original=None)

    game_tracker = tracker.GameTracker(team, jobs, mlbapi, display)
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track_with_retry(game)

    jobs.enter.assert_called_with(tracker.RESCHEDULE_DELAY, 0, game_tracker._track_internal, (game, ANY))
    display.set_away_runs.assert_not_called()
    display.set_home_runs.assert_not_called()
    display.set_inning.assert_not_called()


def test_track_with_results_sets_them_on_the_display():
    game_tracker, display, game_details = get_tracker_display_and_details()
    game_details.home_team_name = "Indians"
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    display.set_away_runs.assert_called_with(
        game_details.away_team_runs, is_favorite_team=False)
    display.set_home_runs.assert_called_with(
        game_details.home_team_runs, is_favorite_team=True)
    display.set_inning.assert_called_with(game_details.inning, is_bottom=ANY)
    display.set_inning_state.assert_called_with(
        balls=game_details.balls,
        strikes=game_details.strikes,
        outs=game_details.outs)


def test_track_top_of_inning_handling():
    game_tracker, display, game_details = get_tracker_display_and_details()
    game_details.inning_state = "Top"
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    display.set_inning.assert_called_once_with(
        game_details.inning, is_bottom=False)


def test_track_middle_of_inning_handling():
    game_tracker, display, game_details = get_tracker_display_and_details()
    game_details.inning_state = "Middle"
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    display.set_inning.assert_called_once_with(
        game_details.inning, is_bottom=False)


def test_track_bottom_of_inning_handling():
    game_tracker, display, game_details = get_tracker_display_and_details()
    game_details.inning_state = "Bottom"
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    display.set_inning.assert_called_once_with(
        game_details.inning, is_bottom=True)


def test_track_end_of_inning_handling():
    game_tracker, display, game_details = get_tracker_display_and_details()
    game_details.inning_state = "End"
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    display.set_inning.assert_called_once_with(
        game_details.inning, is_bottom=True)


def test_track_with_results_game_trackable_reschedules():
    team, jobs, mlbapi, display = get_deps()
    game_details = MagicMock(status=tracker.IN_PROGRESS)
    game_details.inning = 5
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(team, jobs, mlbapi, display)
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    jobs.enter.assert_called_with(
        tracker.RESCHEDULE_DELAY, 0, game_tracker._track_internal, (game, None))


def test_track_with_results_manager_challenge_reschedules():
    team, jobs, mlbapi, display = get_deps()
    game_details = MagicMock(status=tracker.CHALLENGE_PREFIX + " whatever")
    game_details.inning = 4
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(team, jobs, mlbapi, display)
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    jobs.enter.assert_called_with(
        tracker.RESCHEDULE_DELAY, 0, game_tracker._track_internal, (game, None))


def test_track_with_results_umpire_review_reschedules():
    team, jobs, mlbapi, display = get_deps()
    game_details = MagicMock(status="Umpire review: whatever")
    game_details.inning = 4
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(team, jobs, mlbapi, display)
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    jobs.enter.assert_called_with(
        tracker.RESCHEDULE_DELAY, 0, game_tracker._track_internal, (game, None))


def test_track_with_results_delay_reschedules():
    team, jobs, mlbapi, display = get_deps()
    game_details = MagicMock(status="Delay: whatever")
    game_details.inning = 4
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(team, jobs, mlbapi, display)
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    jobs.enter.assert_called_with(
        tracker.RESCHEDULE_DELAY, 0, game_tracker._track_internal, (game, None))


def test_track_with_results_delayed_start_reschedules():
    team, jobs, mlbapi, display = get_deps()
    game_details = MagicMock(status="Delayed Start: whatever")
    game_details.inning = None
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(team, jobs, mlbapi, display)
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    jobs.enter.assert_called_with(
        tracker.RESCHEDULE_DELAY, 0, game_tracker._track_internal, (game, None))


def test_track_with_results_pre_game_reschedules():
    team, jobs, mlbapi, display = get_deps()
    game_details = MagicMock(status="Pre-Game")
    game_details.inning = None
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(team, jobs, mlbapi, display)
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    jobs.enter.assert_called_with(
        tracker.RESCHEDULE_DELAY, 0, game_tracker._track_internal, (game, None))


def test_track_with_results_game_not_trackable_doesnt_reschedule():
    team, jobs, mlbapi, display = get_deps()
    game_details = MagicMock(status=tracker.CANCELLED)
    game_details.inning = None
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(team, jobs, mlbapi, display)
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    jobs.enter.assert_not_called()


def test_track_with_results_game_over_shows_final_for_inning():
    team, jobs, mlbapi, display = get_deps()
    game_details = MagicMock(status=tracker.GAME_OVER)
    game_details.inning = 9
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(team, jobs, mlbapi, display)
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    display.set_inning.assert_called_with("F")


def test_track_with_gamestate_is_over_shows_final_for_inning():
    game_tracker, display, game_details = get_tracker_display_and_details()
    game_details.inning = 9
    game_details.inning_state = "End"
    game_details.home_team_runs = 2
    game_details.away_team_runs = 1

    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    display.set_inning.assert_called_with("F")


def test_track_with_gamestate_is_over_clears_runners_on_base():
    game_tracker, display, game_details = get_tracker_display_and_details()
    game_details.inning = 9
    game_details.inning_state = "End"
    game_details.home_team_runs = 2
    game_details.away_team_runs = 1
    game_details.baserunners = (1, 3)

    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    display.set_baserunners.assert_called_with(())


def test_track_with_missing_runs_and_inning_doesnt_fail():
    game_tracker, display, game_details = get_tracker_display_and_details()
    game_details.inning = None
    game_details.home_team_runs = 0
    game_details.away_team_runs = 0
    game = ScheduledGame(
        game_id="foo",
        start_time=datetime.datetime.now(),
        home_team_name="Cleveland Indians",
        away_team_name="Chicago Cubs")
    game_tracker.track(game)

    display.set_inning.assert_called_once_with(None, is_bottom=ANY)
    display.set_away_runs.assert_called_with(0, is_favorite_team=ANY)
    display.set_home_runs.assert_called_with(0, is_favorite_team=ANY)


def get_deps():
    team = "Indians"
    jobs = MagicMock()
    mlbapi = MagicMock()
    display = MagicMock()
    return team, jobs, mlbapi, display


def get_tracker_display_and_details():
    team, jobs, mlbapi, display = get_deps()
    game_details = MagicMock()
    game_details.inning = None
    game_details.home_team_runs = 0
    game_details.away_team_runs = 0
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(team, jobs, mlbapi, display)
    return game_tracker, display, game_details
