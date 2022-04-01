from pathlib import Path
import matplotlib.pyplot as plt

from ...epochtypes import SpikeEpoch
from ..spike_detection import TraceSpikeResult

def plt_psth(psth, nbins, outputfile:Path = None):
	fig = plt.subplot()
	plt.grid(True)
	plt.plot(range(0, nbins), psth)
	plt.title("PSTH")
	plt.ylabel("Number of spikes / 10ms")
	plt.xlabel("Bin 10ms increments")
	if outputfile:
		plt.savefig(outputfile, dpi = 600)
	plt.show()

def plt_spikes(epoch:SpikeEpoch, outputfile:Path=None):
	fig = plt.subplot()
	plt.plot(epoch.values)
	plt.grid(True)
	y = epoch.values[epoch.spikes.sp]
	plt.scatter(epoch.spikes.sp, y, marker="x", c="#FFA500")

	plt.title(epoch.startdate)
	plt.ylabel("pA")
	plt.xlabel("10e-4 seconds")

	if outputfile:
		plt.savefig(outputfile, dpi = 600)
	plt.show()