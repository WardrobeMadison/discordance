from datetime import datetime
from lib2to3.pytree import Base
from PyQt5.Qt import QStandardItem, QStandardItemModel, Qt, QAbstractItemView
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTreeView

from dissonance.analysis.analysistree import AnalysisTree
from dissonance.analysis.baseanalysis import EpochIO

from ..analysis.trees.base import Node, Tree
from ..analysis import IAnalysis


class RootItem(QStandardItem):
    def __init__(self, node: Node, color=QColor(0, 0, 0)):
        super(QStandardItem, self).__init__()
        self.node = node
        fnt = QFont()
        fnt.setBold(True)
        fnt.setPixelSize(12)

        self.label = f"{node.label}={node.uid}"

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(self.label)
        self.setFlags(self.flags() & ~Qt.ItemIsSelectable)

class GroupItem(QStandardItem):
    def __init__(self, node: Node, color=QColor(0, 0, 0)):
        super(QStandardItem, self).__init__()
        self.node = node
        fnt = QFont()
        fnt.setBold(True)
        fnt.setPixelSize(12)

        #self.label = ", ".join(map(str, self.node.path.values()))
        #self.label = list(self.node.path.values())[-1]
        self.label = f"{node.label}={node.uid}"

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(self.label)

        self.setFlags(self.flags() | Qt.ItemIsSelectable)

class EpochItem(QStandardItem):
    def __init__(self, node: Node, color=QColor(0, 0, 0)):
        super().__init__()

        self.node = node
        fnt = QFont()
        fnt.setPixelSize(12)
        self.label = node.uid

        self.setEditable(False)
        self.setForeground(color)
        self.setBackground(QColor(187, 177, 189))
        self.setFont(fnt)
        # self.setText(epoch.startdate)
        self.setText(f"startdate={self.label}")

        self.setFlags(self.flags() | Qt.ItemIsUserCheckable |
                      Qt.ItemIsSelectable)
        self.setCheckState(Qt.Checked)


class EpochTreeWidget(QTreeView):

    newSelection = pyqtSignal(object)
    newSelectionForPlot = pyqtSignal(str, object)

    def __init__(self, name, splits, epochio: EpochIO, unchecked: set = None):
        super().__init__()
        self.name = name
        self.splits = splits
        self.setHeaderHidden(True)

        self.unchecked = set() if unchecked is None else unchecked
        self.epochio = epochio

        self.createModel(epochio)
        self.initConnections()

    def initConnections(self):
        self.model().itemChanged.connect(self.onCheckToggle)
        self.selectionModel().selectionChanged.connect(self.onTreeSelect)

    def createModel(self, epochio: EpochIO):
        self.treeModel = QStandardItemModel()
        self.setModel(self.treeModel)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.plantTree(epochio)

    def plantTree(self, epochio: EpochIO):
        self.tree = epochio.to_tree(self.name, self.splits)
        # REMOVE DATA CURRENTLY IN TREE MODEL
        self.treeModel.removeRows(0, self.treeModel.rowCount())
        # TRANSLATE TREE TO Qt Items ITEMS
        rootNode = self.treeModel.invisibleRootItem()
        root = RootItem(self.tree)
        self.addItems(self.tree, root)
        rootNode.appendRow(root)

    @pyqtSlot(str, object)
    def updateTree(self, paramname, value):
        self.epochio.update(
            filters = [node.path for node in self.selectedNodes],
            paramname = paramname, value = value)

        # REFRESH AND REATTATCH TREE
        self.plantTree(self.epochio)

    #@pyqtSlot()
    def onCheckToggle(self, item: QStandardItem):
        """Update unchecked list on toggle

        Args:
                item (QStandardItem): Selected tree node
        """
        # INCLUDE EPOCH
        if item.checkState() == Qt.Checked:
            if item.label in self.unchecked:
                self.unchecked.remove(item.label)

            self.at.frame.loc[
                self.at.frame.startdate == item.label,
                "include"
            ] = True

            item.setBackground(QColor(187, 177, 189))
        # EXCLUDE EPOCH
        else:
            self.at.frame.loc[
                self.at.frame.startdate == item.label,
                "include"
            ] = False
            self.unchecked.add(item.label)
            item.setBackground(QColor(255, 255, 255, 0))

    def addItems(self, parentnode: Node, parentitem: QStandardItem):
        """Translate nodes of tree to QT items for treeview

        Args:
                parentnode (Node): Node in tree
                parentitem (QStandardItem): Node in QtTreeView
        """
        for ii, node in enumerate(parentnode):
            if node.isleaf:
                item = EpochItem(node)
                if self.unchecked is not None:
                    if node.uid in self.unchecked:
                        item.setCheckState(Qt.Unchecked)
                parentitem.appendRow(item)
            else:
                item = GroupItem(node)
                parentitem.appendRow(item)
                self.addItems(node, item)

    @property
    def selectedNodes(self):
        # SELECT V MULTI SELECT
        idxs = self.selectedIndexes()
        nodes = []
        if len(idxs) == 1:
            treeitem = self.model().itemFromIndex(idxs[0])
            nodes.append(treeitem.node)
        else:
            nodes = [self.model().itemFromIndex(
                idx).node for idx in idxs]
        return nodes

    @pyqtSlot()
    def onTreeSelect(self):
        # SELECT V MULTI SELECT
        #self.newselection.emit(self.selected_nodes)
        nodes = self.selectedNodes
        if len(nodes) == 0:
            eframe = None
        elif len(nodes) == 1:
            if "startdate" in nodes[0].path.keys():
                eframe = self.epochio.query(filters=[node.path for node in nodes], useincludeflag=False)
            else:
                eframe = self.epochio.query(filters=[node.path for node in nodes])
        else:
            eframe = self.epochio.query(filters=[node.path for node in nodes])

        self.newSelection.emit(eframe)
        if len(nodes) == 1:
            self.newSelectionForPlot.emit(nodes[0].label, eframe)
