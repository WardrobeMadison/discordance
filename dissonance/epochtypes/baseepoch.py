from abc import ABC, abstractproperty
from typing import Dict, Iterable, Iterator, List, Tuple

import h5py
import numpy as np


class IEpoch(ABC):

    def __init__(self, epochgrp: h5py.Group):

        self._epochpath: str = epochgrp.name
        self._response_ds = epochgrp["Amp1"]

        self.protocolname = epochgrp.attrs.get("protocolname")
        self.cellname = epochgrp.attrs.get("cellname")
        self.celltype = epochgrp.attrs.get("celltype")
        self.genotype = epochgrp.attrs.get("genotype")
        self.tracetype = epochgrp.attrs.get("tracetype")
        self.path = epochgrp.attrs.get("path")
        self.amp = epochgrp.attrs.get("amp")
        self.interpulseinterval = epochgrp.attrs.get("interpulseinterval")
        self.led = epochgrp.attrs.get("led")
        self.lightamplitude = epochgrp.attrs.get("lightamplitude")
        self.lightmean = epochgrp.attrs.get("lightmean")
        self.numberofaverages = epochgrp.attrs.get("numberofaverages")
        self.samplerate = epochgrp.attrs.get("samplerate")
        self.pretime = epochgrp.attrs.get("pretime") * 10
        self.stimtime = epochgrp.attrs.get("stimtime") * 10
        self.tailtime = epochgrp.attrs.get("tailtime") * 10
        self.startdate = epochgrp.attrs.get("startdate")
        self.enddate = epochgrp.attrs.get("enddate")
        self.number = int(epochgrp.name.split("/")[-1][5:])
        self.pctcontrast = (
            self.lightamplitude / self.lightmean
            if self.lightmean != 0.0
            else 0.0)

    def __hash__(self):
        return hash(self.startdate)

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
                #print(f"Couldn't set {paramname, value} on object {self}.")
                ...
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

    def params(self) -> Dict:
        return dict()


class EpochBlock(ABC):

    def __init__(self, epochs: List[IEpoch]):
        self._epochs: List[IEpoch] = epochs
        self._epchs = sorted(self._epochs, key=lambda x: x.number)

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

    def __hash__(self):
        startdates = set(self.get_unique("startdate"))
        return hash(startdates)

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


