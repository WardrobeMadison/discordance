from typing import Union
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout, QTableView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import pandas as pd

from ... import io
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

	def __init__(self, epoch: Union[et.SpikeTrace, et.WholeTrace]):
		super().__init__()

		self.update(epoch)


	
	@pyqtSlot()
	def update(self, epoch: Union[et.ITrace, et.Traces]):
		"""Update params table with epoch 

		Args:
			ii (int): Index row of epoch in dataframe
		"""
		#self.data.clear()
		self.setRowCount(0)
		self.setRowCount(len(self.params))
		self.setColumnCount(2)

		if isinstance(epoch, et.Traces):
			for ii, paramname in enumerate(self.params):
				self.setItem(ii,0,
					QTableWidgetItem(paramname))
				text = set(getattr(epoch, paramname+"s"))
				self.setItem(ii,1, 
					QTableWidgetItem(",".join(map(str,text))))
		else:
			for ii, paramname in enumerate(self.params):
				self.setItem(ii,0,
					QTableWidgetItem(paramname))
				self.setItem(ii,1, 
					QTableWidgetItem(str(getattr(epoch, paramname))))
	
