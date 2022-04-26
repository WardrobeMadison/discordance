from abc import ABC, abstractproperty
from dataclasses import dataclass, field
from typing import Iterator, List, Tuple
from datetime import datetime

import numpy as np
import pandas as pd
from h5py._hl.dataset import Dataset

PCTCNTRST = pd.DataFrame(
    columns="lightamplitude lightmean pctcontrast".split(),
    data=[
        [-0.001, 0.005, -25],
        [-0.003, 0.005, -50],
        [-0.005, 0.005, -100],
        [0.001, 0.005, 25],
        [0.003, 0.005, 50],
        [0.005, 0.005, 100],
        [0.002, 0.007, 25],
        [0.004, 0.007, 50],
        [0.005, 0.007, 75],
        [0.007, 0.007, 100],
        [-0.002, 0.007, -25],
        [-0.004, 0.007, -50],
        [-0.005, 0.007, -75],
        [-0.007, 0.007, -100],
        [-0.002, 0.006, -25],
        [-0.003, 0.006, -50],
        [-0.006, 0.006, -100],
        [0.002, 0.006, 25],
        [0.003, 0.006, 50],
        [0.006, 0.006, 100],
        [-0.006, 0.006, -100],
        [0.002, 0.005, 50],
        [0.004, 0.005, 75],
        [-0.004, 0.005, -75],
        [0.005, 0.006, 75],
        [-0.005, 0.006, -75],
        [0.005, 0, 0],
        [0.006, 0, 0]])

def get_pctcntrst(lightamp, lightmean):
    try:
        return PCTCNTRST.loc[
            (PCTCNTRST.lightamplitude == lightamp) &
            (PCTCNTRST.lightmean == lightmean),
            "pctcontrast"
        ]
    except:
        return 0.0


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
        self.pctcontrast = get_pctcntrst(self.lightamplitude, self.lightmean)

    def __eq__(self, other) -> bool:
        return self.enddate == other.enddate

    def __ne__(self, other) -> bool:
        return self.enddate != other.enddate

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


