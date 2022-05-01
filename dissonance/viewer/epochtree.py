from datetime import datetime
from PyQt5.Qt import QStandardItem, QStandardItemModel, Qt, QAbstractItemView
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTreeView

from dissonance.analysis.analysistree import AnalysisTree

from ..analysis.trees.base import Node, Tree



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


class EpochTree(QTreeView):

    newselection = pyqtSignal(list)

    def __init__(self, at: AnalysisTree, unchecked: set = None):
        self.unchecked = set() if unchecked is None else unchecked
        super().__init__()
        self.setHeaderHidden(True)

        self.plant(at)

        # connections
        #self.selectionModel().selectionChanged.connect(self.on_tree_select)
        self.model().itemChanged.connect(self.toggle_check)

    def plant(self, at: AnalysisTree):

        self.treeModel = QStandardItemModel()
        self.setModel(self.treeModel)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.fill_model(at)

    def fill_model(self, at: AnalysisTree):
        self.at = at
        # REMOVE DATA CURRENTLY IN TREE MODEL
        self.treeModel.removeRows( 0, self.treeModel.rowCount())
        # TRANSLATE TREE TO Qt Items ITEMS
        rootNode = self.treeModel.invisibleRootItem()
        root = RootItem(at)
        self.add_items(at, root)
        rootNode.appendRow(root)

    def toggle_check(self, item: QStandardItem):
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

    def add_items(self, parentnode: Node, parentitem: QStandardItem):
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
                self.add_items(node, item)

    @property
    def selected_nodes(self):
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

    def on_tree_select(self):
        # SELECT V MULTI SELECT
        #self.newselection.emit(self.selected_nodes)
        return self.selected_nodes