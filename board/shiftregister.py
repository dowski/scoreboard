from contextlib import contextmanager


class ShiftRegister(object):
    """Provides an interface to an output shift register.

    It supports multiple shift registers if they are daisy chained together.
    It is up to the consumer of the class to shift the correct number of bits
    out to send to the connected devices.

    """
    def __init__(self, data_pin, clock_pin, latch_pin):
        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.latch_pin = latch_pin

    @contextmanager
    def latch(self):
        self.latch_pin.off()
        yield self
        self.latch_pin.on()

    def shift_out(self, data):
        for bit in data:
            self.data_pin.on() if bit else self.data_pin.off()
            self.clock_pin.off()
            self.clock_pin.on()

if __name__ == '__main__':
    import control

    sr = ShiftRegister(control.data, control.clk, control.latch)
    with sr.latch():
        sr.shift_out([1] * 16)
    control.left_display.on()
    control.right_display.on()
    raw_input('press enter')

