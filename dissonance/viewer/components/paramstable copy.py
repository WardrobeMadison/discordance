from typing import Union
from PyQt5.QtWidgets import QTableWidgetItem, QTableView
from PyQt5.QtCore import pyqtSlot, QAbstractTableModel, Qt
import pandas as pd

from ... import io
from ... import epochtypes as et

class ParamsTableModel(QAbstractTableModel):

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
		self._data = epoch

		self.update(epoch)

		self.model().chang

	def rowCount(self, index):
		return len(self.params)

	def columnCount(self, index):
		return 2

	def data(self, index, role=Qt.DisplayRole):
		if index.isValid():
			if role == Qt.DisplayRole or role == Qt.EditRole:
				value = self._data[index.row(), index.column()]
				return str(value)

	def setData(self, index, value, role):
		if role == Qt.EditRole:
			try:
				value = int(value)
			except ValueError:
				return False

			self._data[index.row(), index.column()] = value
			return True
		return False

	def flags(self, index):
		return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
	
	@pyqtSlot()
	def update_mean(self, epochs):
		self.setRowCount(0)
		self.setRowCount(len(self.params))
		self.setColumnCount(2)

		for ii, paramname in enumerate(self.params):
			self.setItem(ii,0,
				QTableWidgetItem(paramname))
			text = set(getattr(epochs, paramname+"s"))
			self.setItem(ii,1, 
				QTableWidgetItem(",".join(map(str,text))))

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
	
