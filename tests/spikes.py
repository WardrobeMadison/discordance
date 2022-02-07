# %%
import numpy as np
import h5py
import matplotlib.pyplot as plt

from discordance.funks.spike_detection import detect_spikes
# %%
path = "tests/data/2020-07-21A.h5"
responsepath = "/experiment-b4de61ea-4027-46ba-bdd3-cc44f85bd683/epochGroups/epochGroup-00aefebb-b806-4e58-8573-a50519ca4783/epochBlocks/edu.wisc.sinhalab.protocols.LedPulse-4923f1e0-ef64-4392-b94d-23fe0ee28f35/epochs/epoch-533b6185-53c2-488b-b1f5-3dfc65b1510c/responses/Amp1-1dce0eb9-ca6c-4ea1-ac01-f64e037124ec"

file = h5py.File(path)
trace = np.fromiter([x[0] for x in file[responsepath]["data"][:]], dtype=float)

# %%
spikeinfo = detect_spikes(trace)

# %%
fig = plt.subplot()
plt.plot(trace)
y = trace[spikeinfo.sp]
plt.grid(True)
plt.scatter(spikeinfo.sp, y, marker="x", c="#FFA500")
plt.show()

# %%
def calculate_psth(trace, spikeinfo, plot=False, inc=100):
	#inc = 100 # 10 ms
	x = np.zeros(trace.shape)
	x[spikeinfo.sp] = 1
	nbins = trace.shape[0] // inc

	psth = []
	for ii in range(0, trace.shape[0]-1, inc):
		cnt = np.count_nonzero(x[ii:ii+inc])
		psth.append(cnt)

	if plot:
		fig = plt.subplot()
		plt.grid(True)
		plt.plot(range(0, nbins), psth)
		plt.title("PSTH")
		plt.ylabel("Number of spikes / 10ms")
		plt.xlabel("Bin 10ms increments")
		plt.show()
	return psth

# %%
psth = calculate_psth(trace, spikeinfo, plot=True)
# %%
