from typing import List, Dict, Tuple

import numpy as np
from ..funks.psth import calculate_psth
import h5py

from .baseepoch import EpochBlock, IEpoch


class SpikeEpoch(IEpoch):

    def __init__(self, epochgrp: h5py.Group):
        super().__init__(epochgrp)
        self._spikegrp = epochgrp["Spikes"]
        self._psth = None

    @property
    def spikes(self) -> np.array:
        return np.array(self._spikegrp[:], dtype=int)

    @property
    def psth(self) -> np.array:
        if self._psth is None:
            self._psth = calculate_psth(self)
        return self._psth

    @property
    def timetopeak(self) -> np.array:
        rng = self.peak_window_range
        return rng[0]//100 + np.argmax(self.psth[rng[0]//100:rng[1]//100])

    @property
    def peakamplitude(self) -> np.array:
        rng = self.peak_window_range
        return np.max(self.psth[rng[0]//100:rng[1]//100])

    @property
    def type(self) -> str:
        return "spiketrace"
        
    @property
    def params(self) -> Dict:
        #"cellname",
        #"startdate",
        #"celltype",
        #"genotype",
        #"protocolname",
        #"enddate",
        #"interpulseinterval",
        #"led",
        #"lightamplitude",
        #"lightmean",
        #"pretime",
        #"stimtime",
        #"samplerate",
        #"tailtime"]

        paramdict = super().params
        params = ["peakamplitude", "timetopeak"]
        for param in params:
            paramdict[param] = getattr(self, param)

        return paramdict

class SpikeEpochs(EpochBlock):

    type = "spiketrace"

    def __init__(self, traces: List[SpikeEpoch]):
        super().__init__(traces)
        self._psth: np.array = None
        self._psths: np.array = None
        self._hillfit:np.array = None
        self.rng = traces[0].peak_window_range

    @property
    def psth(self):
        inc = 100
        if self._psth is None:
            self._psth = np.mean(self.psths, axis=0)
        return self._psth

    @property
    def psths(self) -> np.array:
        inc = 100
        if self._psths is None:
            self._psths = []
            for trace in self._epochs:
                if len(trace.psth) > 0 and trace.psth is not None:
                    cpsth = np.pad(
                        trace.psth, (0, int(self.trace_len // inc - len(trace.psth))))
                    self._psths.append(cpsth)
        return np.array(self._psths, dtype=float)

    @property
    def timetopeak(self) -> np.array:
        return self.rng[0]//100 + np.argmax(self.psth[self.rng[0]//100:self.rng[1]//100])

    @property
    def peakamplitude(self) -> np.array:
        return np.max(self.psth[self.rng[0]//100:self.rng[1]//100])
