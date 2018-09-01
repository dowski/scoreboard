from scoreboard import gamestate


Inning = gamestate.Inning


def test_empty_game_state_is_first_inning_no_balls_strikes_outs():
    state = gamestate.GameState()
    assert state.inning == Inning.top.of(1)
    assert state.balls == 0
    assert state.strikes == 0
    assert state.outs == 0

def test_derived_state_is_state_inside_an_inning():
    state = gamestate.GameState(
            Inning.top.of(1), balls=2, strikes=0, outs=1)
    assert state.derived_state is state

def test_derived_state_is_next_half_inning_after_three_outs():
    state = gamestate.GameState(
            Inning.top.of(1), balls=2, strikes=0, outs=3)
    expected = gamestate.GameState(Inning.bottom.of(1))
    assert state.derived_state == expected

def test_derived_state_is_no_balls_no_strikes_equivalent_outs_after_three_strikes():
    state = gamestate.GameState(
            Inning.top.of(1), balls=2, strikes=3, outs=2)
    expected = gamestate.GameState(Inning.top.of(1), outs=2)
    assert state.derived_state == expected

def test_derived_state_is_no_balls_no_strikes_equivalent_outs_after_four_balls():
    state = gamestate.GameState(
            Inning.top.of(1), balls=4, strikes=2, outs=2)
    expected = gamestate.GameState(Inning.top.of(1), outs=2)
    assert state.derived_state == expected
