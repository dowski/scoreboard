import board

class SingleDigitDisplay(object):
	def __init__(self, control_pin):
		self.control_pin = control_pin

	def enable(self):
		self.control_pin.on()
	
	def disable(self):
		self.control_pin.off()
	
	def set(self, n):
		value = board.digits[n]
		for bit in value:
			if bit:
				board.data.on()
			else:
				board.data.off()
			board.clk.on()
			board.clk.off()
		board.latch.on()
		board.latch.off()

if __name__ == '__main__':
	import time
	left = SingleDigitDisplay(board.left_display)
	right = SingleDigitDisplay(board.right_display)

	while True:
		left.set(4)
		left.enable()
		time.sleep(.01)
		left.disable()
		right.set(2)
		right.enable()
		time.sleep(.01)
		right.disable()

