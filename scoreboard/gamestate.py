"""Code for cleanly representing a baseball game for the scoreboard.

The scoreboard doesn't deal in "middles" or "ends" of innings. Likewise it
doesn't represent 4 balls or 3 strikes or 3 outs. Each of those events should
transition the game state forward to the next batter or next inning,
respectively.

The code in this module models that sort of game state tracking.

"""
import collections


Inning = collections.namedtuple("Inning", ["number", "half"])
Inning.TOP = "Top"
Inning.BOTTOM = "Bottom"


class InningBuilder:
    def __init__(self, half):
        self.half = half

    def of(self, number):
        return Inning(number, self.half)


_top = Inning.top = InningBuilder(Inning.TOP)
_bottom = Inning.bottom = InningBuilder(Inning.BOTTOM)


Score = collections.namedtuple("Score", ["home", "away"])


class GameState(object):
    def __init__(
            self,
            inning=_top.of(1),
            balls=0,
            strikes=0,
            outs=0,
            score=Score(0, 0),
            final=False):
        self.inning = inning
        self.balls = balls
        self.strikes = strikes
        self.outs = outs
        self.score = score
        self.final = final

    def next_inning(self):
        if self.inning.half == Inning.TOP:
            return GameState(
                    inning=_bottom.of(self.inning.number),
                    score=self.score)
        return GameState(
                inning=_top.of(self.inning.number + 1),
                score=self.score)

    def next_batter(self):
        return GameState(inning=self.inning, outs=self.outs, score=self.score)

    @property
    def derived_state(self):
        if self.is_over:
            return GameState(inning=self.inning, score=self.score, final=True)
        if self.outs == 3:
            return self.next_inning()
        if self.strikes == 3 or self.balls == 4:
            return self.next_batter()
        return self

    @property
    def is_over(self):
        return self.final \
                or (self.inning.number >= 9 \
                and self.inning.half == Inning.BOTTOM \
                and self.score.home > self.score.away) \
                or (self.inning.number >= 9 \
                and self.inning.half == Inning.BOTTOM \
                and self.outs == 3 \
                and self.score.away > self.score.home)


    def __eq__(self, other):
        return self.inning == other.inning \
                and self.balls == other.balls \
                and self.strikes == other.strikes \
                and self.outs == other.outs \
                and self.score == other.score

    def __repr__(self):
        return "GameState(%s of %d, balls=%d, strikes=%d, outs=%d)" % (
                self.inning.half,
                self.inning.number,
                self.balls,
                self.strikes,
                self.outs)
