from abc import ABC, abstractproperty
from functools import reduce
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import pandas as pd

from ..epochtypes import EpochBlock, IEpoch
from .charting import MplCanvas

class IAnalysis(ABC):

    @property
    @abstractproperty
    def name(self):
        ...

    @property
    @abstractproperty
    def labels(self) -> List[str]:
        ...

    @property
    @abstractproperty
    def tracetype(self) -> IEpoch:
        ...

    @property
    @abstractproperty
    def tracestype(self) -> EpochBlock:
        ...

    @abstractproperty
    def plot(self, eframe: pd.DataFrame, canvas: MplCanvas = None):
        ...
