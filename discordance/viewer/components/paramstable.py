from typing import Union
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import pandas as pd

from ... import io
from ... import epochtypes as et


class ParamsTable(QTableWidget):

	params = [
		"cellname",
		"lightamplitude",
		"lightmean",
		"pretime",
		"samplerate",
		"stimtime",
		"tailtime",
		"startdate",
		"enddate"
	]

	def __init__(self, epoch: Union[et.SpikeTrace, et.WholeTrace]):
		super().__init__()

		self.update(epoch)
		# TABLE SELECTION CHANGE
		self.doubleClicked.connect(self.on_click)

	@pyqtSlot()
	def update(self, epoch):
		"""Update params table with epoch 

		Args:
			ii (int): Index row of epoch in dataframe
		"""
		# TODO should this be a model?
		#self.data.clear()

		self.setRowCount(0)
		self.setRowCount(len(self.params))
		self.setColumnCount(2)

		for ii, paramname in enumerate(self.params):
				self.setItem(ii,0,
					QTableWidgetItem(paramname))
				self.setItem(ii,1, 
					QTableWidgetItem(str(getattr(epoch, paramname))))

	@pyqtSlot()
	def on_click(self):
		print("\n")
		for currentQTableWidgetItem in self.selectedItems():
			print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
