from .basetrace import ITrace


class WholeTrace(ITrace):

	@property
	def timetopeak(self):
		...

	@property
	def width_at_half_max(self):
		...

	@property
	def type(self) -> str:
		return "WholeTrace"
