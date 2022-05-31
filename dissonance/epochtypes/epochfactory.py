import h5py

from .spikeepoch import SpikeEpoch
from .wholeepoch import WholeEpoch
from .noiseepoch import NoiseEpoch
from .sacaadeepoch import SaccadeEpoch
from .chirpepoch import ChirpEpoch

def epoch_factory(epochgrp: h5py.Group):
    protocolname = epochgrp.attrs["protocolname"]
    if protocolname == "LedNoiseFamily":
        return NoiseEpoch(epochgrp)
    elif protocolname == "SaccadeTrajectory2":
        return SaccadeEpoch(epochgrp)
    elif protocolname == "ChirpStimulusLED":
        return ChirpEpoch(epochgrp)
    elif protocolname in ["LedPulse", "LedPulseFamily"]:
        tracetype = epochgrp.attrs["tracetype"]
        if tracetype == "spiketrace":
            return SpikeEpoch(epochgrp)
        elif tracetype == "wholetrace":
            return WholeEpoch(epochgrp)
    raise Exception("Trace type not yet specified")