from abc import ABC, abstractproperty
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Tuple, Dict
from datetime import datetime
from matplotlib.colors import LightSource

import numpy as np
import pandas as pd
from h5py._hl.dataset import Dataset
from pytest import param

@dataclass
class EpochSpikeInfo:
    sp: np.array
    spike_amps: np.array
    min_spike_peak_idx: np.array
    max_noise_peak_time: np.array
    violation_idx: np.array

    def __post_init__(self):
        self.sp = self.sp.astype(int)
        self.min_spike_peak_idx = self.min_spike_peak_idx.astype(int)
        self.max_noise_peak_time = self.max_noise_peak_time.astype(int)
        self.violation_idx = self.violation_idx.astype(int)

@dataclass
class DissonanceParams:
    protocolname: str = field( default=None)
    cellname: str = field( default=None)
    celltype: str = field( default=None)
    tracetype: str = field( default = None)
    genotype: str = field( default = None)
    path: str = field( default=None)
    amp: float = field( default=None)
    interpulseinterval: float = field( default=None)
    led: float = field( default=None)
    lightamplitude: float = field( default=None)
    rstarr: float = field(default=None)
    lightmean: float = field( default=None)
    numberofaverages: float = field( default=None)
    pretime: float = field( default=None)
    samplerate: float = field( default=None)
    stimtime: float = field( default=None)
    tailtime: float = field( default=None)
    startdate: str = field( default=None)
    enddate: str = field( default=None)


class IEpoch(ABC):

    def __init__(self, epochpath: str, params: DissonanceParams, response: Dataset, number:str="0"):

        self._epochpath: str = epochpath
        self._response_ds = response

        self.protocolname = params.protocolname
        self.cellname = params.cellname
        self.celltype = params.celltype
        self.genotype = params.genotype
        self.tracetype = params.tracetype
        self.path = params.path
        self.amp = params.amp
        self.interpulseinterval = params.interpulseinterval
        self.led = params.led
        self.lightamplitude = params.lightamplitude
        self.rstarr = params.rstarr
        self.lightmean = params.lightmean
        self.numberofaverages = params.numberofaverages
        self.samplerate = params.samplerate
        self.pretime = params.pretime * 10
        self.stimtime = params.stimtime * 10
        self.tailtime = params.tailtime * 10
        self.startdate = params.startdate
        self.enddate = params.enddate
        self.number = number

    def __str__(self):
        return f"Epoch(cell_name={self.cellname}, start_date={self.startdate})"

    def __len__(self):
        try:
            return int(self.pretime + self.stimtime + self.tailtime)
        except TypeError as e:
            print(e)
            return 0.0

    def update(self, paramname, value):
        if paramname in set(["genotype", "celltype"]):
            parent = self._response_ds.parent
            parent.attrs[paramname] = value
            try:
                setattr(self, paramname, value)
            except:
                print(f"Couldn't set {paramname, value} on object {self}.")
            return
        else:
            print(f"Can't change {paramname} to {value}")

    @property
    def values(self):
        return self._response_ds[:]

    @property
    @abstractproperty
    def type(self):
        ...

    def get(self, paramname):
        return [getattr(self, paramname)]
    def get_unique(self, paramname):
        return [getattr(self, paramname)]

class EpochBlock(ABC):

    def __init__(self, epochs:List[IEpoch]):
        self._epochs: List[IEpoch] = epochs
        self._epochs.sort(key = lambda x: x.number)

        if len(epochs) > 0:
            self.key = epochs[0].startdate
        else:
            self.key = None

        # DUMMY PROPERTIES
        self._trace_len: int = None

    def __str__(self):
        return "EpochBlock"

    def __repr__(self):
        return "EpochBlocks"

    def __getitem__(self, val) -> IEpoch:
        return self._epochs[val]

    def __len__(self):
        return len(self._epochs)

    def __iter__(self) -> Iterable[IEpoch]:
        yield from self._epochs

    @property
    def epochs(self) -> List[IEpoch]: 
        return self._epochs

    def append(self, epoch) -> None:
        self._trace_len = None
        self._epochs.append(epoch)

    @property
    def trace_len(self):
        if self._trace_len is None:
            #self._trace_len = max([len(e) for e in self._traces])
            # TODO HACK debug the above
            self._trace_len = int(max([len(e) for e in self._epochs]))
        return self._trace_len

    @property
    def traces(self) -> np.array:
        # PAD ALL VALUES TO STRETCH INTO FULL ARRAY
        return np.vstack(
                [
                    np.pad(epoch.values, (0, self.trace_len - len(epoch)))
                    for epoch in self._epochs
                ])

    def get(self, paramname) -> np.array:
        try:
            return np.array(
                [
                    getattr(e, paramname)
                    for e in self._epochs
                ],
                dtype=float)
        except:
            return np.array(
                [
                    getattr(e, paramname)
                    for e in self._epochs
                ],
                dtype=str)

    def get_unique(self, paramname) -> np.array:
        return np.unique(self.get(paramname))
    