class Epochs(ABC):

    def __init__(self, traces=List[IEpoch]):
        # HACK key should be daterange, convert dates from string to datetimes
        if len(traces) > 0:
            self.key = traces[0].startdate
        else:
            self.key = None
        self._traces: List[IEpoch] = traces
        self._traces.sort(key = lambda x: x.number)
        self._trace_len: int = None
        self._celltypes: List[str] = None
        self._tracetypes: List[str] = None
        self._genotypes: List[str] = None
        self._interpulseintervals = None
        self._leds = None
        self._cellnames: List[str] = None
        self._protocolnames: List[str] = None
        self._lightamplitudes: List[float] = None
        self._rstarrs: List[float] = None
        self._lightmeans: List[float] = None
        self._pretimes: List[float] = None
        self._samplerates: List[float] = None
        self._stimtimes: List[float] = None
        self._pretimes: List[float] = None
        self._tailtimes: List[float] = None
        self._startdates: List[str] = None
        self._enddates: List[str] = None
        self._values: np.array = None
        self._pctcontrasts: List[float] = None

    def __str__(self):
        return str(self.key)

    def __getitem__(self, val) -> IEpoch:
        return self._traces[val]

    def __len__(self):
        return len(self._traces)

    @property
    def trace_len(self):
        if self._trace_len is None:
            #self._trace_len = max([len(e) for e in self._traces])
            # TODO HACK debug the above
            self._trace_len = int(max([len(e) for e in self._traces]))
        return self._trace_len

    @property
    def traces(self) -> List[IEpoch]: return self._traces

    @property
    def values(self) -> np.array:
        # PAD ALL VALUES TO STRETCH INTO FULL ARRAY
        # TODO Don't cache value call
        if self._values is None:
            self._values = np.vstack(
                [
                    np.pad(trace.values, (0, self.trace_len - len(trace)))
                    for trace in self._traces
                ])
        return self._values

    @property
    def rstarrs(self) -> List[str]:
        self._rstarrs = list(
            map(
                lambda e: e.rstarr,
                self._traces))
        return self._rstarrs

    @property
    def celltypes(self) -> List[str]:
        self._celltypes = list(
            map(
                lambda e: e.celltype,
                self._traces))
        return self._celltypes

    @property
    def pctcontrasts(self) -> List[str]:
        self._pctcontrasts = list(
            map(
                lambda e: e.pctcontrast,
                self._traces))
        return self._pctcontrasts

    @property
    def tracetypes(self) -> List[str]:
        if self._tracetypes is None:
            self._tracetypes = list(
                map(
                    lambda e: e.tracetypes,
                    self._traces))
        return self._tracetypes

    @property
    def genotypes(self) -> List[str]:
        self._genotypes = list(
            map(
                lambda e: e.genotype,
                self._traces))
        return self._genotypes

    @property
    def protocolnames(self) -> List[str]:
        if self._protocolnames is None:
            self._protocolnames = list(
                map(
                    lambda e: e.protocolname,
                    self._traces))
        return self._protocolnames

    @property
    def cellnames(self) -> List[str]:
        if self._cellnames is None:
            self._cellnames = list(
                map(
                    lambda e:
                    e.cellname,
                    self._traces))
        return self._cellnames

    @property
    def lightamplitudes(self) -> List[float]:
        if self._lightamplitudes is None:
            self._lightamplitudes = list(
                map(
                    lambda e:
                    e.lightamplitude,
                    self._traces))
        return self._lightamplitudes

    @property
    def lightmeans(self) -> List[float]:
        if self._lightmeans is None:
            self._lightmeans = list(
                map(
                    lambda e:
                    e.lightmean,
                    self._traces))
        return self._lightmeans

    @property
    def pretimes(self) -> List[float]:
        if self._pretimes is None:
            self._pretimes = list(
                map(
                    lambda e:
                    e.pretime,
                    self._traces))
        return self._pretimes

    @property
    def samplerates(self) -> List[float]:
        if self._samplerates is None:
            self._samplerates = list(
                map(
                    lambda e:
                    e.samplerate,
                    self._traces))
        return self._samplerates

    @property
    def stimtimes(self) -> List[float]:
        if self._stimtimes is None:
            self._stimtimes = list(
                map(
                    lambda e:
                    e.stimtime,
                    self._traces))
        return self._stimtimes

    @property
    def pretimes(self) -> List[float]:
        if self._pretimes is None:
            self._pretimes = list(
                map(
                    lambda e:
                    e.pretime,
                    self._traces))
        return self._pretimes

    @property
    def tailtimes(self) -> List[float]:
        if self._tailtimes is None:
            self._tailtimes = list(
                map(
                    lambda e:
                    e.tailtime,
                    self._traces))
        return self._tailtimes

    @property
    def startdates(self) -> List[str]:
        if self._startdates is None:
            self._startdates = list(
                map(
                    lambda e:
                    e.startdate,
                    self._traces))
        return self._startdates

    @property
    def enddates(self) -> List[str]:
        if self._enddates is None:
            self._enddates = list(
                map(
                    lambda e:
                    e.enddate,
                    self._traces))
        return self._enddates

    @property
    def interpulseintervals(self) -> List[str]:
        if self._interpulseintervals is None:
            self._interpulseintervals = list(
                map(
                    lambda e:
                    e.interpulseinterval,
                    self._traces))
        return self._interpulseintervals

    @property
    def leds(self) -> List[str]:
        self._leds = list(
            map(
                lambda e:
                e.led,
                self._traces))
        return self._leds

    def get(self, paramname):
        try:
            return np.fromiter(
                map(
                    lambda e:
                    getattr(e, paramname),
                    self._traces
                ),
                dtype=float)
        except:
            return np.fromiter(
                map(
                    lambda e:
                    getattr(e, paramname),
                    self._traces
                ),
                dtype=str)
