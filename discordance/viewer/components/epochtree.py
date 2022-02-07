import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView
from PyQt5.Qt import Qt, QStandardItem, QStandardItemModel
from PyQt5.QtGui import QFont, QColor
import pandas as pd
from PyQt5.QtCore import pyqtSlot

class EpochHeader(QStandardItem):
    def __init__(self, txt='', color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont()
        fnt.setBold(True)
        fnt.setPixelSize(12)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)

class EpochItem(QStandardItem):
    def __init__(self, txt='', color=QColor(0, 0, 0)):
        super().__init__()

        fnt = QFont()
        fnt.setPixelSize(11)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)

        self.setFlags( Qt.ItemIsUserCheckable)
        #self.setFlags(Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Checked)


class EpochTree(QTreeView):

    def __init__(self, epochs: pd.DataFrame):
        super().__init__()

        self.setHeaderHidden(True)

        treeModel = QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        for name, grp in epochs.groupby(["Type","CellName"]):
            print(name)
            # HEAD NODE 
            head = EpochHeader(str(name)) 

            for epoch in grp.Epoch.values:
                subitem = EpochItem(epoch.startdate)
                head.appendRow(subitem)

            rootNode.appendRow(head)

        self.setModel(treeModel)
        #self.expandAll()
