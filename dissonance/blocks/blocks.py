from abc import ABC, abstractmethod
from collections import UserList
from itertools import groupby

class EpochList(UserList):

    def __init__(self, epochs=None, keys=None):

        if epochs is None:
            return

        self.keys = keys
        super().__init__(self, epochs)

        if keys is not None:
            for key in keys:
                if not self.ishomogenous((getattr(epoch, key) for epoch in epochs)):
                    raise Exception(f"Need homogenous list w.r.t keys {keys}.")

    def append(self, item):
        if self.keys is not None:
            if len(self) != 0:
                if not self.ishomogenous((self.data[-1], item)):
                    raise Exception(f"Need homogenous list w.r.t keys {self.keys}.")
        super().append(item)
    
    @staticmethod
    def ishomogenous(iterable):
        g = groupby(iterable)
        return next(g, True) and not next(g, False)

class IBlock:

    @property
    @abstractmethod
    def keys(self):
        ...

class IEpoch:

    @property
    @abstractmethod
    def startdate(self):
        ...

    @property
    @abstractmethod
    def trace(self):
        ...