import time

import control


class Multiplexor(object):
    """Drives a board with two-digit 7-segment displays.

    It supports multiple displays if the board has them connected with
    daisy-chained shift registers.

    To render a two-digit number the code must multiplex between the two
    display digits by setting a single digit to be shown and then quickly
    alternating the cathode pins.

    """
    def __init__(self, display_count, shift_register,
            left_digit_toggle, right_digit_toggle):
        self.display_count = display_count
        self.shift_register = shift_register
        self.left_digit = left_digit_toggle
        self.right_digit = right_digit_toggle
        self.values = [None] * display_count
        self.left_bits = [0] * 8 * display_count
        self.right_bits = [0] * 8 * display_count

    def set(self, display_index, value):
        self.values[display_index] = value
        self.left_bits = []
        self.right_bits = []
        for value in reversed(self.values):
            if value is not None:
                left_digit, right_digit = divmod(value, 10)
                if left_digit == 0:
                    left_digit = None
            else:
                left_digit, right_digit = None, None
            self.left_bits.extend(control.DIGITS[left_digit])
            self.right_bits.extend(control.DIGITS[right_digit])

    def pulse(self):
        with self.shift_register.latch():
            self.shift_register.shift_out(self.right_bits)
        self.right_digit.on()
        time.sleep(0.005)
        self.right_digit.off()

        with self.shift_register.latch():
            self.shift_register.shift_out(self.left_bits)
        self.left_digit.on()
        time.sleep(0.005)
        self.left_digit.off()
