from typing import List, Tuple

import numpy as np
from ..funks.psth import calculate_psth
from ..funks import hill
from h5py._hl.dataset import Dataset
from scipy.stats import sem

from .baseepoch import DissonanceParams, EpochBlock, IEpoch


def calc_width_at_half_max(values):
    """Width at half max (actually half min since data should be negative"""
    ttp = np.argmin(values)
    halfmax = np.min(values) / 2.0

    start = np.argmax(values < halfmax)
    end = np.argmax(values[ttp:] > halfmax) + ttp

    return end-start, (start,end)


class WholeEpoch(IEpoch):

    def __init__(self, epochpath: str,
                 parameters: DissonanceParams = None,
                 response: Dataset = None,
                 number="0"):

        super().__init__(epochpath, parameters, response, number)
        self._widthathalfmax = None
        self._timetopeak = None
        self._peakamplitude = None
        self._widthrange = None

    @property
    def timetopeak(self) -> float:
        if self._timetopeak is None:
            self._timetopeak  = np.argmin(self.values)
        return self._timetopeak

    @property
    def widthrange(self) -> float:
        if self._widthrange is None:
            # set this property to set range as well
            self.width_at_half_max
        return self._widthrange

    @property
    def peakamplitude(self) -> float:
        if self._peakamplitude is None:
            self._peakamplitude  = np.max(self.values)
        return self._peakamplitude

    @property
    def width_at_half_max(self) -> float:
        if self._widthathalfmax is None:
            self._widthathalfmax, self._widthrange = calc_width_at_half_max(self.values)
        return self._widthathalfmax

    @property
    def type(self) -> str:
        return "WholeTrace"

class WholeEpochs(EpochBlock):

    type = "wholetrace"

    def __init__(self, epochs: List[WholeEpoch], keys):
        super().__init__(epochs, keys)

    @property
    def trace(self) -> float:
        return np.mean(self.traces, axis=1)

    @property 
    def widthathalfmax(self) -> Tuple[float, Tuple[float, float]]:
        # assume it's cell, lightamp, lightmean
        return calc_width_at_half_max(self.trace)

    @property 
    def peakamplitude(self) -> float:
        return np.min(self.trace)

    @property 
    def timetopeak(self) -> float:
        return np.argmin(self.trace)



           
