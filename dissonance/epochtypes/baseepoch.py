from collections import defaultdict
from pathlib import Path
from abc import ABC, abstractproperty
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Tuple, Dict
from datetime import datetime

import numpy as np
import pandas as pd
from h5py._hl.dataset import Dataset
from pytest import param


rstarrdf = pd.read_csv(Path(__file__).parent.parent.parent / "data/rstarrmap.txt", "\t",
                        parse_dates=["startdate", "enddate"])
RSTARRMAP = defaultdict(list)
for _, row in rstarrdf.iterrows():
    RSTARRMAP[(row["protocolname"], row["led"], row["lightamplitude"], row["lightmean"])] = (row["lightamplitude_rstarr"], row["lightmean_rstarr"])


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
    protocolname: str = field(default=None)
    cellname: str = field(default=None)
    celltype: str = field(default=None)
    tracetype: str = field(default=None)
    genotype: str = field(default=None)
    path: str = field(default=None)
    amp: float = field(default=None)
    interpulseinterval: float = field(default=None)
    led: float = field(default=None)
    lightamplitude: float = field(default=None)
    lightmean: float = field(default=None)
    numberofaverages: float = field(default=None)
    pretime: float = field(default=None)
    samplerate: float = field(default=None)
    stimtime: float = field(default=None)
    tailtime: float = field(default=None)
    startdate: str = field(default=None)
    enddate: str = field(default=None)
    startdatetime: datetime = field(init=False, default=None)
    enddatetime: datetime = field(init=False, default=None)


    def __post_init__(self):
        #self.startdatetime = datetime.strptime(
        #    self.startdate, '%Y-%m-%d %H:%M:%S.%f')
        #self.enddatetime = datetime.strptime(
        #    self.enddate, '%Y-%m-%d %H:%M:%S.%f')

        # TODO MOVE THIS TO IO AT READ TIME AND CONVERT TO DICTIONARY  
        # CONVERT LIGHT AMPLITUDE AND LIGHT MEAN TO RSTARR
        try:
                ...
                #df = RSTARRMAP.query(f"(protocolname == '{self.protocolname}') & (led=='{self.led}') & (lightamplitude=={self.lightamplitude}) & (lightmean=={self.lightmean})")
                #self.lightamplitude, self.lightmean = df[["lightamplitude_rstarr", "lightmean_rstarr"]].iloc[0]

                self.lightamplitude, self.lightmean = RSTARRMAP[(self.protocolname, self.led, self.lightamplitude, self.lightmean)]

        except:
            # TODO SHOULD I GO WITH ORIGINAL VALUES?
            print(f"RstarrConversionError,{self.startdatetime},{self.protocolname},{self.led},{self.lightamplitude},{self.lightmean}")


class IEpoch(ABC):

    def __init__(self, epochpath: str, params: DissonanceParams, response: Dataset, number: str = "0"):

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
        self.lightmean = params.lightmean
        self.pctcontrast = (
            self.lightamplitude / self.lightmean 
            if self.lightmean != 0.0 
            else 0.0)
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
    def trace(self):
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

    def __init__(self, epochs: List[IEpoch]):
        self._epochs: List[IEpoch] = epochs
        self._epochs.sort(key=lambda x: x.number)

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
                np.pad(epoch.trace, (0, self.trace_len - len(epoch)))
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
