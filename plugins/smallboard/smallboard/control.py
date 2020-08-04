"""Low-level support for controlling the two digits of the 7-segment display.

"""
from gpiozero import LED


DIGITS = {
#       7-segment pins
#      -----------------
#       4 3 2 1 8 7 6 5
#      -|-------------|-
#       |             |
    0: [1,1,1,0,1,1,0,1], # 0
    1: [1,0,0,0,1,0,0,0], # 1
    2: [1,1,0,1,0,1,0,1], # 2
    3: [1,1,0,1,1,0,0,1], # 3
    4: [1,0,1,1,1,0,0,0], # 4
    5: [0,1,1,1,1,0,0,1], # 5
    6: [0,1,1,1,1,1,0,1], # 6
    7: [1,1,0,0,1,0,0,0], # 7
    8: [1,1,1,1,1,1,0,1], # 8
    9: [1,1,1,1,1,0,0,0], # 9
  '-': [0,0,0,1,0,0,0,0], # -
  'F': [0,1,1,1,0,1,0,0], # F
  'd': [1,0,0,1,1,0,0,0], # d - incomplete
 None: [0,0,0,0,0,0,0,0], # blank
}

SPECIAL_VALUES = set(k for k in DIGITS if type(k) is not int)

# The index of the bit in the DIGITS lists representing the decimal point
DECIMAL_INDEX = 6

# Shift register pins
# -------------------

# Toggle this pin `on` to set the bit value 1 and `off` to set 0
data = LED(14)
# Toggling this pin `on` then `off` will shift the shift register by 1 bit
clk = LED(18)
# Togglging this pin `on` then `off` will display the bits set in the shift
# register on the displays.
latch = LED(15)


# Transistor pins
# ---------------

# Each of these pins controls a transistor which are used to switch
# transistors that control the cathode pins of the 7-segment display.
# This way each digit on the dual display can be controled independently.
left_display = LED(23, initial_value=False)
right_display = LED(24, initial_value=False)

# Inning Display Pins
# -------------------
inning_data_pin = 2
inning_latch_pin = 3
inning_clk_pin = 4

def get_digit_bits(value, include_decimal_bit):
    digit_bits = DIGITS[value][:]
    if include_decimal_bit:
        digit_bits[DECIMAL_INDEX] = 1
    return digit_bits
