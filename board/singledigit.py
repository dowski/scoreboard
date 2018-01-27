import control


class SingleDigitDisplay(object):
    def __init__(self, control_pin):
        self.control_pin = control_pin

    def enable(self):
        self.control_pin.on()

    def disable(self):
        self.control_pin.off()

    def set(self, n):
        value = control.DIGITS[n]
        for bit in value:
            if bit:
                control.data.on()
            else:
                control.data.off()
            control.clk.on()
            control.clk.off()
        control.latch.on()
        control.latch.off()

if __name__ == '__main__':
    import control
    import time

    left = SingleDigitDisplay(control.left_display)
    right = SingleDigitDisplay(control.right_display)

    while True:
        left.set(4)
        left.enable()
        time.sleep(.01)
        left.disable()
        right.set(2)
        right.enable()
        time.sleep(.01)
        right.disable()

