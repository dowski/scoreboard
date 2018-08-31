from scoreboard import gamestate

def test_empty_log_last_state_is_first_inning_no_balls_strikes_outs():
    log = gamestate.GameLog()
    assert log.last_state.inning == gamestate.top.of(1)
    assert log.last_state.balls == 0
    assert log.last_state.strikes == 0
    assert log.last_state.outs == 0

def test_adding_state_to_log_updates_last_state():
    log = gamestate.GameLog()
    new_state = gamestate.GameState(
            gamestate.top.of(1), balls=2, strikes=0, outs=1)
    log.add(new_state)
    assert log.last_state is new_state

def test_derived_state_is_last_state_inside_an_inning():
    log = gamestate.GameLog()
    new_state = gamestate.GameState(
            gamestate.top.of(1), balls=2, strikes=0, outs=1)
    log.add(new_state)
    assert log.derived_state is new_state

def test_derived_state_is_next_half_inning_after_three_outs():
    log = gamestate.GameLog()
    new_state = gamestate.GameState(
            gamestate.top.of(1), balls=2, strikes=0, outs=3)
    log.add(new_state)
    expected = gamestate.GameState(gamestate.bottom.of(1))
    assert log.derived_state == expected

def test_derived_state_is_no_balls_no_strikes_equivalent_outs_after_three_strikes():
    log = gamestate.GameLog()
    new_state = gamestate.GameState(
            gamestate.top.of(1), balls=2, strikes=3, outs=2)
    log.add(new_state)
    expected = gamestate.GameState(gamestate.top.of(1), outs=2)
    assert log.derived_state == expected

def test_derived_state_is_no_balls_no_strikes_equivalent_outs_after_four_balls():
    log = gamestate.GameLog()
    new_state = gamestate.GameState(
            gamestate.top.of(1), balls=4, strikes=2, outs=2)
    log.add(new_state)
    expected = gamestate.GameState(gamestate.top.of(1), outs=2)
    assert log.derived_state == expected
