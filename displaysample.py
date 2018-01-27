import datetime
import sys
import time

import mlbgame

VALID_TARGETS = ["hardware", "software"]
STREAK_START = datetime.date(2017, 8, 24)

try:
    from board.twodigit import TwoDigitDisplay
except ImportError:
    HW_AVAILABLE = False
else:
    HW_AVAILABLE = True
from cursesdisplay import CursesDisplay


def main(argv):
    if len(argv) != 2 or sys.argv[1] not in VALID_TARGETS:
        print "usage: python %s %s" % (argv[0], "|".join(VALID_TARGETS))
        sys.exit(1)

    target = sys.argv[1]
    if target == "software":
        display = CursesDisplay()
    elif target == "hardware":
        if not HW_AVAILABLE:
            print "error: hardware not available; is gpiozero installed?"
            sys.exit(1)
        display = TwoDigitDisplay()
    else:
        raise RuntimeError("unhandled target: %s" % target)

    display.enable()
    try:
        while True:
            for game in get_streak_games("Indians"):
                runs = get_team_runs(game, "Indians")
                show_runs(display, runs)
            # showing -1 actually shows -- on the display
            show_runs(display, -1)
    finally:
        display.disable()

def show_runs(display, runs):
    display.show(runs)
    time.sleep(2)
    display.hide()
    time.sleep(.5)

_streak_games_cache = []
def get_streak_games(team):
    if _streak_games_cache:
        return iter(_streak_games_cache)
    return _fetch_and_cache_streak(team)

def _fetch_and_cache_streak(team):
    date = STREAK_START
    temp_cache = []
    while True:
        games = mlbgame.day(date.year, date.month, date.day,
                home=team, away=team)
        date += datetime.timedelta(days=1)
        still_winning = True
        for game in games:
            if game.game_status != "FINAL":
                continue
            still_winning = game.w_team == team
            if not still_winning:
                break
            if not _streak_games_cache:
                temp_cache.append(game)
            yield game
        if not still_winning:
            _streak_games_cache.extend(temp_cache)
            break

def get_team_runs(game, team):
    if team == game.home_team:
        return game.home_team_runs
    return game.away_team_runs

if __name__ == '__main__':
    main(sys.argv)
