import threading
import Queue

import control
from inning import InningDisplay
from multiplexor import Multiplexor
from shiftregister import ShiftRegister


DISPLAY_COUNT = 3
# None indicates that no number segments should be shown and False
# indicates that the right-most decimal should not be lit.
EMPTY_DISPLAY = (None, False)


class DisplayController(object):
    """A threaded interface to a display composed of 7-segment displays.

    """
    def __init__(self):
        self.commands = Queue.Queue()
        shift_register = ShiftRegister(
                control.data, control.clk, control.latch)
        self.multiplexor = Multiplexor(
                DISPLAY_COUNT, shift_register, control.left_display,
                control.right_display)
        self._render_thread = threading.Thread(target = self._mainloop)
        self.values = [EMPTY_DISPLAY] * DISPLAY_COUNT
        self.inning_display = InningDisplay(
                control.inning_data_pin,
                control.inning_clk_pin,
                control.inning_latch_pin)

    def on(self):
        # This update() call is needed to make sure the inning display starts
        # in an "off" state.
        self.inning_display.update()
        self._render_thread.start()

    def off(self):
        self.commands.put(('stop', None))
        self._render_thread.join()

    def clear_all(self):
        self.values = [EMPTY_DISPLAY] * DISPLAY_COUNT
        self.commands.put(('set', list(self.values)))

    def set_inning(self, value, is_bottom=False):
        self.values[0] = (value, is_bottom)
        self.commands.put(('set', list(self.values)))

    def set_away_runs(self, value, is_favorite_team=False):
        self.values[2] = (value, is_favorite_team)
        self.commands.put(('set', list(self.values)))

    def set_home_runs(self, value, is_favorite_team=False):
        self.values[1] = (value, is_favorite_team)
        self.commands.put(('set', list(self.values)))

    def set_inning_state(self, balls, strikes, outs):
        self.inning_display.balls = balls
        self.inning_display.strikes = strikes
        self.inning_display.outs = outs
        self.inning_display.update()

    def _mainloop(self):
        command, values = None, []
        while command != 'stop':
            try:
                command, values = self.commands.get(False)
            except Queue.Empty:
                # pulse the display a show loop
                pass
            if command == 'set':
                for index, (value, right_decimal) in enumerate(values):
                    self.multiplexor.set(index, value,
                            left_decimal_on=False,
                            right_decimal_on=right_decimal)
            self.multiplexor.pulse()

if __name__ == '__main__':
    import time
    from itertools import chain
    dc = DisplayController()
    dc.on()
    try:
        while True:
            for a,b,c in zip(
                    range(100),
                    reversed(range(100)),
                    chain(*zip(range(0,100,2), range(0,100,2)))):
                dc.set_away_runs(a)
                dc.set_home_runs(b)
                dc.set_inning(c)
                time.sleep(0.1)
    finally:
        dc.off()

