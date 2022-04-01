from re import S
import sys
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import \
	FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
	NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.Qt import Qt
from PyQt5.QtCore import QModelIndex, pyqtSlot, pyqtSignal 
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
							 QPushButton, QVBoxLayout, QWidget, QScrollArea,
							 QFileDialog)

from .components import MplCanvas

from ..epochtypes import SpikeEpochs, Epochs
from . import components as cp


class App(QWidget):

	def __init__(self, tree, unchecked: set=None, uncheckedpath=None):
		super().__init__()
		self.unchecked = unchecked
		self.uncheckedpath = "unchecked.csv" if uncheckedpath is None else uncheckedpath
		#self.epochs = epochs
		self.tree = tree
		self.left = 0
		self.top = 0
		self.width = 1200
		self.height = 800
		self.initUI()
		
	def initUI(self):
		self.setWindowTitle("dissonance")
		self.setGeometry(self.left, self.top, self.width, self.height)

		initepoch = self.tree.frame.epoch.iloc[0]
		
		# EPOCH TRACE INFORMATION TABLE
		self.tableWidget = cp.ParamsTable(initepoch)
		header = self.tableWidget.horizontalHeader()       
		header.setStretchLastSection(True)
		
		self.tableWidget.itemDelegate().closeEditor.connect(self.on_table_edit)

		# MATLAB NAVIGATION
		self.canvas = MplCanvas(self)
		self.toolbar = NavigationToolbar(self.canvas, self)

		# SAVE UNCHECKED FILTERS
		savebttn = QPushButton("Save filters", self)
		savebttn.clicked.connect(self.on_save_bttn_click)

		# TRACE TREE VIEWER
		treesplitlabel = QLabel(", ".join(self.tree.labels), self)
		self.treeWidget = cp.et.EpochTree(self.tree, unchecked=self.unchecked)
		self.treeWidget.selectionModel().selectionChanged.connect(self.on_tree_select)

		# FIRST COLUMNS
		col0 = QVBoxLayout()
		col0.addWidget(savebttn)
		col0.addWidget(treesplitlabel)
		col0.addWidget(self.treeWidget,10)
		col0.addWidget(self.tableWidget, 4) 
		col0.minimumSize()

		# SECOND COLUMN
		col1 = QVBoxLayout()
		col1.addWidget(self.toolbar)

		self.scroll = QScrollArea()
		self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.scroll.setWidgetResizable(True)
		self.scroll.setWidget(self.canvas)

		col1.addWidget(self.scroll)

		# COMBINE COLUMNS
		self.layout = QHBoxLayout()
		self.layout.addLayout(col0, 1)
		self.layout.addLayout(col1, 2)
		self.layout.addStretch()
		self.setLayout(self.layout) 

		# SHOW WIDGET
		self.showMaximized()
		self.show()

	def disconnect_edit(self):
		# DISCCONECT TABLE EDIT SIGNAL WHEN UPDATING TABLE
		#self.disconnect(self.tableWidget, PYQT_SIGNAL("cellChanged(int, int)"), self.DoSomething)
		...

	def connect_edit(self):
		# RECONNECT TABLE EDIT SIGNAL TO PICK UP EDITS FROM USER
		#self.connect(self.tableWidget, PYQT_SIGNAL("cellChanged(int, int)"), self.DoSomething)
		...

	def on_table_edit(self, item):
		pass
		## FROM TABLE WIDGET SEND TREE UPDATED PARAMS
		#idx = self.tableWidget.selectionModel().currentIndex()
		#row, col = idx.row(), idx.column()
		#paramname = self.tableWidget.model().index(row, 0).data()
		#value = self.tableWidget.model().index(row, 1).data()
		#startdates = self.tableWidget.df.loc[self.tableWidget.df.Param == "startdate"].Val.values

		## UPDATE EPOCHS
		#for epoch in self.epochs:
		#	if epoch.startdate in startdates:
		#		#epoch.update(paramname, value)
		#		print(epoch.startdate, paramname,value)

		## REFRESH TREE
		#self.tree.plant(self.epochs)
		#self.treeWidget.plant(self.tree)
		#print(item)

	def on_reload_tree_click(self):
		# ON BTTN CLICK, RELOAD TREE WITH UPDATED PARAMS FROM TABLE INPUT
		...

	def on_tree_select(self, item: QModelIndex):
		# UPDATE PLOT
		treeitem = self.treeWidget.model().itemFromIndex(item.indexes()[0])
		self.tree.plot(treeitem.node, self.canvas)

		epoch = self.tree.query(treeitem.node)
		self.tableWidget.update(epoch)

	@pyqtSlot()
	def on_save_bttn_click(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
		if fileName:
			print(fileName)
			(self.tree.frame.query("include == False")
				.index.get_level_values("startdate").to_series()
				.to_csv(fileName, index=False))
 
def run(tree, unchecked:set=None):
	app = QApplication(sys.argv)
	ex = App( tree, unchecked)
	sys.exit(app.exec_())  
