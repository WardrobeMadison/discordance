from abc import ABC, abstractproperty
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Tuple

import h5py
import numpy as np
import pandas as pd

from .baseepoch import IEpoch


class NoiseEpoch(IEpoch):

    def __init__(self, epochgrp: h5py.Group):
        super().__init__(epochgrp)

        self.stimparams = {key: val for key,
                        val in epochgrp[self.led].attrs.items()}

    @property
    def type(self):
        return "noisepoch"

    @property
    def stimulus(self):
        std = self.stimparams["stdev"]
        mean = self.stimparams["mean"]
        lower = self.stimparams["lowerlimit"]
        upper = self.stimparams["upperlimit"]
        seed = self.stimparams["seed"]

        np.random.seed(seed)

        # REVERSE ORDER TO MATCH MATLAB
        if self.stimparams["units"] == "_normalized_":
            stim = np.random.randn((1,len(self))).T * std + mean
            stim = np.clip(stim, lower, upper)
            return stim
        else:
            raise Exception(f"Don't know these units! {self.stimparams['units']}")

