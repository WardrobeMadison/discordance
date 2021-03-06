import sys
from functools import lru_cache
from pathlib import Path

from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from PyQt5.Qt import Qt
from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QDialog,
                             QFileDialog, QHBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)

from ..analysis import EpochIO, IAnalysis
from ..analysis.charting import MplCanvas
from .epochtree import EpochTreeWidget
from .exportwindow import ExportDataWindow
from .graphwidget import GraphWidget
from .paramstable import ParamsTable


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, process):
        super().__init__()
        self.process = process

    @pyqtSlot(str, object)
    def plot(self, level, eframe):
        self.process(level, eframe)
        self.finished.emit()


class DissonanceUI(QWidget):

    def __init__(self, epochio: EpochIO, analysis: IAnalysis, unchecked: set = None, uncheckedpath: Path = None, export_dir: Path = None):
        super().__init__()
        # EPOCH INFORMATION
        self.unchecked = unchecked
        self.uncheckedpath = "unchecked.csv" if uncheckedpath is None else uncheckedpath
        self.export_dir = export_dir

        # SET GEOMETRY
        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 800

        # INIT UI
        self.initUI(epochio, analysis)

    def initUI(self, epochio, analysis):
        self.setWindowTitle("Dissonance")
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.initParamsTable()

        # SAVE UNCHECKED FILTERS
        savebttn = QPushButton("Save filters", self)
        savebttn.clicked.connect(self.on_save_bttn_click)

        self.treeWidget = EpochTreeWidget(
            str(analysis), analysis.labels, epochio, unchecked=self.unchecked)
        treesplitlabel = QLabel(", ".join(self.treeWidget.tree.labels), self)
        # LABEL FOR CURRENT FILE BEING USED TO STORE STARTDATES OF UNCHECK EPOCHS
        self.filterfilelabel = QLabel(str(self.uncheckedpath))

        # SET LAYOUT
        # COMBINE COLUMNS
        col0 = QVBoxLayout()
        col1 = QVBoxLayout()
        self.layout = QHBoxLayout()
        self.layout.addLayout(col0, 1)
        self.layout.addLayout(col1, 2)
        self.layout.addStretch()
        self.setLayout(self.layout)

        # FIRST COLUMNS
        col0.addWidget(savebttn)
        col0.addWidget(self.filterfilelabel)
        col0.addWidget(treesplitlabel)
        col0.addWidget(self.treeWidget, 10)
        col0.addWidget(self.paramstable, 4)
        col0.minimumSize()

        # SECOND COLUMN
        hbox = QHBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.horizontalScrollBar().setEnabled(False)
        self.scroll_area.setWidgetResizable(True)

        col1.addLayout(hbox)
        col1.addWidget(self.scroll_area)

        canvas = MplCanvas(self.scroll_area)
        self.graphWidget = GraphWidget(analysis, canvas=canvas)
        self.toolbar = NavigationToolbar(canvas, self)

        # EXPORT DATA BUTTON
        self.exportdata_bttn = QPushButton("Export Data", self)

        # SECOND COLUMN WIDGETS
        hbox.addWidget(self.toolbar)
        hbox.addWidget(self.exportdata_bttn)
        self.scroll_area.setWidget(self.graphWidget)

        # STAGE EXPORT DIALOG
        self.dialog = ExportDataWindow(
            parent=self, charts=None, outputdir=self.export_dir)
        self.dialog.closeEvent

        self.initConnections()

        # SHOW WIDGET
        self.showMaximized()
        self.show()

        # SHOW LOGGING WINDOW
        #self.logger = LoggerDialog(self)
        # self.logger.show()
        # self.logger.exec_()

# region WIDGETS*****************************************************************
    def initParamsTable(self):
        # EPOCH TRACE INFORMATION TABLE
        self.paramstable = ParamsTable()
        header = self.paramstable.horizontalHeader()
        header.setStretchLastSection(True)

    def initConnections(self):
        self.treeWidget.newSelection.connect(self.updateTableOnTreeSelect)
        self.paramstable.rowEdited.connect(self.treeWidget.updateTree)
        self.exportdata_bttn.clicked.connect(self.on_export_bttn_click)

        # PLOT ON A SEPARATE THREAD
        thread = QThread(self)
        self.graphWidget.moveToThread(thread)
        thread.start()

        # ADD THREAD CONNECTIONS
        self.treeWidget.newSelectionForPlot.connect(self.graphWidget.plot)
        self.graphWidget.redrawCanvas.connect(self.redrawCanvas)

# endregion

# region SLOTS*******************************************************************
    @pyqtSlot()
    def redrawCanvas(self):
        self.graphWidget.canvas.draw()

    @pyqtSlot(object)
    def updateTableOnTreeSelect(self, eframe):
        epochs = eframe.epoch.values
        self.paramstable.onNewEpochs(epochs)
        self.dialog.fillList(self.graphWidget.currentplots)

    @pyqtSlot()
    def on_save_bttn_click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "QFileDialog.getSaveFileName()", "", "All Files (*);;Text Files (*.txt)", options=options)
        self.uncheckedpath = fileName
        self.filterfilelabel.setText(self.uncheckedpath)
        if fileName:
            (self.analysis.frame.loc[~self.analysis.frame.include, "startdate"].to_csv(
                fileName, index=False))

    @pyqtSlot()
    def on_export_bttn_click(self):
        self.exportdata_bttn.setEnabled(False)
        charts = self.analysis.currentplots
        self.dialog.fillList(charts)
        self.dialog.show()
        self.dialog.exec_()
# endregion


def run(epochio, analysis, unchecked, uncheckedpath: Path = None):
    app = QApplication(sys.argv)
    ex = DissonanceUI(epochio, analysis, unchecked, uncheckedpath)
    sys.exit(app.exec_())
