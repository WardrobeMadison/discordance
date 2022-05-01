from pathlib import Path

import pandas as pd
from PyQt5.Qt import Qt
from PyQt5.QtCore import (QModelIndex, QObject, Qt, QThread, pyqtSignal,
                          pyqtSlot)
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QDialog,
                             QFileDialog, QHBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)

from ..analysis import  IAnalysis
from ..analysis.charting import MplCanvas


class GraphWidget(QWidget):

    def __init__(self, analysis: IAnalysis, canvas: MplCanvas):
        super().__init__()
        self.analysis = analysis
        self.canvas = canvas
        self.currentplots = []

    @pyqtSlot(str, object)
    def plot(self, level:str, eframe: pd.DataFrame):
        self.analysis.plot(level, eframe, self.canvas)
        self.currentplots = self.analysis.currentplots
        self.canvas.draw()
