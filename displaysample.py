import sys
import time

VALID_TARGETS = ["hardware", "software"]

try:
    from led.twodigit import TwoDigitDisplay
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
            for i in xrange(100):
                display.show(i)
                time.sleep(0.1)
    finally:
        display.disable()

if __name__ == '__main__':
    main(sys.argv)
