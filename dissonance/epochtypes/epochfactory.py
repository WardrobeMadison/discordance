import h5py

from .spikeepoch import SpikeEpoch
from .wholeepoch import WholeEpoch

def epoch_factory(epochgrp: h5py.Group):
    tracetype = epochgrp.attrs["tracetype"]
    if tracetype == "spiketrace":
        return SpikeEpoch(epochgrp)
    elif tracetype == "wholetrace":
        return WholeEpoch(epochgrp)