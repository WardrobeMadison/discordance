import numpy as np
import matplotlib.pyplot as plt

def calculate_psth(epoch, inc=100, outputfile=None) -> np.array:
	#inc = 100 # 10 ms
	try:
		x = np.zeros(epoch.traces.shape)
	except:
		x = np.zeros(epoch.trace.shape)
	x[epoch.spikes.sp] = 1
	#nbins = epoch.values.shape[0] // inc

	psth = np.fromiter(
		[
			np.sum(x[ii:ii+inc])
			for ii in range(0, epoch.trace.shape[0], inc)
		], dtype=float)

	# adjust for baseline
	psth = 100 * (psth - np.mean(psth[:int(epoch.stimtime//100)]))
	return psth
