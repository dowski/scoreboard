"""A DisplayController for the new big scoreboard.

The board is powered by a MAX7219 chip and uses the luma.led_matrix library
to interface with the chip.

"""
from .constants import DIGITS, CHARS, BALLS, STRIKES, OUTS, TOP, BOTTOM
from .constants import (
        DISP_HOME, DISP_AWAY, DISP_INNING, DISP_BSO, DISP_BASES, DISP_ARROWS,
        BASES_TO_DISP, DECIMAL)

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas


class DisplayController:
    def __init__(self):
        serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(serial, cascaded=1)
        self.device.contrast(64)
        self.device.hide()
        self._data = {
            'inning': 1,
            'half': TOP,
            'home': 0,
            'away': 0,
            'balls': 0,
            'strikes': 0,
            'outs': 0,
            'baserunners': (),
            'favorite': None,
        }

    def on(self):
        self.device.show()

    def off(self):
        self.device.hide()

    def clear_all(self):
        self.device.clear()

    def set_inning(self, value, is_bottom=False):
        self._data['inning'] = value if value != -1 else None
        if isinstance(value, str) or value == -1:
            self._data['half'] = None
        else:
            self._data['half'] = BOTTOM if is_bottom else TOP
        self._refresh()

    def set_away_runs(self, value, is_favorite_team=False):
        self._data['away'] = value
        if is_favorite_team:
            self._data['favorite'] = 'away'
        self._refresh()

    def set_home_runs(self, value, is_favorite_team=False):
        self._data['home'] = value
        if is_favorite_team:
            self._data['favorite'] = 'home'
        self._refresh()

    def set_inning_state(self, balls, strikes, outs):
        self._data['balls'] = balls
        self._data['strikes'] = strikes
        self._data['outs'] = outs
        self._refresh()

    def set_baserunners(self, bases_with_runners):
        self._data['baserunners'] = tuple(
                BASES_TO_DISP[base] for base in bases_with_runners)
        self._refresh()

    def _refresh(self):
        with canvas(self.device) as draw:
            show_value(
                    draw,
                    self._data['home'],
                    DISP_HOME,
                    highlight=self._data['favorite'] == 'home')
            show_value(
                    draw,
                    self._data['away'],
                    DISP_AWAY,
                    highlight=self._data['favorite'] == 'away')
            show_value(draw, self._data['inning'], DISP_INNING, highlight=False)
            show_inning_indicator(draw, self._data['half'])
            show_balls(draw, self._data['balls'])
            show_strikes(draw, self._data['strikes'])
            show_outs(draw, self._data['outs'])
            show_runners(draw, self._data['baserunners'])


def number_to_digits(number):
    tens, ones = divmod(number, 10)
    return (DIGITS[tens] if tens else [], DIGITS[ones])

def value_to_char(value):
    # sets the value on the right-most display in the pair
    return ([], CHARS[value])

def show_value(canvas, value, displays, highlight):
    if value is None:
        return
    if value in CHARS:
        result = value_to_char(value)
    else:
        result = number_to_digits(value)
    if highlight:
        result = (result[0], result[1] + DECIMAL)
    for display, digits in zip(displays, result):
        for bit in digits:
            canvas.point((display, bit), fill="red")

def show_outs(canvas, number):
    for bit in OUTS[number]:
        canvas.point((DISP_BSO, bit), fill="red")

def show_balls(canvas, number):
    for bit in BALLS[number]:
        canvas.point((DISP_BSO, bit), fill="red")

def show_strikes(canvas, number):
    for bit in STRIKES[number]:
        canvas.point((DISP_BSO, bit), fill="red")

def show_runners(canvas, bases):
    for bit in bases:
        canvas.point((DISP_BASES, bit), fill="red")

def show_inning_indicator(canvas, top_or_bottom):
    if top_or_bottom is not None:
        canvas.point((DISP_ARROWS, top_or_bottom), fill="red")


if __name__ == '__main__':
    import random
    import time

    display = DisplayController()
    display.on()

    game = {
        'inning': 1,
        'half': TOP,
        'home': 0,
        'away': 0,
        'balls': 0,
        'strikes': 0,
        'outs': 0,
        'baserunners': [],
    }
    for inning in range(1, 10):
        game['inning'] = inning
        for half in [TOP, BOTTOM]:
            display.set_inning(inning, half == BOTTOM)
            outs = 0
            while outs < 3:
                strikes = 0
                balls = 0
                while strikes < 3 or balls < 4:
                    display.set_inning_state(balls, strikes, outs)
                    strike = random.choice([True, False])
                    if strike:
                        strikes += 1
                    else:
                        balls += 1
                    display.set_home_runs(game['home'])
                    display.set_away_runs(game['away'])
                    time.sleep(0.5)
                    if strikes == 3:
                        outs += 1
                        break
                    elif balls == 4:
                        break
                if random.random() > 0.92:
                    if game['half'] == TOP:
                        game['away'] += random.randint(1,3)
                    else:
                        game['home'] += random.randint(1,3)
