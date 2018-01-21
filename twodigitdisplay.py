import time

import board

from singledigitdisplay import SingleDigitDisplay


class TwoDigitDisplay(object):
	def __init__(self):
		self.left = SingleDigitDisplay(board.left_display)
		self.right = SingleDigitDisplay(board.right_display)
	
	def show(self, n, duration):
		if n > 99:
			self._show_error(duration)
			return
		left_digit, right_digit = divmod(n, 10)
		if left_digit > 0:
			self._show_both(left_digit, right_digit, duration)
		else:
			self._show_right_only(right_digit, duration)
	
	def _show_right_only(self, n, duration):
		end = time.time() + duration
		while time.time() < end:
			self.right.set(n)
			self.right.enable()
			self.right.disable()
			time.sleep(0.01)
	
	def _show_both(self, left_n, right_n, duration):
		end = time.time() + duration
		while time.time() < end:
			self.left.set(left_n)
			self.left.enable()
			self.left.disable()
			time.sleep(0.01)
			self.right.set(right_n)
			self.right.enable()
			self.right.disable()
			time.sleep(0.01)
	
	def _show_error(self, duration):
		self.right.set(-1)
		self.left.set(-1)
		self.right.enable()
		self.left.enable()
		time.sleep(duration)
		self.right.disable()
		self.left.disable()

if __name__ == '__main__':
	d = TwoDigitDisplay()
	while True:
		for i in xrange(100):
			d.show(i, 1)
