import sys
from functools import lru_cache
from pathlib import Path

from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from PyQt5.Qt import Qt
from PyQt5.QtCore import (QModelIndex, QObject, Qt, QThread, pyqtSignal,
                          pyqtSlot)
from PyQt5.QtWidgets import (QAbstractItemView, QApplication,
                             QDialog, QFileDialog, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QPushButton,
                             QScrollArea, QVBoxLayout, QWidget)

from ..analysis.charting import MplCanvas
from .. analysis import BaseAnalysis, AnalysisTree
from .epochtree import EpochTree
from .log import LoggerDialog
from .paramstable import ParamsTable


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, process, *args, **kwargs):
        super().__init__()
        self.process = process
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.process(*self.args, **self.kwargs)
            self.finished.emit()
        except Exception as e: 
            (type, value, traceback) = sys.exc_info()
            sys.excepthook(type, value, traceback)
            raise e

class CanvasWorker(QObject):
    finished = pyqtSignal()
    updatecanvas = pyqtSignal(object)
    updatetable = pyqtSignal(list)
    updatedialog = pyqtSignal(list)

    def __init__(self, nodes, tree, canvas):
        super().__init__()
        self.nodes = nodes
        self.tree = tree
        self.canvas = canvas

    def run(self):
        # PLOT NODES
        if len(self.nodes) == 1:
            if "startdate" in self.nodes[0].path.keys():
                self.canvas = self.tree.plot(self.nodes[0], self.canvas, useincludeflag=False)
                eframe = self.tree.query(filters=[node.path for node in self.nodes], useincludeflag= False)
            else:
                self.canvas = self.tree.plot(self.nodes[0], self.canvas)
                eframe = self.tree.query(filters=[node.path for node in self.nodes])
        else:
            eframe = self.tree.query(filters=[node.path for node in self.nodes])

        self.updatecanvas.emit(self.canvas)

        # UPDATE PARAMETER TABLE
        epochs = eframe.epoch.values
        self.updatetable.emit(epochs)

        # UPDATE CHARTS IN DIALOG
        self.updatedialog.emit(self.tree.currentplots)


