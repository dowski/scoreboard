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

    @property
    def derived_state(self):
        if self.outs == 3:
            return self.next_inning()
        if self.strikes == 3 or self.balls == 4:
            return self.next_batter()
        return self

    def __eq__(self, other):
        return self.inning == other.inning \
                and self.balls == other.balls \
                and self.strikes == other.strikes \
                and self.outs == other.outs

    def __repr__(self):
        return "GameState(inning=%s, balls=%d, strikes=%d, outs=%d)" % (
                self.inning, self.balls, self.strikes, self.outs)
