import curses
import itertools
import time

# The 7-segment display is 13 characters wide at its widest point
WIDTH = 13
# A padding value - not chosen for a specific reason
PADDING = 1
# The height of the display
HEIGHT = 11
# Width and height of the display area - should be big enough to hold
# two of the 7-segment digits side-by-side.
DWIDTH = PADDING + WIDTH + PADDING + WIDTH + PADDING
DHEIGHT = PADDING + HEIGHT + PADDING

# Reads the full 7-segment ASCII art into one long
# string with no newlines.
full = open('full.ascii').read().replace('\n', '')

# This maps various values to the corresponding characters that make up
# each of the segments of the display. For instance, to show the number
# 1 you'd want to show all of the characters in the `full` string above
# that have a corresponding 2 or 5 value in the `full_map` below. 9
# represents a value that will never be displayed.
full_map = [
    9,9,0,0,0,0,0,0,9,9,9,9,9,
    9,1,9,9,9,9,9,9,2,9,9,9,9,
    1,1,1,9,9,9,9,2,2,2,9,9,9,
    1,1,1,9,9,9,9,2,2,2,9,9,9,
    9,1,9,9,9,9,9,9,2,9,9,9,9,
    9,9,3,3,3,3,3,3,9,9,9,9,9,
    9,4,9,9,9,9,9,9,5,9,9,9,9,
    4,4,4,9,9,9,9,5,5,5,9,9,9,
    4,4,4,9,9,9,9,5,5,5,9,9,9,
    9,4,9,9,9,9,9,9,5,9,9,9,9,
    9,9,6,6,6,6,6,6,9,9,7,7,7,
    ]


# default pin config
#  0
# 1 2
#  3
# 4 5
#  6 7

DEFAULT_DIGIT_BITS = {
    0:[1,1,1,0,1,1,1,0],
    1:[0,0,1,0,0,1,0,0],
    2:[1,0,1,1,1,0,1,0],
    3:[1,0,1,1,0,1,1,0],
    4:[0,1,1,1,0,1,0,0],
    5:[1,1,0,1,0,1,1,0],
    6:[1,1,0,1,1,1,1,0],
    7:[1,0,1,0,0,1,0,0],
    8:[1,1,1,1,1,1,1,0],
    9:[1,1,1,1,0,1,0,0],
  '-':[0,0,1,0,0,1,0,0],
  'F':[0,0,1,0,0,1,0,0],
}

def get_bits_for_digit(digit):
    return DEFAULT_DIGIT_BITS[digit]

def pinmap(bits):
    pins = []
    for i, value in enumerate(bits):
        if value:
            pins.append(i)
    return pins

def render(pins):
    output = []
    for i, (pin, char) in enumerate(zip(full_map, full)):
        if i % WIDTH == 0:
            line = []
            output.append(line)
        line.append(char if pin in pins else ' ')
    return "\n".join("".join(line) for line in output)

def app(stdscr):
    stdscr.nodelay(1)
    y, x = stdscr.getmaxyx()
    w = stdscr.subwin(DHEIGHT, DWIDTH, y / 2 - DHEIGHT / 2, x / 2 - DWIDTH / 2)
    w.box()
    w.refresh()
    for num in itertools.cycle(range(10)):
        cy = 1
        for line in render(pinmap(get_bits_for_digit(num))).split('\n'):
            w.move(cy, 1)
            w.addstr(line)
            w.addstr(line)
            w.refresh()
            cy += 1
        time.sleep(.25)
        if stdscr.getch() != -1:
            break

if __name__ == '__main__':
    curses.wrapper(app)
