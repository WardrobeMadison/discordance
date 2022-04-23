from email.headerregistry import Group

from PyQt5.Qt import QStandardItem, QStandardItemModel, Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTreeView

from ...trees.base import Node, Tree


class GroupItem(QStandardItem):
    def __init__(self, node: Node, color=QColor(0, 0, 0)):
        super(QStandardItem, self).__init__()
        self.node = node
        fnt = QFont()
        fnt.setBold(True)
        fnt.setPixelSize(11)

        self.label = ", ".join(map(str, self.node.path.values()))

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(self.label)

        self.setFlags(self.flags() | Qt.ItemIsSelectable)


class EpochItem(QStandardItem):
    def __init__(self, node: Node, number:int, color=QColor(0, 0, 0)):
        super().__init__()

        self.node = node
        fnt = QFont()
        fnt.setPixelSize(10)
        self.label = node.uid
        self.number  = number

        self.setEditable(False)
        self.setForeground(color)
        self.setBackground(QColor(187, 177, 189))
        self.setFont(fnt)
        # self.setText(epoch.startdate)
        self.setText(f"Epoch{number}")

        self.setFlags(self.flags() | Qt.ItemIsUserCheckable |
                      Qt.ItemIsSelectable)
        self.setCheckState(Qt.Checked)


class EpochTree(QTreeView):

    def __init__(self, at: Tree, unchecked: set = None):
        self.unchecked = set() if unchecked is None else unchecked
        super().__init__()
        self.setHeaderHidden(True)

        self.plant(at)
        self.model().itemChanged.connect(self.toggle_check)

        self.set_initial_collapse()

    def set_initial_collapse(self):
        # TODO make expoch layer not collapsed
        print("here")
        ...

    def plant(self, at):
        self.at = at

        treeModel = QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        # TRANSLATE TREE TO Qt Items ITEMS
        root = GroupItem(at)
        self.add_items(at, root)
        rootNode.appendRow(root)

        self.setModel(treeModel)
        #self.expandAll()

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
                self.at.frame.index.get_level_values(
                    "startdate") == item.label,
                "include"
            ] = True

            item.setBackground(QColor(187, 177, 189))
        # EXCLUDE EPOCH
        else:
            self.at.frame.loc[
                self.at.frame.index.get_level_values(
                    "startdate") == item.label,
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
                item = EpochItem(node, ii)
                if self.unchecked is not None:
                    if node.uid in self.unchecked:
                        item.setCheckState(Qt.Unchecked)
                parentitem.appendRow(item)
            else:
                item = GroupItem(node)
                parentitem.appendRow(item)
                self.add_items(node, item)
