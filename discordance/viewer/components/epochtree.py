from email.headerregistry import Group
import sys
from typing import List
import itertools

import pandas as pd
from PyQt5.Qt import QStandardItem, QStandardItemModel, Qt, QModelIndex
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView

from ...epochtypes import ITrace, Traces, SpikeTraces, groupby
from ...trees.base import Tree

class HeaderItem(QStandardItem):
	def __init__(self, name, color=QColor(0, 0, 0)):
		super().__init__()

		fnt = QFont()
		fnt.setBold(True)
		fnt.setPixelSize(12)

		self.setEditable(False)
		self.setForeground(color)
		self.setFont(fnt)
		self.setText(str(name))

		self.setFlags(self.flags() | Qt.ItemIsSelectable)

class GroupItem(QStandardItem):
	def __init__(self, name, epochs: Traces, color=QColor(0, 0, 0)):
		super().__init__()

		self.epochs = epochs

		fnt = QFont()
		fnt.setBold(True)
		fnt.setPixelSize(11)

		self.setEditable(False)
		self.setForeground(color)
		self.setFont(fnt)
		self.setText(str(name))

		self.setFlags(self.flags() | Qt.ItemIsSelectable)


class EpochItem(QStandardItem):
	def __init__(self, epoch: ITrace, color=QColor(0, 0, 0)):
		super().__init__()

		self.epoch = epoch

		fnt = QFont()
		fnt.setPixelSize(10)

		self.setEditable(False)
		self.setForeground(color)
		self.setBackground(QColor(187,177,189))
		self.setFont(fnt)
		self.setText(epoch.startdate)

		self.setFlags(self.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
		self.setCheckState(Qt.Checked)

class EpochTree(QTreeView):

	def __init__(self, epochs: Traces, groupkeys=["protocolname", "celltype", "cellname", "lightamplitude", "lightmean"], unchecked:set=None):
		super().__init__()

		self.setHeaderHidden(True)
		self.unchecked = set() if unchecked is None else unchecked

		treeModel = QStandardItemModel()
		rootNode = treeModel.invisibleRootItem()

		for name, grp in groupby(epochs, groupkeys):
			print(name)
			# HEAD NODE 
			head = GroupItem(name, grp)

			for epoch in grp.traces:
				subitem = EpochItem(epoch)
				if unchecked is not None:
					if epoch.startdate in unchecked:
						subitem.setCheckState(Qt.Unchecked)
				head.appendRow(subitem)

			rootNode.appendRow(head)
		# TODO change to on selection, not item changed
		#self.expandAll()
		self.setModel(treeModel)
		treeModel.itemChanged.connect(self.toggle_check)
		self.model()

	def toggle_check(self, item:QStandardItem):
		if item.checkState() == Qt.Checked:
			# ADD TRACE TO PARENT
			traces = [trace for trace in item.parent().epochs.traces]
			traces.append(item.epoch)
			if item.parent().epochs.type=="spiketrace":
				item.parent().epochs = SpikeTraces(item.parent().epochs.key, traces)
			else:
				...

			if item.epoch.startdate in self.unchecked:
				self.unchecked.remove(item.epoch.startdate)

			item.setBackground(QColor(187,177,189))
		else: 
			# REMOVE TRACE TO PARENT
			# TODO need to remove from all parent groups
			traces = [trace for trace in item.parent().epochs.traces if trace != item.epoch]
			if item.parent().epochs.type=="spiketrace":
				item.parent().epochs = SpikeTraces(item.parent().epochs.key, traces)
			else:
				...
			self.unchecked.add(item.epoch.startdate)
			item.setBackground(QColor(255, 255, 255, 0))
