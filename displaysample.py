import datetime
import sys
import time

import mlbgame

VALID_TARGETS = ["hardware", "software"]
STREAK_START = datetime.date(2017, 8, 24)

try:
    from board.display import DisplayController
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
        display = DisplayController()
    else:
        raise RuntimeError("unhandled target: %s" % target)

    display.on()
    try:
        while True:
            for game in get_streak_games("Indians"):
                indians, opponent = get_game_runs(game, "Indians")
                show_runs(display, indians, opponent)
            # showing -1 actually shows -- on the display
            show_runs(display, -1, -1)
    finally:
        display.off()

def show_runs(display, indians, opponent):
    display.set_away_runs(indians)
    display.set_home_runs(opponent)
    display.set_inning(9)
    time.sleep(2)
    display.clear_all()
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

def get_game_runs(game, team):
    """Returns the Indians' runs first, and opponent second."""
    if team == game.home_team:
        return (game.home_team_runs, game.away_team_runs)
    return (game.away_team_runs, game.home_team_runs)

if __name__ == '__main__':
    main(sys.argv)
