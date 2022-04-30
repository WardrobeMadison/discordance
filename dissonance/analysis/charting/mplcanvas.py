import sys

import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

mpl.use('Qt5Agg')
mpl.rcParams["axes.spines.right"] = False
mpl.rcParams["axes.spines.top"] = False
mpl.rcParams["xtick.top"] = False
mpl.rcParams["ytick.right"] = False
mpl.rcParams["ytick.direction"] = "in"
mpl.rcParams["xtick.direction"] = "in"

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=6, height=4, dpi=100, m:int=1, n:int=1, offline=False):
        # PLOT EITHER TO QT WINDOW OR OUT FOR TESTING
        self.offline = offline
        if self.offline:
            self.fig, self.axes = plt.subplots(m,n, tight_layout=True, figsize=(width,height))
        else:
            self.fig = Figure(constrained_layout=True, figsize=(width,height))
            self.axes = None
        
        # SET BASE DIMENSIONS OF SUBPLOT
        self.basewidth, self.baseheight = width, height

        # CREATE PARENT CLASS
        self.myparent = parent
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)
        
        # SET INTIIAL AXIS 
        self.m, self.n = m, n
        self.numaxes = self.m * self.n
        self.caxes = 1
        self.axes = self.grid_axis(n,m)

    def __getitem__(self, val):
        return self.axes[val]

    def __iter__(self):
        yield from self.axes

    def grid_axis(self, n:int, m:int):
        """Create grid axis rows x cols (n x m)"""
        self.m, self.n = m, n
        self.numaxes = self.m * self.n
        self.caxes = self.numaxes

        if self.axes is not None:
            self.axes.clear()
            self.fig.clf()

        # ADJUST WIDTH AND HEIGHT OF CHART BASE ON NUMBER OF SUBPLOTS
        self.currentheight = self.baseheight*n
        if not self.offline:
            viewwidth = self.parent().width() / 100
            self.currentwidth =  (viewwidth if (viewwidth < self.basewidth * m) else self.basewidth * m) - 1 # PADDING FOR WIDTH
        else:
            self.currentwidth = self.basewidth * m

        self.fig.set_size_inches((self.currentwidth, self.currentheight), forward=True)
        self.setFixedHeight(self.currentheight*100)
        self.setFixedWidth(self.currentwidth*100)

        # ADD SUBPLOT FOR EACH GRID
        self.axes = [
            self.fig.add_subplot(n, m, ii+1)
            for ii in range(n*m)]

        return self.axes

    def draw(self, *args, **kwargs):
        if self.offline:
            plt.show()
        else:
            super().draw()
