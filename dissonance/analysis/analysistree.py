from pathlib import Path
from typing import List, Tuple, Union, Dict, Any
from abc import ABC, abstractproperty

import pandas as pd

from .trees import Node, Tree

class AnalysisTree(Tree):

    def __init__(self, name, splits, params: pd.DataFrame):
        self.name = name
        self.splits = splits
        self.plant(params)

    def plant(self, params: pd.DataFrame):
        self.labels = self.splits

        if "startdate" not in self.labels:
            self.labels = [*self.labels, "startdate"]
        self.keys = params[self.labels].values

        # CREATE TREE STRUCTURE
        super().__init__(self.name, self.labels, self.keys)
