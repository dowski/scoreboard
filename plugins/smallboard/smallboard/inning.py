from .shiftregister import ShiftRegister
from gpiozero import LED

# The key is the number of balls, the value is the bits to set
BALL_SLICES = {
    0: [0,0,0],
    1: [0,0,1],
    2: [0,1,1],
    3: [1,1,1],
}

# The key is the number of strikes/outs, the value is the bits to set
STRIKE_AND_OUT_SLICES = {
    0: [0,0],
    1: [0,1],
    2: [1,1],
}

class InningDisplay(object):
    """Renders important data about the current inning to an LED display.

    The data in question are the balls, strikes and outs count for the current
    inning.

    The display is driven by a shift register.

    """
    def __init__(self, data_pin_num, clock_pin_num, latch_pin_num):
        data = LED(data_pin_num)
        clock = LED(clock_pin_num)
        latch = LED(latch_pin_num)
        self.register = ShiftRegister(data, clock, latch)
        self.balls = 0
        self.strikes = 0
        self.outs = 0

    def update(self):
        bits = [0] * 8
        bits[-3:] = BALL_SLICES[self.balls]
        bits[-5:-3] = STRIKE_AND_OUT_SLICES[self.strikes]
        bits[-7:-5] = STRIKE_AND_OUT_SLICES[self.outs]
        with self.register.latch():
            self.register.shift_out(bits)

    def __repr__(self):
        return "InningDisplay(balls=%d, strikes=%d, outs=%d)" % (
                self.balls, self.strikes, self.outs)


if __name__ == '__main__':
    import random
    inning = InningDisplay(data_pin_num=14, clock_pin_num=18, latch_pin_num=15)
    while True:
        inning.balls = random.randint(0,3)
        inning.strikes = random.randint(0,2)
        inning.outs = random.randint(0,2)
        inning.update()
        print(inning)
        input("press a enter to continue or ctrl-c to quit")
