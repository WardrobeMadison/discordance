import sys
from pathlib import Path

from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar)
from PyQt5.Qt import Qt
from PyQt5.QtCore import QModelIndex, pyqtSlot
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QFileDialog,
                             QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
                             QPushButton, QScrollArea, QVBoxLayout, QWidget)
from functools import lru_cache

from . import components as cp


class App(QWidget):

    def __init__(self, tree, unchecked: set = None, uncheckedpath: Path = None, export_dir: Path = None):
        super().__init__()
        # EPOCH INFORMATION
        self.unchecked = unchecked
        self.uncheckedpath = "unchecked.csv" if uncheckedpath is None else uncheckedpath
        self.export_dir = export_dir
        self.tree = tree

        # SET WINDOW
        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 800
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Dissonance")
        self.setGeometry(self.left, self.top, self.width, self.height)

        initepoch = self.tree.frame.epoch.iloc[0]

        # EPOCH TRACE INFORMATION TABLE
        self.tableWidget = cp.ParamsTable(initepoch)
        header = self.tableWidget.horizontalHeader()
        header.setStretchLastSection(True)

        self.tableWidget.itemDelegate().closeEditor.connect(self.on_table_edit)

        # SAVE UNCHECKED FILTERS
        savebttn = QPushButton("Save filters", self)
        savebttn.clicked.connect(self.on_save_bttn_click)

        # TRACE TREE VIEWER
        treesplitlabel = QLabel(", ".join(self.tree.labels), self)
        self.treeWidget = cp.et.EpochTree(self.tree, unchecked=self.unchecked)
        self.treeWidget.selectionModel().selectionChanged.connect(self.on_tree_select)

        self.filterfilelabel = QLabel(str(self.uncheckedpath))

        # FIRST COLUMNS
        col0 = QVBoxLayout()
        col0.addWidget(savebttn)
        col0.addWidget(self.filterfilelabel)
        col0.addWidget(treesplitlabel)
        col0.addWidget(self.treeWidget, 10)
        col0.addWidget(self.tableWidget, 4)
        col0.minimumSize()

        # SECOND COLUMN
        col1 = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.horizontalScrollBar().setEnabled(False)

        self.canvas = cp.MplCanvas(self.scroll_area)
        self.toolbar = NavigationToolbar(self.canvas, self)

        exportdata = QPushButton("Export Data", self)
        exportdata.clicked.connect(self.on_export_bttn_click)

        hbox = QHBoxLayout()
        hbox.addWidget(self.toolbar)
        hbox.addWidget(exportdata)

        # ADD WIDGETS
        self.scroll_area.setWidget(self.canvas)
        col1.addLayout(hbox)
        col1.addWidget(self.scroll_area)

        # COMBINE COLUMNS
        self.layout = QHBoxLayout()
        self.layout.addLayout(col0, 1)
        self.layout.addLayout(col1, 2)
        self.layout.addStretch()
        self.setLayout(self.layout)

        # SHOW WIDGET
        self.showMaximized()
        self.show()

    def on_table_edit(self, item):
        # GET PARAMNAME AND NEW VALUE
        idx = self.tableWidget.selectionModel().currentIndex()
        row, col = idx.row(), idx.column()
        paramname = self.tableWidget.model().index(row, 0).data()
        value = self.tableWidget.model().index(row, 1).data()

        if paramname.lower() in ("celltype", "genotype"):
            nodes = self.get_nodes_from_selection()
            epochs = self.tree.query(nodes)

            # UPDATE EPOCHS
            if len(nodes) > 1:
                for epoch in epochs:
                    epoch.update(paramname, value)
                    #print(epoch.startdate, paramname,value)

                # TODO wrap this into epochs object? how to handle updates?
                epochs[0]._response_ds.flush()
            else:
                epoch.update(paramname, value)
                epochs._response_ds.flush()

            # REFRESH AND REATTATCH TREE
            # TODO make updating work refresh tree
            self.tree.tracetype
            self.tree = type(self.tree)(self.tree.tracestype(
                self.tree.frame["epoch"].to_list()))
            self.treeWidget.fill_model(self.tree)

    def get_nodes_from_selection(self):
        # SELECT V MULTI SELECT
        idxs = self.treeWidget.selectedIndexes()
        nodes = []
        if len(idxs) == 1:
            treeitem = self.treeWidget.model().itemFromIndex(idxs[0])
            nodes.append(treeitem.node)
        else:
            nodes = [self.treeWidget.model().itemFromIndex(
                idx).node for idx in idxs]
        return nodes

    def on_tree_select(self, item: QModelIndex):
        # SELECT V MULTI SELECT
        nodes = self.get_nodes_from_selection()

        if len(nodes) == 1:
            self.tree.plot(nodes[0], self.canvas)

        epoch = self.tree.query(nodes)
        self.tableWidget.update(epoch)

    @pyqtSlot()
    def on_save_bttn_click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "QFileDialog.getSaveFileName()", "", "All Files (*);;Text Files (*.txt)", options=options)
        self.uncheckedpath = fileName
        self.filterfilelabel.setText(self.uncheckedpath)
        if fileName:
            print(fileName)
            (self.tree.frame.query("include == False")
                .index.get_level_values("startdate").to_series()
                .to_csv(fileName, index=False))

    @pyqtSlot()
    def on_export_bttn_click(self):
        charts = self.tree.currentplots
        dialog = ExportDataWindow(charts=charts, outputdir=self.export_dir)
        dialog.show()


class ExportDataWindow(QWidget):

    def __init__(self, charts=None, outputdir: Path = None):
        super(ExportDataWindow, self).__init__()

        self.charts = charts
        self.outputdir = outputdir

        # EXPORT BUTTON
        exportbttn = QPushButton("Export Selected Data")
        exportbttn.clicked.connect(self.on_export_bttn_click)

        # LIST OF CHART DATA TO EXPORT
        self.listwidget = QListWidget(self)
        for ii, chart in enumerate(charts):
            item = QListWidgetItem(f"{type(chart)}_{ii}")
            self.listwidget.addItem(item)

        self.listwidget.setSelectionMode(QAbstractItemView.MultiSelection)

        # WIDGET LAYOUT
        layout = QVBoxLayout()
        layout.addWidget(self.listwidget)
        layout.addWidget(exportbttn)
        self.setLayout(layout)

    @pyqtSlot()
    def on_export_bttn_click(self):
        for index in self.listwidget.selectedIndexes():
            try:
                self.charts[index.row()].to_csv(outputdir=self.outputdir)
            except:
                ...
        self.close()


def run(tree, unchecked, uncheckedpath: Path = None):
    app = QApplication(sys.argv)
    ex = App(tree, unchecked, uncheckedpath)
    sys.exit(app.exec_())
