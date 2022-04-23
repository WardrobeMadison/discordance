from typing import Union

import pandas as pd
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from ... import epochtypes as et


class ParamsTable(QTableWidget):

    params = [
        "cellname",
        "startdate",
        "celltype",
        "protocolname",
        "enddate",
        "interpulseinterval",
        "led",
        "lightamplitude",
        "lightmean",
        "pretime",
        "stimtime",
        "samplerate",
        "tailtime"]

    def __init__(self, epoch: Union[et.SpikeEpoch, et.WholeEpoch]):
        super().__init__()

        self.update(epoch)

    @pyqtSlot()
    def update(self, epoch: Union[et.IEpoch, et.Epochs]):
        """Update params table with epoch 

        Args:
                ii (int): Index row of epoch in dataframe
        """
        # self.data.clear()
        self.setRowCount(0)
        self.setRowCount(len(self.params))
        self.setColumnCount(2)

        data = []
        if isinstance(epoch, et.Epochs):
            for ii, paramname in enumerate(self.params):
                self.setItem(ii, 0,
                             QTableWidgetItem(paramname))
                val = set(getattr(epoch, paramname+"s"))
                text = ",".join(map(str, val))
                self.setItem(ii, 1,
                             QTableWidgetItem(text))
                data.append([paramname, text, val])
        else:
            for ii, paramname in enumerate(self.params):
                self.setItem(ii, 0,
                             QTableWidgetItem(paramname))
                val = getattr(epoch, paramname)
                text = str(val)
                self.setItem(ii, 1,
                             QTableWidgetItem(text))
                data.append([paramname, text, val])

        self.df = pd.DataFrame(columns="Param Text Val".split(), data=data)