class DissonanceUI(QWidget):

    def __init__(self, analysis: BaseAnalysis, unchecked: set = None, uncheckedpath: Path = None, export_dir: Path = None):
        super().__init__()
        # EPOCH INFORMATION
        self.unchecked = unchecked
        self.uncheckedpath = "unchecked.csv" if uncheckedpath is None else uncheckedpath
        self.export_dir = export_dir
        self.analysis = analysis
        self.tree = AnalysisTree(str(analysis), analysis.labels, analysis.frame)

        # SET WINDOW
        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 800
        self.initUI()

    def init_params_table(self):
        # EPOCH TRACE INFORMATION TABLE
        self.paramstable = ParamsTable()
        header = self.paramstable.horizontalHeader()
        header.setStretchLastSection(True)

        self.paramstable.itemDelegate().closeEditor.connect(self.on_table_edit)
        #self.paramstable.edited.connect(self.on_table_edit)

    def init_tree(self):
        # TRACE TREE VIEWER
        # TREE CONNECTIONS
        self.treeWidget = EpochTree(self.tree, unchecked=self.unchecked)
        self.treeWidget.newselection.connect(self.on_tree_select)

    def initUI(self):
        self.setWindowTitle("Dissonance")
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.init_params_table()

        # SAVE UNCHECKED FILTERS
        savebttn = QPushButton("Save filters", self)
        savebttn.clicked.connect(self.on_save_bttn_click)
        
        self.init_tree()
        treesplitlabel = QLabel(", ".join(self.tree.labels), self)
        # LABEL FOR CURRENT FILE BEING USED TO STORE STARTDATES OF UNCHECK EPOCHS
        self.filterfilelabel = QLabel(str(self.uncheckedpath))
        self.treeWidget.selectionModel().selectionChanged.connect(self.on_tree_select)

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

        self.canvas = MplCanvas(parent=self.scroll_area)
        #canvaslayout.addWidget(self.canvas)
        self.scroll_area.setWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        hbox.addWidget(self.toolbar)

        # EXPORT DATA BUTTON  
        self.exportdata_bttn = QPushButton("Export Data", self)
        self.exportdata_bttn.clicked.connect(self.on_export_bttn_click)
        hbox.addWidget(self.exportdata_bttn)

        # STAGE EXPORT DIALOG
        self.dialog = ExportDataWindow(
            parent=self, charts=None, outputdir=self.export_dir)
        self.dialog.closeEvent

        # SHOW WIDGET
        self.showMaximized()
        self.show()

        # SHOW LOGGING WINDOW
        #self.logger = LoggerDialog(self)
        #self.logger.show()
        #self.logger.exec_()

    def on_table_edit(self):
        # GET PARAMNAME AND NEW VALUE
        #paramname = vals[0]
        #value = vals[1]
        idx = self.paramstable.selectionModel().currentIndex()
        row, col = idx.row(), idx.column()
        paramname = self.paramstable.model().index(row, 0).data()
        value = self.paramstable.model().index(row, 1).data()

        if paramname.lower() in ("celltype", "genotype"):
            nodes = self.treeWidget.selected_nodes
            eframe = self.analysis.query(filters=[node.path for node in nodes])

            newframe = self.analysis.frame
            for _, row in eframe.iterrows():
                row["epoch"].update(paramname, value)
                if paramname in newframe.columns:
                    newframe.loc[newframe.startdate == row["startdate"], paramname] = value

            eframe.epoch.iloc[0]._response_ds.flush()

            # REFRESH AND REATTATCH TREE
            self.analysis.update_frame(newframe)
            self.tree = AnalysisTree(str(self.analysis), self.analysis.labels, newframe)

            self.treeWidget.fill_model(self.tree)

    def on_tree_select(self, item):

        nodes = self.treeWidget.selected_nodes

        def update_gui():
            # PLOT NODES
            if len(nodes) == 0:
                return
            elif len(nodes) == 1:
                if "startdate" in nodes[0].path.keys():
                    self.analysis.plot(nodes[0], self.canvas, useincludeflag=False)
                    eframe = self.analysis.query(filters=[node.path for node in nodes], useincludeflag= False)
                else:
                    self.analysis.plot(nodes[0], self.canvas)
                    eframe = self.analysis.query(filters=[node.path for node in nodes])
            else:
                eframe = self.analysis.query(filters=[node.path for node in nodes])

            # UPDATE PARAMETER TABLE
            epochs = eframe.epoch.values
            self.paramstable.update_rows(epochs)

            # UPDATE CHARTS IN DIALOG
            self.dialog.fill_list(self.analysis.currentplots)

        def in_sep_thread():
            self.thread = QThread()
            self.worker = Worker(update_gui)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

            # Final resets
            self.treeWidget.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection)
            self.thread.finished.connect(
                lambda: self.treeWidget.setSelectionMode(
                    QAbstractItemView.SelectionMode.ExtendedSelection)
            )
        
        def use_canvas_worker():
            nodes = self.get_nodes_from_selection()

            self.thread = QThread()
            self.worker = CanvasWorker(nodes, self.tree, self.canvas)

            self.worker.moveToThread(self.thread)

            self.worker.updatecanvas.connect(self.update_canvas)
            self.worker.updatetable.connect(self.paramstable.update_rows)
            self.worker.updatedialog.connect(self.dialog.fill_list)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()

            # Final resets
            self.treeWidget.setSelectionMode(
                QAbstractItemView.SelectionMode.NoSelection)
            self.thread.finished.connect(
                lambda: self.treeWidget.setSelectionMode(
                    QAbstractItemView.SelectionMode.ExtendedSelection)
            )

        #if __debug__:
        update_gui()
        #else:
        #in_sep_thread()
        #use_canvas_worker()

    @pyqtSlot(object)
    def update_canvas(self, canvas):
        self.canvas = canvas
        self.canvas.draw()

    @pyqtSlot()
    def on_save_bttn_click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "QFileDialog.getSaveFileName()", "", "All Files (*);;Text Files (*.txt)", options=options)
        self.uncheckedpath = fileName
        self.filterfilelabel.setText(self.uncheckedpath)
        if fileName:
            (self.tree.frame.loc[~self.tree.frame.include, "startdate"].to_csv(fileName, index=False))

    @pyqtSlot()
    def on_export_bttn_click(self):
        self.exportdata_bttn.setEnabled(False)
        charts = self.tree.currentplots
        self.dialog.fill_list(charts)
        self.dialog.show()
        self.dialog.exec_()


class ExportDataWindow(QDialog):

    def __init__(self, parent=None, charts=None, outputdir: Path = None):
        super(ExportDataWindow, self).__init__(parent)

        self.charts = list() if charts is None else charts
        self.outputdir = outputdir

        self.setWindowTitle("Options")
        self.resize(600, 600)

        # EXPORT BUTTON
        exportbttn = QPushButton("Export Selected Data")
        exportbttn.clicked.connect(self.on_export_bttn_click)

        # LIST OF CHART DATA TO EXPORT
        self.listwidget = QListWidget(self)
        self.listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.fill_list(charts)

        # WIDGET LAYOUT
        layout = QVBoxLayout()
        layout.addWidget(self.listwidget)
        layout.addWidget(exportbttn)
        self.setLayout(layout)

    @pyqtSlot(list)
    def fill_list(self, charts):
        self.listwidget.clear()
        self.charts = list() if charts is None else charts
        if len(self.charts) > 0:
            for ii, chart in enumerate(self.charts):
                item = QListWidgetItem(f"{str(chart)}")
                self.listwidget.addItem(item)

    def closeEvent(self, event):
        self.parent().exportdata_bttn.setEnabled(True)
        event.accept()

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
    ex = DissonanceUI(tree, unchecked, uncheckedpath)
    sys.exit(app.exec_())
