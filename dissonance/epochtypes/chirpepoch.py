
from typing import List, Tuple

import numpy as np
from ..funks.psth import calculate_psth
from ..funks import hill
import h5py
from scipy.stats import sem

from .baseepoch import EpochBlock, IEpoch



class ChirpEpoch(IEpoch):

    def __init__(self, epochgrp:h5py.Group):

        super().__init__(epochgrp)
        self.holdingpotential = epochgrp.attrs.get("holdingpotential")
        self.backgroundval = epochgrp.attrs.get("backgroundval")

    @property
    def trace(self):
        vals = self._response_ds[:] 
        return vals

    @property
    def type(self) -> str:
        return "ChirpTrace"

    @property
    def incrementdecrementratio(self):
        ...

class ChirpEpochs(EpochBlock):

    type = "chirpepochs"

    def __init__(self, epochs: List[ChirpEpoch]):
        super().__init__(epochs)
        self.holdingpotential = epochs[0].holdingpotential
        self.backgroundval = epochs[0].backgroundval

    @property
    def trace(self) -> float:
        return np.mean(self.traces, axis=0)
