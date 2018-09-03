from scoreboard import gamestate
from scoreboard.gamestate import Inning, Score


def test_empty_game_state_is_first_inning_no_balls_strikes_outs_no_score():
    state = gamestate.GameState()
    assert state.inning == Inning.top.of(1)
    assert state.balls == 0
    assert state.strikes == 0
    assert state.outs == 0
    assert state.score == Score(0, 0)

def test_derived_state_is_state_inside_an_inning():
    state = gamestate.GameState(
            Inning.top.of(1), balls=2, strikes=0, outs=1)
    assert state.derived_state is state

def test_derived_state_is_next_half_inning_after_three_outs():
    state = gamestate.GameState(
            Inning.top.of(1), balls=2, strikes=0, outs=3, score=Score(2, 1))
    expected = gamestate.GameState(Inning.bottom.of(1), score=Score(2, 1))
    assert state.derived_state == expected

def test_derived_state_is_no_balls_no_strikes_equivalent_outs_after_three_strikes():
    state = gamestate.GameState(
            Inning.top.of(1), balls=2, strikes=3, outs=2, score=Score(4, 4))
    expected = gamestate.GameState(Inning.top.of(1), outs=2, score=Score(4, 4))
    assert state.derived_state == expected

def test_derived_state_is_no_balls_no_strikes_equivalent_outs_after_four_balls():
    state = gamestate.GameState(
            Inning.top.of(1), balls=4, strikes=2, outs=2)
    expected = gamestate.GameState(Inning.top.of(1), outs=2)
    assert state.derived_state == expected

def test_derived_state_home_team_in_lead_after_top_of_ninth_is_over():
    state = gamestate.GameState(
            Inning.top.of(9),
            balls=2,
            strikes=2,
            outs=3,
            score=Score(home=1, away=0))
    assert state.derived_state.is_over

def test_derived_state_home_team_in_lead_in_end_of_eight_is_not_over():
    state = gamestate.GameState(
            Inning.bottom.of(8),
            balls=2,
            strikes=2,
            outs=3,
            score=Score(home=4, away=2))
    assert not state.derived_state.is_over

def test_derived_state_home_team_takes_lead_in_bottom_of_ninth_is_over():
    state = gamestate.GameState(
            Inning.bottom.of(9),
            balls=2,
            strikes=2,
            outs=1,
            score=Score(home=4, away=2))
    assert state.derived_state.is_over

def test_derived_state_afer_nine_tied_goes_to_extras():
    state = gamestate.GameState(
            Inning.bottom.of(9),
            balls=2,
            strikes=2,
            outs=3,
            score=Score(home=1, away=1))
    expected = gamestate.GameState(
            Inning.top.of(10),
            score=Score(home=1, away=1))
    assert state.derived_state == expected
    assert not state.derived_state.is_over

def test_derived_state_after_away_up_in_top_of_extra_innings_goes_to_bottom():
    state = gamestate.GameState(
            Inning.top.of(10),
            balls=1,
            strikes=0,
            outs=3,
            score=Score(home=1, away=2))
    expected = gamestate.GameState(
            Inning.bottom.of(10),
            score=Score(home=1, away=2))
    assert state.derived_state == expected
    assert not state.derived_state.is_over

def test_derived_state_home_team_losing_after_nine_is_over():
    state = gamestate.GameState(
            Inning.bottom.of(9),
            balls=2,
            strikes=2,
            outs=3,
            score=Score(home=1, away=5))
    assert state.derived_state.is_over

