import sys
from typing import Union

import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtCore import QModelIndex, pyqtSlot
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
                             QPushButton, QVBoxLayout, QWidget)
import matplotlib.pyplot as plt
plt.style.use('seaborn-ticks')

from ..epochtypes import Traces, SpikeTraces
from . import components as cp


class App(QWidget):

    def __init__(self, epochs: Traces, groupkeys=["protocolname", "celltype", "cellname", "lightamplitude", "lightmean"], unchecked: set=None):
        super().__init__()
        self.unchecked = unchecked
        self.groupkeys = groupkeys
        self.epochs = epochs
        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 800
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Discordance")
        self.setGeometry(self.left, self.top, self.width, self.height)

        initepoch = self.epochs[0]
        
		# create params table
        # TODO add signal from TreeView to update table on selection
        self.tableWidget = cp.ParamsTable(initepoch)
        # FILL TABLE TO SPACE
        header = self.tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        # CREATE FIGURE
        # TODO move to class
        # a figure instance to plot on
        self.figure = Figure()
        self.ax = None

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.plot_trace(initepoch)

        # Treeview
        col0 = QVBoxLayout()
        # TODO add save button to save unchecked epochs
        self.treeWidget = cp.et.EpochTree(self.epochs, groupkeys=self.groupkeys, unchecked=self.unchecked)
        self.treeWidget.selectionModel().selectionChanged.connect(self.update_from_tree_selection)

        col0.addWidget(QLabel(
            ", ".join(self.groupkeys),
            self))
        col0.addWidget(self.treeWidget)

        # Add box layout, add table to box layout and add box layout to widget
        col1 = QVBoxLayout()
        col1.addWidget(self.toolbar)
        col1.addWidget(self.canvas)
        col1.addWidget(self.tableWidget) 

        # Combine columns
        self.layout = QHBoxLayout()
        self.layout.addLayout(col0)
        self.layout.addLayout(col1)
        self.setLayout(self.layout) 

        # Show widget
        self.show()

    def toggle_check(self, item, column):
        mdlindex = self.treeWidget.model().itemFromIndex(item)
        if item.checkState(column) == Qt.Checked:
            print(f'{item.text(column)} was checked')
        else:
            print(f'{item.text(column)} was unchecked')

    #@pyqtSlot() 
    def update_from_tree_selection(self, item: QModelIndex):
        # HACK only works with first item selected
        treeitem = self.treeWidget.model().itemFromIndex(item.indexes()[0])
        if isinstance(treeitem, cp.et.GroupItem):
            # TODO TOGGLE BETWEEN WHOLE AND SPIKE CELL TO PLOIT MEAN TRACE
            self.plot_psth(treeitem.epochs)
            self.tableWidget.update_mean(treeitem.epochs)
        else:
            self.plot_trace(treeitem.epoch)
            self.tableWidget.update(treeitem.epoch)

    def plot_psth(self, epochs: SpikeTraces):
        # TODO Add filters and apply from checks
        psth = epochs.psth
        self.ax.clear()

        self.ax.grid(True)
        self.ax.plot(np.arange(len(psth))+1, psth)
        #self.ax.title("PSTH")
        self.ax.set_ylabel("Number of spikes per second")
        self.ax.set_xlabel("Bin 10ms increments")

        self.canvas.draw()


    def plot_mean_trace(self, epochs:Traces):

        values = np.mean(
            epochs.values,
            axis=0)

        if self.ax is None:
            self.ax = self.figure.add_subplot(111)
        else:
            self.ax.clear()
        self.ax.plot(values)
        self.ax.grid(True)

        #ax.title =  epoch.startdate
        self.ax.set_ylabel("pA")
        self.ax.set_xlabel("10e-4 seconds")

        # refresh canvas
        self.canvas.draw()

    #@pyqtSlot()
    def plot_trace(self, epoch):
        ''' plot some random stuff '''

        if self.ax is None:
            self.ax = self.figure.add_subplot(111)
        else:
            self.ax.clear()
        self.ax.plot(epoch.values)
        self.ax.grid(True)

        if (
            epoch.type == "SpikeTrace"
            and epoch.spikes.sp is not None):
                y = epoch.values[epoch.spikes.sp]
                self.ax.scatter(epoch.spikes.sp, y, marker="x", c="#FFA500")

        #ax.title =  epoch.startdate
        self.ax.set_ylabel("pA")
        self.ax.set_xlabel("10e-4 seconds")

        # refresh canvas
        self.canvas.draw()
 
def run(epochs, groupbykeys=None, unchecked:set=None):
    app = QApplication(sys.argv)
    ex = App(epochs, groupbykeys, unchecked)
    sys.exit(app.exec_())  
