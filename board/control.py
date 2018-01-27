"""Low-level support for controlling the two digits of the 7-segment display.

"""
from gpiozero import LED


DIGITS = {
#       7-segment pins
#      -----------------
#       8             1
#      -|-------------|-
#       |             |
    0: [1,1,0,1,1,1,1,0], # 0
    1: [1,0,0,0,1,0,0,0], # 1
    2: [0,1,0,1,1,1,0,1], # 2
    3: [1,0,0,1,1,1,0,1], # 3
    4: [1,0,0,0,1,0,1,1], # 4
    5: [1,0,0,1,0,1,1,1], # 5
    6: [1,1,0,1,0,1,1,1], # 6
    7: [1,0,0,0,1,1,0,0], # 7
    8: [1,1,0,1,1,1,1,1], # 8
    9: [1,0,0,0,1,1,1,1], # 9
   -1: [0,0,0,0,0,0,0,1], # err
}

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
