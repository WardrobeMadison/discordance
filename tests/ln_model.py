import numpy as np
from pathlib import Path
from dissonance import io, epochtypes, viewer
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy.signal import conolve

ROOTDIR = Path("/home/joe/Projects/DataStore/MappedData")

# LOAD DATA
def load_epochs(folders, tracetype, uncheckedpath = None):
    if uncheckedpath is None:
        unchecked = None
    else:
        unchecked = io.read_unchecked_file(uncheckedpath)

    paths = []
    for fldr in folders:
        paths.extend(
            [	file
                for ii, file in enumerate((ROOTDIR/fldr).glob("*.h5"))
                if ii < 1
            ]
        )

    dr = io.DissonanceReader(paths)
    epochs = dr.to_epochs(tracetype = tracetype)
    epochs = epochtypes.SpikeEpochs(epochs)

    tree = viewer.analysistrees.LedSpikeAnalysis(epochs)
    return tree

# %%
tree = load_epochs(["DR"], "spiketrace")

for ii, cnode in enumerate(tree.leaves):
    if ii == 100:
        node = cnode
        break

epoch = tree.query(cnode)

epoch.trace
epoch.spikes

# stimulus, response, spikes
I = np.array()
R = np.array()
S = np.array()

# calculate spike triggered average
timebefore = 1000
for ii, spike in enumerate(S):
    sta = np.mean(I[min(0,ii-1000):ii])

sta = np.mean(sta)

# calculate generator signal
conv(sta)

# normalize filter

# convolution with normalized filtered

# make continuous spike rate

# sort and bin spikes

# plot linear

# fit sigmoid

# plot nonlinear


