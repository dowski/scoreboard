import time

from . import control


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
        self.right_decimals = [False] * display_count
        self.left_decimals = [False] * display_count
        self.left_bits = [0] * 8 * display_count
        self.right_bits = [0] * 8 * display_count

    def set(self, display_index, value, left_decimal_on, right_decimal_on):
        self.values[display_index] = value
        self.right_decimals[display_index] = right_decimal_on
        self.left_decimals[display_index] = left_decimal_on
        self.left_bits = []
        self.right_bits = []
        for value, left_decimal_on, right_decimal_on in zip(
                reversed(self.values),
                reversed(self.left_decimals),
                reversed(self.right_decimals)):
            if value not in control.SPECIAL_VALUES:
                left_digit, right_digit = divmod(value, 10)
                if left_digit == 0:
                    left_digit = None
            elif value is None:
                left_digit, right_digit = None, None
            elif value == '-':
                left_digit, right_digit = value
            elif value == 'F':
                left_digit, right_digit = None, value
            self.left_bits.extend(
                    control.get_digit_bits(left_digit, left_decimal_on))
            self.right_bits.extend(
                    control.get_digit_bits(right_digit, right_decimal_on))

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
