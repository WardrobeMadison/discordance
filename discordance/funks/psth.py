import numpy as np
import matplotlib.pyplot as plt

def calculate_psth(epoch, inc=100, outputfile=None) -> np.array:
	#inc = 100 # 10 ms
	x = np.zeros(epoch.values.shape)
	x[epoch.spikes.sp] = 1
	#nbins = epoch.values.shape[0] // inc

	psth = np.fromiter(
		[
			np.sum(x[ii:ii+inc])
			for ii in range(0, epoch.values.shape[0]-1, inc)
		], dtype=float)

	# adjust for baseline
	psth = 100 * (psth - np.mean(psth[:int(epoch.stimtime//100)]))
	return psth
