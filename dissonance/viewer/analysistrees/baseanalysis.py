from typing import List, Tuple, Union, Dict, Any
from abc import ABC, abstractproperty

import pandas as pd
import numpy as np

from ...trees import Node, Tree
from ...epochtypes import groupby, Traces, ITrace
from ..components.chart import MplCanvas

# AMP, MEAN
PCTCNTRST = {
    (-0.001, 0.005): -25,
    (-0.003, 0.005): -50,
    (-0.005, 0.005): -100,
    (0.001, 0.005): 25,
    (0.003, 0.005): 50,
    (0.005, 0.005): 100,
    (0.002, 0.007): 25,
    (0.004, 0.007): 50,
    (0.005, 0.007): 75,
    (0.007, 0.007): 100,
    (-0.002, 0.007): -25,
    (-0.004, 0.007): -50,
    (-0.005, 0.007): -75,
    (-0.007, 0.007): -100,
    (-0.002, 0.006): -25,
    (-0.003, 0.006): -50,
    (-0.006, 0.006): -100,
    (0.002, 0.006): 25,
    (0.003, 0.006): 50,
    (0.006, 0.006): 100,
    (-0.006, 0.006): -100,
    (0.002, 0.005): 50,
    (0.004, 0.005): 75,
    (-0.004, 0.005): -75,
    (0.005, 0.006): 75,
    (-0.005, 0.006): -75,
    (0.005, 0): 0,
    (0.006, 0): 0}

# LED, AMP
RSTRMAP = {
    ("Green", 0.007): 5,
    ("Green", 0.014): 10,
    ("Green", 0.0121): 10,
    ("Green", 0.006): 5,
    ("Green", 0.003): 0.025,
    ("Green", 0.006): 0.05,
    ("Green", 0.012): 0.1,
    ("Green", 0.024): 0.2,
    ("Green", 0.048): 0.4,
    ("Green", 0.096): 0.8,
    ("Green", 0.192): 1.6,
    ("Green", 0.384): 3.2,
    ("Green", 0.015): 0.1,
    ("Green", 0.03): 0.2,
    ("Green", 0.06): 0.4,
    ("Green", 0.12): 0.8,
    ("Green", 0.24): 1.6,
    ("Green", 0.48): 3.2,
    ("Green", 0.004): 0.025,
    ("Green", 0.008): 0.05,
    ("Green", 0.016): 0.1,
    ("Green", 0.032): 0.2,
    ("Green", 0.064): 0.4,
    ("Green", 0.128): 0.8,
    ("Green", 0.256): 1.6,
    ("Green", 0.512): 3.2,
    ("Green", 0.007): 0.05,
    ("Green", 0.014): 0.1,
    ("Green", 0.028): 0.2,
    ("Green", 0.056): 0.4,
    ("Green", 0.112): 0.8,
    ("Green", 0.224): 1.6,
    ("Green", 0.448): 3.2,
    ("Green", 0.896): 6.4,
    ("Green", 0.768): 6.4,
    ("Green", 0.0074): 0.05,
    ("Green", 0.0148): 0.1,
    ("Green", 0.006): 5,
    ("Green", 0.007): 5,
    ("Green", 0.012): 10,
    ("Green", 0.013): 10,
    ("Green", 0.014): 10,
    ("Green", 0.0121): 10}


class BaseAnalysis(ABC, Tree):
    pctcntrst = PCTCNTRST
    rstrmap = RSTRMAP

    def __init__(self, epochs: Traces, unchecked: set = None):
        # GROUP EPOCHS INTO FLAT LIST
        self.unchecked = set() if unchecked is None else unchecked
        self.plant(epochs)

    @property
    @abstractproperty
    def name(self):
        ...

    @property
    @abstractproperty
    def protocolname(self):
        ...

    @property
    @abstractproperty
    def led(self):
        ...

    @property
    @abstractproperty
    def labels(self) -> Tuple[str]:
        ...

    @property
    @abstractproperty
    def tracetype(self) -> ITrace:
        ...

    @property
    @abstractproperty
    def tracestype(self) -> Traces:
        ...

    @abstractproperty
    def plot(self, node: Node, canvas: MplCanvas = None):
        ...

    def plant(self, epochs):
        self.create_groups(epochs)

        # CREATE TREE STRUCTURE
        super().__init__(self.name, self.labels, self.keys)

        # ADD EPOCHS TO LEAVES OF TREE
        self.add_epoch_leaves()

        # CREATE DATAFRAME
        self.create_frame()

    def create_groups(self, epochs):
        df = groupby(epochs, self.labels)
        self.keys = df[[col for col in df.columns if col != "trace"]].values
        self.groupedvals = df.loc[:, "trace"].values

    def add_epoch_leaves(self):
        # ADD EPOCHS AS LEAVES TO TREE
        for leaf, group in zip(self.leaves, self.groupedvals):
            for epoch in group:
                leaf.add(Node("startdate", epoch.startdate))

    def create_frame(self):
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
        epochs = self.query(node, includeflag=None)
        keys = node.path

        # UPDATE EACH EPOCH
        for epoch in epochs:
            epoch.update(keys, paramname, value)

        # REMAKE THE WHOLE CLASS.
        epochs = self.frame.epoch.to_list()
        self.__init__(epochs, self.unchecked)

    def query(self, node: Node, includeflag=True) -> Union[Traces, ITrace]:
        """Relate nodes from tree to underlying dataframe. Only passes inclued nodes

        Args:
                node (Node): Node's path used for lookup

        Returns:
                Union[Traces, ITrace]: Traces or individual Trace for leaf node
        """
        if node.isleaf:
            return self.frame.query(f"startdate == '{node.uid}'").epoch.iloc[0]
        else:
            path = node.path  # dictionary of all values
            #condition = " and ".join([f"{key}=='{val}'" for key,val in path.items()])
            #df.loc[(slice(None), 5, slice(None))]
            condition = []
            for key in self.labels:
                temp = path.get(key)
                if temp is None:
                    temp = slice(None)
                condition.append(temp)

            dff = self.frame.loc[tuple(condition), :]
            if includeflag is None:
                vals = dff.loc[:, "epoch"].to_list()
            else:
                vals = dff.loc[dff.include == includeflag, "epoch"].to_list()
            return self.tracestype(self.labels, vals)
