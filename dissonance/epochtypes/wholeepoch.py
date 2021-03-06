from typing import List, Tuple

import numpy as np
from ..funks.psth import calculate_psth
from ..funks import hill
import h5py
from scipy.stats import sem

from .baseepoch import EpochBlock, IEpoch


def calc_width_at_half_max(values, holdingpotential):
    """Width at half max (actually half min since data should be negative"""
    if holdingpotential == "inhibition":
        ttp = np.argmax(values)
        halfmax = np.max(values) / 2.0
    else:
        ttp = np.argmin(values)
        halfmax = np.min(values) / 2.0

    if halfmax < 0:
        start = ttp - np.argmax(values[ttp::-1] > halfmax)
        end = np.argmax(values[ttp:] > halfmax) + ttp
    else:
        start = ttp - np.argmax(values[:ttp:-1] < halfmax)
        end = np.argmax(values[ttp:] < halfmax) + ttp

    return end-start, (int(start),int(end))


class WholeEpoch(IEpoch):

    def __init__(self, epochgrp:h5py.Group):

        super().__init__(epochgrp)
        self.holdingpotential = epochgrp.attrs.get("holdingpotential")
        self.backgroundval = epochgrp.attrs.get("backgroundval")
        self._widthathalfmax = None
        self._timetopeak = None
        self._peakamplitude = None
        self._widthrange = None

    @property
    def trace(self):
        vals = self._response_ds[:] 
        return vals - np.mean(vals[:int(self.pretime)])

    @property
    def timetopeak(self) -> float:
        if self._timetopeak is None:
            if self.holdingpotential == "inhibition":
                self._timetopeak  = np.argmax(self.trace)
            else: 
                self._timetopeak  = np.argmin(self.trace)
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
            if self.holdingpotential == "inhibition":
                self._peakamplitude  = np.max(self.trace)
            else: 
                self._peakamplitude  = np.min(self.trace)
        return self._peakamplitude

    @property
    def width_at_half_max(self) -> float:
        if self._widthathalfmax is None:
            self._widthathalfmax, self._widthrange = calc_width_at_half_max(self.trace, self.holdingpotential)
        return self._widthathalfmax

    @property
    def type(self) -> str:
        return "WholeTrace"

class WholeEpochs(EpochBlock):

    type = "wholetrace"

    def __init__(self, epochs: List[WholeEpoch]):
        super().__init__(epochs)
        self.holdingpotential = epochs[0].holdingpotential
        self.backgroundval = epochs[0].backgroundval
        self._widthathalfmax = None
        self._widthrange = None

    @property
    def trace(self) -> float:
        return np.mean(self.traces, axis=0)

    @property
    def widthrange(self) -> float:
        if self._widthrange is None:
            # set this property to set range as well
            self.width_at_half_max
        return self._widthrange

    @property
    def width_at_half_max(self) -> float:
        if self._widthathalfmax is None:
            self._widthathalfmax, self._widthrange = calc_width_at_half_max(self.trace, self.holdingpotential)
        return self._widthathalfmax

    @property 
    def peakamplitude(self) -> float:
        if self.holdingpotential == "inhibition":
            self._peakamplitude  = np.max(self.trace)
        else: 
            self._peakamplitude  = np.min(self.trace)
        return self._peakamplitude

    @property 
    def timetopeak(self) -> float:
        if self.holdingpotential == "inhibition":
            self._timetopeak  = np.argmax(self.trace)
        else: 
            self._timetopeak  = np.argmin(self.trace)
        return self._timetopeak



           
