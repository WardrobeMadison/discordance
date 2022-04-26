from typing import List, Tuple, Union, Dict, Any
from abc import ABC, abstractproperty

import pandas as pd
import numpy as np

from ...trees import Node, Tree
from ...epochtypes import groupby, Epochs, IEpoch
from ..components.chart import MplCanvas


class BaseAnalysis(ABC, Tree):

    def __init__(self, epochs: Epochs, unchecked: set = None):
        # GROUP EPOCHS INTO FLAT LIST
        self.unchecked = set() if unchecked is None else unchecked
        self.plant(epochs)

    @property
    @abstractproperty
    def name(self):
        ...

    @property
    @abstractproperty
    def labels(self) -> Tuple[str]:
        ...

    @property
    @abstractproperty
    def tracetype(self) -> IEpoch:
        ...

    @property
    @abstractproperty
    def tracestype(self) -> Epochs:
        ...

    @abstractproperty
    def plot(self, node: Node, canvas: MplCanvas = None):
        ...

    def plant(self, epochs):
        df = groupby(epochs, self.labels)
        self.keys = df[[col for col in df.columns if col != "trace"]].values
        self.groupedvals = df.loc[:, "trace"].values

        # CREATE TREE STRUCTURE
        super().__init__(self.name, self.labels, self.keys)

        # MAP EPOCHS TO LEAVES OF TREE
        # TODO sort leaves automatically by number
        leaves = list(self.leaves)
        leaves.sort(key=lambda x: x.number)
        for leaf in leaves:
            condition = " and ".join((f"{key} == '{val}'" for key,val in leaf.path.items() if key != "Name"))
            epochs = df.query(condition).iloc[0,-1] # ONLY ONE WILL FIT  
            for epoch in epochs:
                leaf.add(Node("startdate", epoch.startdate, epoch.number))

        # CREATE DATAFRAME WITH SEPARATE EPOCHS IN EACH ROW
        # FLAG INCLUDED AND EXCLUDED EPOCHS
        data = []
        for key, group in zip(self.keys, self.groupedvals):
            for epoch in group:
                if epoch.startdate in self.unchecked:
                    data.append([*key, epoch.startdate, False, epoch])
                else:
                    data.append([*key, epoch.startdate, True, epoch])

        # CREATE DATAFRAME FOR INCES LOOKUP OF EPOCHS BY PARAMETERS	FOR FASTER QUERIES
        self.frame = (
            pd.DataFrame(columns=[*self.labels, "startdate",
                         "include", "epoch"], data=data)
            .set_index(keys=[*self.labels, "startdate"])
            .sort_index())

    def update(self, node, paramname: str, value: Any):
        epochs = self.query(node, useincludeflag=None)
        keys = node.path

        # UPDATE EACH EPOCH
        for epoch in epochs:
            epoch.update(keys, paramname, value)

        # REMAKE THE WHOLE CLASS.
        epochs = self.frame.epoch.to_list()
        self.__init__(epochs, self.unchecked)

    def query(self, node: Node, useincludeflag=True) -> Union[Epochs, IEpoch]:
        """Relate nodes from tree to underlying dataframe. Only passes inclued nodes

        Args:
                node (Node): Node's path used for lookup

        Returns:
                Union[Traces, ITrace]: Traces or individual Trace for leaf node
        """

        if not isinstance(node, list):
            nodes = [node]
        else:
            nodes = node

        vals_ = []
        for node in nodes:
            if node.isleaf:
                vals = self.frame.query(f"startdate == '{node.uid}'").epoch.iloc[0]
                vals_.append(vals)
            else:
                # DICTIONARY OF ALL VALUES
                path = node.path  
                # BUILD FILTER CONDITION
                # FILTERED ON INDEX SO ONLY NEED VALUES IN LABEL ORDER
                condition = []
                for key in self.labels:
                    temp = path.get(key)
                    if temp is None:
                        temp = slice(None)
                    condition.append(temp)
                dff = self.frame.loc[tuple(condition), :]
                
                # FILTER FOR CHECKED VALUES
                if useincludeflag is False:
                    vals = dff.loc[:, "epoch"].to_list()
                else:
                    vals = dff.loc[dff.include == useincludeflag, "epoch"].to_list()
                vals_.extend(vals)

        if len(vals_) == 1:
            return vals_[0]
        else:
            return self.tracestype(vals_)
