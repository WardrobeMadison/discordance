import numpy as np
import matplotlib.pyplot as plt

from .charting import plt_psth

def calculate_psth(epoch, plot=False, inc=100, outputfile=None) -> np.array:
	#inc = 100 # 10 ms
	x = np.zeros(epoch.values.shape)
	x[epoch.spikes.sp] = 1
	nbins = epoch.values.shape[0] // inc

	psth = []
	for ii in range(0, epoch.values.shape[0]-1, inc):
		cnt = np.count_nonzero(x[ii:ii+inc])
		psth.append(cnt)

	if plot:
		plt_psth(psth, nbins, outputfile = outputfile)
	return psth