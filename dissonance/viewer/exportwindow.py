from pathlib import Path

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QAbstractItemView, QDialog, QListWidget,
                             QListWidgetItem, QPushButton, QVBoxLayout)


class ExportDataWindow(QDialog):

    def __init__(self, parent=None, charts=None, outputdir: Path = None):
        super(ExportDataWindow, self).__init__(parent)

        self.charts = list() if charts is None else charts
        self.outputdir = outputdir

        self.setWindowTitle("Options")
        self.resize(600, 600)

        # EXPORT BUTTON
        exportbttn = QPushButton("Export Selected Data")
        exportbttn.clicked.connect(self.onExportBttnClick)

        # LIST OF CHART DATA TO EXPORT
        self.listwidget = QListWidget(self)
        self.listwidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.fillList(charts)

        # WIDGET LAYOUT
        layout = QVBoxLayout()
        layout.addWidget(self.listwidget)
        layout.addWidget(exportbttn)
        self.setLayout(layout)

    @pyqtSlot(list)
    def fillList(self, charts):
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
    def onExportBttnClick(self):
        for index in self.listwidget.selectedIndexes():
            try:
                self.charts[index.row()].to_csv(outputdir=self.outputdir)
            except:
                ...
        self.close()
