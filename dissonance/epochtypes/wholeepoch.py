from .baseepoch import IEpoch


class WholeEpoch(IEpoch):

	@property
	def timetopeak(self):
		...

	@property
	def width_at_half_max(self):
		...

	@property
	def type(self) -> str:
		return "WholeTrace"
