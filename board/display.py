import threading
import Queue

import control
from multiplexor import Multiplexor
from shiftregister import ShiftRegister


class DisplayController(object):
    """A threaded interface to a display composed of 7-segment displays.

    """
    def __init__(self):
        self.commands = Queue.Queue()
        shift_register = ShiftRegister(control.data, control.clk, control.latch)
        self.multiplexor = Multiplexor(
                2, shift_register, control.left_display, control.right_display)
        self._render_thread = threading.Thread(target = self._mainloop)
        self.values = [None, None]

    def on(self):
        self._render_thread.start()

    def off(self):
        self.commands.put(('stop', None))
        self._render_thread.join()

    def clear_all(self):
        self.values = [None, None]
        self.commands.put(('set', list(self.values)))

    def set_left(self, value):
        self.values[0] = value
        self.commands.put(('set', list(self.values)))

    def set_right(self, value):
        self.values[1] = value
        self.commands.put(('set', list(self.values)))

    def _mainloop(self):
        command, values = None, []
        while command != 'stop':
            try:
                command, values = self.commands.get(False)
            except Queue.Empty:
                # pulse the display a show loop
                pass
            if command == 'set':
                for index, value in enumerate(values):
                    self.multiplexor.set(index, value)
            self.multiplexor.pulse()

if __name__ == '__main__':
    import time
    dc = DisplayController()
    dc.on()
    try:
        for a,b in zip(range(100), reversed(range(100))):
            dc.set_left(a)
            dc.set_right(b)
            time.sleep(0.1)
    finally:
        dc.off()

