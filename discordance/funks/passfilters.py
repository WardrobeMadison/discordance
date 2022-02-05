"""
Band pass filters
"""
import numpy as np
from scipy import fft

def low_pass_filter(X:np.array, F:np.array, dt:float) -> np.array:
	"""
	Filter to cut out high freqnecies about X for cutoff F.

	X    := nd array of signal data
	F    := cutoff frequency
	dt   := sampling interval in seconds.
	"""
	L = X.shape[0]
	if L == 1:
		L = X.shape[1] 
	
	# dt * l := step size in seconds
	# F := cutoff frequency
	# df : index for cut off
	df = round(F * dt * L)

	trans = fft.fft(X)
	trans[df:-df] = 0
	xfilt = fft.ifft(trans).real

	return xfilt

def high_pass_filter(X:np.array, F:np.array, dt:float) -> np.array:
	"""
	Filter to cut out low freqnecies about X for cutoff F.

	X    := nd array of signal data
	F    := cutoff frequency
	dt   := sampling interval in seconds.
	"""
	L = X.shape[0]
	if L == 1:
		L = X.shape[1] 

	df = round(F * dt * L)

	fft_data = fft.fft(X)

	fft_data[0:df] = 0
	fft_data[-df:] = 0

	xfilt = fft.ifft(fft_data, n=None, axis=-1).real

	return xfilt