from typing import List

import numpy as np
from dissonance.funks.psth import calculate_psth
from h5py._hl.dataset import Dataset

from .baseepoch import DissonanceParams, Epochs, EpochSpikeInfo, IEpoch


class SpikeEpoch(IEpoch):

    def __init__(self, epochpath: str,
                 parameters: DissonanceParams = None,
                 spikes: EpochSpikeInfo = None,
                 response: Dataset = None,
                 number="0"):

        super().__init__(epochpath, parameters, response, number)
        self._spikes = spikes
        self._psth = None

    @property
    def spikes(self) -> EpochSpikeInfo:
        return self._spikes

    @property
    def psth(self) -> np.array:
        if self._psth is None:
            self._psth = calculate_psth(self)
        return self._psth

    @property
    def type(self) -> str:
        return "spiketrace"


class SpikeEpochs(Epochs):

    type = "spiketrace"

    def __init__(self, traces: List[SpikeEpoch]):
        super().__init__(traces)
        self._psth: np.array = None
        self._psths: np.array = None

    @property
    def psth(self):
        inc = 100
        if self._psth is None:
            cnt = 0
            for trace in self._traces:
                if len(trace.psth) > 0 and trace.psth is not None:
                    # FILL TAIL OF PSTH'S WITH 0'S SO ALL OF SAME SIZE
                    cpsth = np.pad(
                        trace.psth, (0, int(self.trace_len // inc - len(trace.psth))))
                    if cnt == 0:
                        psths_ = cpsth
                    else:
                        psths_ += cpsth
                    cnt += 1

            if cnt != 0:
                self._psth = psths_ / cnt

        return self._psth

    @property
    def psths(self) -> np.array:
        inc = 100
        if self._psths is None:
            self._psths = []
            for trace in self._traces:
                if len(trace.psth) > 0 and trace.psth is not None:
                    cpsth = np.pad(
                        trace.psth, (0, int(self.trace_len // inc - len(trace.psth))))
                    self._psths.append(cpsth)
        return np.array(self._psths, dtype=float)
