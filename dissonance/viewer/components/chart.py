import sys

import matplotlib
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

matplotlib.use('Qt5Agg')

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height),
                          dpi=dpi, constrained_layout=True)
        #self.axes = fig.add_subplot(111)
        self.axes = None
        self.m, self.n = 1, 1
        self.numaxes = self.m * self.n
        self.caxes = 0
        super(MplCanvas, self).__init__(self.fig)

    def grid_axis(self, n, m):
        self.m, self.n = m, n

        if self.axes is not None:
            self.numaxes = self.m * self.n
            self.caxes = self.numaxes
            self.fig.clf()

        self.axes = [
            self.fig.add_subplot(n, m, ii+1)
            for ii in range(n*m)]

        return self.axes

    def add_axis(self):
        self.caxes += 1
        return self.fig.add_subplot(self.n+1, self.m, self.caxes)

    def axis(self):
        self.m = 1
        self.n = 1
        self.caxes = 1
        if self.axes is None:
            self.axes = self.fig.add_subplot(111)
        else:
            self.axes.cla()
        return self.axes
