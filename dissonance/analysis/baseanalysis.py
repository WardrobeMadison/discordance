from pathlib import Path
from typing import List, Tuple, Union, Dict, Any
from abc import ABC, abstractproperty

import pandas as pd
import numpy as np
import operator
from functools import reduce
import h5py

from ..trees import Node, Tree
from ..epochtypes import groupby, EpochBlock, IEpoch
from .charting import MplCanvas


class BaseAnalysis(ABC, Tree):

    def __init__(self, params: pd.DataFrame, experimentpaths: List[Path], unchecked: set = None):
        self.files = {
            path: h5py.File(str(path))["experiment"] for path in experimentpaths
        }
        # GROUP EPOCHS INTO FLAT LIST
        self.unchecked = set() if unchecked is None else unchecked
        self.plant(params)

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
    def plot(self, node: Node, canvas: MplCanvas = None):
        ...

    def plant(self, params: pd.DataFrame):
        self.keys = params[self.labels].values

        # CREATE TREE STRUCTURE
        super().__init__(self.name, self.labels, self.keys)

        params["include"] = params.startdate.apply(lambda x: not (x in self.unchecked))

        # CREATE DATAFRAME FOR INCES LOOKUP OF EPOCHS BY PARAMETERS	FOR FASTER QUERIES
        self.frame = params

    def update(self, node, paramname: str, value: Any):
        epochs = self.query(node, useincludeflag=None)
        keys = node.path

        # UPDATE EACH EPOCH
        for epoch in epochs:
            epoch.update(keys, paramname, value)

        # REMAKE THE WHOLE CLASS.
        epochs = self.frame.epoch.to_list()
        self.__init__(epochs, self.unchecked)

    def query(self, filters=List[Dict], useincludeflag=True) -> pd.DataFrame:
        """Relate nodes from tree to underlying dataframe. Only passes inclued nodes

        Args:
                node (Node): Node's path used for lookup

        Returns:
                Union[Traces, ITrace]: Traces or individual Trace for leaf node
        """
        if not isinstance(filters, list):
            filters = [filters]

        dfs = []
        vals_ = []
        for filter in filters:
            if len(filter) == 1 and list(filter.keys())[0] == "startdate":
                dfs.append(self.frame.query(f"""startdate == '{filter["startdate"]}'"""))
            else:
                # DICTIONARY OF ALL VALUES
                # BUILD FILTER CONDITION
                # FILTERED ON INDEX SO ONLY NEED VALUES IN LABEL ORDER
                condition = []
               # for key in self.labels:
               #     temp = filter.get(key)
               #     if temp is None:
               #         temp = slice(None)
               #     condition.append(temp)
                for key,value in filter.items():
                    condition.append(
                        self.frame[key] == value
                    )
                dff = self.frame.loc[reduce(operator.and_, condition), :]
                
                # FILTER FOR CHECKED VALUES
                if useincludeflag is False:
                    dfs.append(dff)
                else:
                    dfs.append(dff.loc[dff.include == useincludeflag])
                # TODO convert to epoch
                vals = []
                vals_.extend(vals)
        # CONVERT TO EPOCHS IN DATAFRAME    
        df = (pd.concat(dfs)
            .reset_index(drop=True)
            .drop_duplicates(keep="first"))

        df["epoch"] = df.apply(lambda x: 
            self.tracetype(self.files[x.exppath][f"epoch{int(x.number)}"]), 
            axis=1)

        if len(vals_) == 1:
            return vals_[0]
        else:
            return self.tracestype(vals_)
