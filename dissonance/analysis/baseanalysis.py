from pathlib import Path
from typing import List, Tuple, Union, Dict, Any
from abc import ABC, abstractproperty

import pandas as pd
import numpy as np
import operator
from functools import reduce
import h5py

from .trees import Node, Tree
from ..epochtypes import groupby, EpochBlock, IEpoch, epoch_factory
from .charting import MplCanvas
from .analysistree import AnalysisTree


class EpochIO(ABC):

    def __init__(self, params: pd.DataFrame, experimentpaths: List[Path], unchecked: set = None):
        self.files = {
            path: h5py.File(str(path),"a")["experiment"] for path in experimentpaths
        }
        # GROUP EPOCHS INTO FLAT LIST
        self.unchecked = set() if unchecked is None else unchecked
        self.set_frame(params)
        
    def to_tree(self, name, splits) -> AnalysisTree:
        return AnalysisTree(name, splits, self.frame)

    def set_frame(self, params:pd.DataFrame):
        params.loc[:, "include"] = params.startdate.apply(lambda x: not (x in self.unchecked))
        self.frame = params

    def update(self, filters:List[Dict], paramname: str, value: Any):
        # FILTER DATATABLE TO APPLICABLE EPOCHS
        eframe = self.query(filters=filters)

        for _, row in eframe.iterrows():
            # UPDATE H5 GROUP ATTRIBUTES
            row["epoch"].update(paramname, value)
            # UPDATE EPOCHIO DATATABLE PARAMETERS
            if paramname in self.frame.columns:
                self.frame.loc[self.frame.startdate == row["startdate"], paramname] = value

        # FLUSH CHANGES MADE TO ANY H5 FILES
        for experimentgrp in self.files.values(): experimentgrp.file.flush()

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
        for filter in filters:
            if "Name" in filter.keys(): 
                del filter["Name"]
            if len(filter) == 1 and list(filter.keys())[0] == "startdate":
                dfs.append(self.frame.query(f"startdate == {filter['startdate']:!r}"))
            else:
                # DICTIONARY OF ALL VALUES
                # BUILD FILTER CONDITION
                # FILTERED ON INDEX SO ONLY NEED VALUES IN LABEL ORDER
                condition = []
                for key,value in filter.items():
                    if value is None:
                        condition.append(
                            self.frame[key].apply(lambda x: x is None)
                        )
                    else:
                        condition.append(
                            self.frame[key] == value
                        )
                dff = self.frame.loc[reduce(operator.and_, condition), :]
                
                # FILTER FOR CHECKED VALUES
                if useincludeflag is False:
                    dfs.append(dff)
                else:
                    dfs.append(dff.loc[dff.include == True])
        # CONVERT TO EPOCHS IN DATAFRAME    
        if len(dfs) == 0:
            raise Exception("No epochs returns")
        else:
            df = (pd.concat(dfs))
            df = df.reset_index(drop=True)
            df = df.drop_duplicates(keep="first")
            # HACK why are there NAs here?
            df = df[~df.isna()]

        if df.shape[0] != 0:
            def func(row):
                try:
                    return epoch_factory(self.files[row.exppath][f"epoch{int(row.number)}"])
                except Exception as e:
                    print(row.exppath)
                    raise e

            df["epoch"] = df.apply(lambda x: 
                func(x),
                axis=1)
        else:
            raise Exception("No epochs returns")

        return df


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
