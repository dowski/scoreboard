import threading
import time
import Queue

import control

from .singledigit import SingleDigitDisplay


class TwoDigitDisplay(object):
    """Drives a two-digit 7-segment display board.

    The board has a 7-segment display with common cathode pins. One cathode
    pin controls the left display and the other controls the right.

    To display a two-digit number the code must multiplex between the two
    display digits by setting a single digit to be shown and then quickly
    switching the correct cathode pin on and off.

    """
    def __init__(self):
        self.left = SingleDigitDisplay(control.left_display)
        self.right = SingleDigitDisplay(control.right_display)
        self.commands = Queue.Queue()
        self.render_thread = threading.Thread(target=self._render)

    def enable(self):
        """Prepare the display for use.

        Must be called before any calls to `show`.

        """
        self.render_thread.start()

    def show(self, v):
        """Show a number between 0 and 99 on the display.

        It will be displayed until `show` is called again with another number.

        """
        self.commands.put(('show', v))

    def hide(self):
        """Don't show anything on the display.

        """
        self.commands.put(('hide', None))

    def disable(self):
        """Call this method when you are done with the display instance.

        """
        self.commands.put(('disable', None))
        self.render_thread.join()

    def _render(self):
        command, value = None, None
        while True:
            try:
                command, value = self.commands.get(False)
            except Queue.Empty:
                # run the previous command
                pass
            if command == 'show':
                self._show(value)
            elif command == 'hide':
                self._hide()
            elif command == 'disable':
                break

    def _show(self, n):
        left_digit, right_digit = divmod(n, 10)
        if 0 > left_digit or left_digit > 9:
            self._show_error()
            return
        if left_digit > 0:
            self._show_both(left_digit, right_digit)
        else:
            self._show_right_only(right_digit)

    def _hide(self):
        self.right.disable()
        self.left.disable()

    def _show_right_only(self, n):
        self.right.set(n)
        self.right.enable()
        time.sleep(0.01)
        self.right.disable()

    def _show_both(self, left_n, right_n):
        self.left.set(left_n)
        self.left.enable()
        time.sleep(0.005)
        self.left.disable()
        self.right.set(right_n)
        self.right.enable()
        time.sleep(0.005)
        self.right.disable()

    def _show_error(self):
        self.right.set(-1)
        self.left.set(-1)
        self.right.enable()
        self.left.enable()
        time.sleep(0.01)
        self.right.disable()
        self.left.disable()

