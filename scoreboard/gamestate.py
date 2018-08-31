"""Code for cleanly representing a baseball game for the scoreboard.

The scoreboard doesn't deal in "middles" or "ends" of innings. Likewise it
doesn't represent 4 balls or 3 strikes or 3 outs. Each of those events should
transition the game state forward to the next batter or next inning,
respectively.

The code in this module models that sort of game state tracking.

"""
import collections


Inning = collections.namedtuple("Inning", ["number", "half"])
Inning.TOP = "top"
Inning.BOTTOM = "bottom"

class InningBuilder:
    def __init__(self, half):
        self.half = half

    def of(self, number):
        return Inning(number, self.half)

top = InningBuilder(Inning.TOP)
bottom = InningBuilder(Inning.BOTTOM)

class GameState(object):
    def __init__(self, inning=top.of(1), balls=0, strikes=0, outs=0):
        self.inning = inning
        self.balls = balls
        self.strikes = strikes
        self.outs = outs

    def next_inning(self):
        if self.inning.half == Inning.TOP:
            return GameState(inning=bottom.of(self.inning.number))
        return GameState(inning=top.of(self.inning.number + 1))

    def next_batter(self):
        return GameState(inning=self.inning, outs=self.outs)

    def __eq__(self, other):
        return self.inning == other.inning \
                and self.balls == other.balls \
                and self.strikes == other.strikes \
                and self.outs == other.outs

    def __repr__(self):
        return "GameState(inning=%s, balls=%d, strikes=%d, outs=%d)" % (
                self.inning, self.balls, self.strikes, self.outs)

class GameLog:
    def __init__(self):
        self.entries = [GameState()]

    def add(self, state):
        self.entries.append(state)

    @property
    def last_state(self):
        return self.entries[-1]

    @property
    def derived_state(self):
        last_state = self.entries[-1]
        if last_state.outs == 3:
            return last_state.next_inning()
        if last_state.strikes == 3 or last_state.balls == 4:
            return last_state.next_batter()
        return last_state

