import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QHeaderView, QHBoxLayout
from PyQt5.QtCore import pyqtSlot
import pandas as pd

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from . import components as cp
from ..funks import charting

class App(QWidget):
    title = 'Discordance'

    def __init__(self, epochs: pd.DataFrame):
        super().__init__()
        self.epochs = epochs
        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 800
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        initepoch = self.epochs.Epoch.iloc[0]
        
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
        self.treeWidget = cp.EpochTree(self.epochs)
        self.treeWidget.doubleClicked.connect(self.update_from_tree_selection)


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

    #@pyqtSlot() 
    def update_from_tree_selection(self, val):
        startdate = val.data()
        epoch = self.epochs.loc[
            self.epochs.Epoch.apply(lambda x: x.startdate == startdate),
            "Epoch"].iloc[0]
        self.plot_trace(epoch)
        self.tableWidget.update(epoch)


    #@pyqtSlot()
    def plot_trace(self, epoch):
        ''' plot some random stuff '''
        # random data
        # create an axis

        if self.ax is None:
            self.ax = self.figure.add_subplot(111)
        else:
            self.ax.clear()
        self.ax.plot(epoch.values)
        self.ax.grid(True)

        if epoch.type == "SpikeTrace":
            y = epoch.values[epoch.spikes.sp]
            self.ax.scatter(epoch.spikes.sp, y, marker="x", c="#FFA500")

        #ax.title =  epoch.startdate
        self.ax.set_ylabel("pA")
        self.ax.set_xlabel("10e-4 seconds")

        # refresh canvas
        self.canvas.draw()
 
def run(epochs):
    app = QApplication(sys.argv)
    ex = App(epochs)
    sys.exit(app.exec_())  
