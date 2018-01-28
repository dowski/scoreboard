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
        control.latch.off()
        for bit in value:
            if bit:
                control.data.on()
            else:
                control.data.off()
            control.clk.off()
            control.clk.on()
        control.latch.on()

if __name__ == '__main__':
    import control
    import time

    display = SingleDigitDisplay(control.right_display)
    display.enable()
    while True:
        for i in xrange(10):
            display.set(i)
            time.sleep(1)
