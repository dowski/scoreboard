DEFAULT_DELAY_SECONDS = 90


class DelayedDisplay:
    """Wraps a display and delays most updates to it.

    The audio broadcasts on the MLB mobile app are delayed when compared to the
    stats that are available via the API. This class exists in an attempt to
    have the contents of the scoreboard more closely match what is being
    announced when listening to games on the app.

    It will delay most data sent to the display by the given delay.
    """
    def __init__(self, jobs, display, delay=DEFAULT_DELAY_SECONDS):
        self.jobs = jobs
        self.display = display
        self.delay = delay

    def on(self):
        self.display.on()

    def off(self):
        self.display.off()

    def set_away_runs(self, runs, is_favorite_team=False):
        self.jobs.enter(self.delay, 0, self.display.set_away_runs, (runs, is_favorite_team))

    def set_home_runs(self, runs, is_favorite_team=False):
        self.jobs.enter(self.delay, 0, self.display.set_home_runs, (runs, is_favorite_team))

    def set_inning(self, inning, is_bottom=False):
        self.jobs.enter(self.delay, 0, self.display.set_inning, (inning, is_bottom))

    def set_inning_state(self, balls, strikes, outs):
        self.jobs.enter(self.delay, 0, self.display.set_inning_state, (balls, strikes, outs))

    def set_baserunners(self, baserunners):
        self.jobs.enter(self.delay, 0, self.display.set_baserunners, (baserunners,))
