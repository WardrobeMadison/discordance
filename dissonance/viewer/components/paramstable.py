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
        "genotype",
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
    def update(self, epoch: Union[et.IEpoch, et.EpochBlock]):
        """Update params table with epoch 

        Args:
                ii (int): Index row of epoch in dataframe
        """
        # self.data.clear()
        self.setRowCount(0)
        self.setRowCount(len(self.params))
        self.setColumnCount(2)

        data = []
        for ii, paramname in enumerate(self.params):
            self.setItem(ii, 0,
                            QTableWidgetItem(paramname))
            val = epoch.get_unique(paramname)
            text = ",".join(map(str, val))
            self.setItem(ii, 1,
                            QTableWidgetItem(text))
            data.append([paramname, text, val])

        self.df = pd.DataFrame(columns="Param Text Val".split(), data=data)
