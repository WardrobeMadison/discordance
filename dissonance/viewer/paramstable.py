from typing import Union, List, Iterable

import pandas as pd
import numpy as np
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from .. import epochtypes as et

class ParamsTable(QTableWidget):
    rowEdited = pyqtSignal(str, object)

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

    def __init__(self, epoch: Union[et.SpikeEpoch, et.WholeEpoch]=None):
        super().__init__()

        self.initConnections()

        if epoch is not None:
            self.fillTable(epoch)
        
    def initConnections(self):
        self.itemDelegate().closeEditor.connect(self.onTableEdit)

    def fillTable(self, epochs: List[Union[et.IEpoch, et.EpochBlock]]):
        """Update params table with epoch 

        Args:
                ii (int): Index row of epoch in dataframe
        """
        if not isinstance(epochs, Iterable):
            epochs = [epochs]

        # self.data.clear()
        self.setRowCount(0)
        self.setRowCount(len(self.params))
        self.setColumnCount(2)

        data = []
        for ii, paramname in enumerate(self.params):
            self.setItem(ii, 0,
                            QTableWidgetItem(paramname))
            vals  = list()
            for epoch in epochs:
                val = epoch.get_unique(paramname)
                vals.extend(val)

            text = ", ".join(map(str, list(set(vals))))
            self.setItem(ii, 1, QTableWidgetItem(text))
            data.append([paramname, text, vals])

        self.df = pd.DataFrame(columns="Param Text Val".split(), data=data)
    
    @pyqtSlot(list)
    def onNewEpochs(self, epochs):
        self.fillTable(epochs)

    @pyqtSlot()
    def onTableEdit(self):
        idx = self.selectionModel().currentIndex()
        row, col = idx.row(), idx.column()
        paramname = self.model().index(row, 0).data()
        value = self.model().index(row, 1).data()

        self.rowEdited.emit(paramname, value)
