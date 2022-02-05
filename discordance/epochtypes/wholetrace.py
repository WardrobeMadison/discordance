from .basetrace import BaseTrace


class WholeTrace(BaseTrace):

	type = "WholeTrace"

	@property
	def timetopeak(self):
		...

	@property
	def width_at_half_max(self):
		...
