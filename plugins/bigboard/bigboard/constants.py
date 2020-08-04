# Bits in a byte that map to 7-segment display segments
SEG_TOP_LEFT = 1
SEG_BOTTOM_LEFT = 2
SEG_BOTTOM = 3
SEG_BOTTOM_RIGHT = 4
SEG_TOP_RIGHT = 5
SEG_DECIMAL = 7
SEG_TOP = 6
SEG_MIDDLE = 0


# The IDs of the displays on the board
DISP_HOME = (0, 1)
DISP_AWAY = (2, 3)
DISP_INNING = (4, 5)
DISP_BASES = 6
DISP_ARROWS = 6
DISP_BSO = 7


# Numbers that can be shown on the 7-segment displays
ZERO = (SEG_TOP_LEFT, SEG_BOTTOM_LEFT, SEG_BOTTOM, SEG_BOTTOM_RIGHT, SEG_TOP_RIGHT, SEG_TOP)
ONE = (SEG_TOP_RIGHT, SEG_BOTTOM_RIGHT)
TWO = (SEG_TOP, SEG_TOP_RIGHT, SEG_MIDDLE, SEG_BOTTOM_LEFT, SEG_BOTTOM)
THREE = (SEG_TOP, SEG_TOP_RIGHT, SEG_MIDDLE, SEG_BOTTOM_RIGHT, SEG_BOTTOM)
FOUR = (SEG_TOP_LEFT, SEG_TOP_RIGHT, SEG_MIDDLE, SEG_BOTTOM_RIGHT)
FIVE = (SEG_TOP, SEG_TOP_LEFT, SEG_MIDDLE, SEG_BOTTOM_RIGHT, SEG_BOTTOM)
SIX = (SEG_TOP, SEG_TOP_LEFT, SEG_MIDDLE, SEG_BOTTOM_LEFT, SEG_BOTTOM_RIGHT, SEG_BOTTOM)
SEVEN = (SEG_TOP, SEG_TOP_RIGHT, SEG_BOTTOM_RIGHT)
EIGHT = (SEG_TOP_LEFT, SEG_BOTTOM_LEFT, SEG_BOTTOM, SEG_BOTTOM_RIGHT, SEG_TOP_RIGHT, SEG_TOP, SEG_MIDDLE)
NINE = (SEG_TOP, SEG_TOP_RIGHT, SEG_TOP_LEFT, SEG_MIDDLE, SEG_BOTTOM_RIGHT)
DECIMAL = (SEG_DECIMAL,)


# Maps ints to the list of bits required to render them on DISP_HOME, DISP_AWAY and DISP_INNING
DIGITS = {
    0: ZERO,
    1: ONE,
    2: TWO,
    3: THREE,
    4: FOUR,
    5: FIVE,
    6: SIX,
    7: SEVEN,
    8: EIGHT,
    9: NINE,
}

F = (SEG_TOP, SEG_TOP_LEFT, SEG_MIDDLE, SEG_BOTTOM_LEFT)
D = (SEG_TOP_RIGHT, SEG_BOTTOM_RIGHT, SEG_BOTTOM, SEG_BOTTOM_LEFT, SEG_MIDDLE)

CHARS = {
    "F": F,
    "d": D,
}


# Maps numbers of balls to the bits required to render them on DISP_BSO
BALLS = {
    0:[],
    1:[6],
    2:[6,5],
    3:[6,5,4],
    4:[6,5,4],
}


# Maps numbers of strikes to the bits required to render them on DISP_BSO
STRIKES = {
    0:[],
    1: [3],
    2: [3,2],
    3: [3,2],
}


# Maps numbers of outs to the bits required to render them on DISP_BSO
OUTS = {
    0:[],
    1: [1],
    2: [1,0],
    3: [1,0],
}

# Bits that represent the bases on DISP_BASES
HOME = 5
FIRST = 2
SECOND = 4
THIRD = 0

BASES_TO_DISP = {
    1: FIRST,
    2: SECOND,
    3: THIRD,
}

# Bits that represent the top/bottom indicator on DISP_ARROWS
TOP = 7
BOTTOM = 3

