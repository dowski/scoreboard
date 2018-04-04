from mock import MagicMock

from scoreboard import tracker
from scoreboard.mlb import FetchError


def test_creating_GameTracker_succeeds():
    game_tracker = tracker.GameTracker(*get_deps())

def test_track_with_immediate_network_error_reschedules_and_returns():
    jobs, mlbapi, display = get_deps()
    mlbapi.get_game_detail.side_effect = FetchError

    game_tracker = tracker.GameTracker(jobs, mlbapi, display)
    game_tracker.track("foo")

    jobs.enter.assert_called_with(tracker.RESCHEDULE_DELAY, 0, game_tracker.track, ("foo",))
    display.set_top_score.assert_not_called()
    display.set_bottom_score.assert_not_called()
    display.set_inning.assert_not_called()

def test_track_with_results_sets_them_on_the_display():
    jobs, mlbapi, display = get_deps()
    game_details = MagicMock()
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(jobs, mlbapi, display)
    game_tracker.track("foo")

    display.set_top_score.assert_called_with(game_details.away_team_runs)
    display.set_bottom_score.assert_called_with(game_details.home_team_runs)
    display.set_inning.assert_called_with(game_details.inning)

def test_track_with_results_game_trackable_reschedules():
    jobs, mlbapi, display = get_deps()
    game_details = MagicMock(status=tracker.IN_PROGRESS)
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(jobs, mlbapi, display)
    game_tracker.track("foo")

    jobs.enter.assert_called_with(tracker.RESCHEDULE_DELAY, 0, game_tracker.track, ("foo",))

def test_track_with_results_game_not_trackable_doesnt_reschedule():
    jobs, mlbapi, display = get_deps()
    game_details = MagicMock(status=tracker.CANCELLED)
    mlbapi.get_game_detail.return_value = game_details

    game_tracker = tracker.GameTracker(jobs, mlbapi, display)
    game_tracker.track("foo")

    jobs.enter.assert_not_called()

def get_deps():
    jobs = MagicMock()
    mlbapi = MagicMock()
    display = MagicMock()
    return jobs, mlbapi, display
