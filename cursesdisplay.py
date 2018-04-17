import curses
import threading
from Queue import Queue

DWIDTH = 7
DHEIGHT = 3

class CursesDisplay():
    def __init__(self):
        self._render_thread = threading.Thread(target=lambda: curses.wrapper(self.app))

    def on(self):
        self._commands = Queue()
        self._render_thread.start()

    def app(self, stdscr):
        y, x = stdscr.getmaxyx()
        hy, hx = y/2, x/2
        qy, qx = hy/2, hx/2
        self.hy, self.hx = hy, hx
        self.qy, self.qx = qy, qx
        self.stdscr = stdscr
        self.stdscr.vline(self.hy-DHEIGHT/2, self.hx-DWIDTH/2, ord("|"), DHEIGHT)
        self.stdscr.vline(self.hy-DHEIGHT/2, self.hx+DWIDTH/2, ord("|"), DHEIGHT)
        self.stdscr.hline(self.hy-DHEIGHT/2, self.hx-DWIDTH/2, ord("-"), DWIDTH)
        self.stdscr.hline(self.hy+DHEIGHT/2, self.hx-DWIDTH/2, ord("-"), DWIDTH)
        self.stdscr.refresh()
        while True:
            command, value = self._commands.get()
            if command == "quit":
                break
            if command == "show":
                self._show(value)
            elif command == "hide":
                self._hide()

    def set_away_runs(self, n, is_favorite_team=False):
        self._commands.put(("show", n))

    def set_home_runs(self, n, is_favorite_team=False):
        pass

    def set_inning(self, n, is_bottom=False):
        pass

    def clear_all(self):
        self._commands.put(("hide", None))

    def _show(self, n):
        self.stdscr.addstr(self.hy, self.hx - 1, "  ")
        nposx = self.hx if 0 < n < 10 else self.hx - 1
        self.stdscr.addstr(self.hy, nposx, str(n) if n >= 0 else "--")
        self.stdscr.refresh()

    def _hide(self):
        self.stdscr.addstr(self.hy, self.hx - 1, "  ")
        self.stdscr.refresh()

    def off(self):
        self._commands.put(("quit", None))
