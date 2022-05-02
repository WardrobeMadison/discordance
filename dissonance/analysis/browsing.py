import pandas as pd
from dissonance.epochtypes.spikeepoch import SpikeEpoch

from ..epochtypes import SpikeEpochs, groupby , IEpoch, EpochBlock
from .baseanalysis import IAnalysis
from .charting import (MplCanvas, PlotCRF, PlotHill, PlotPsth, PlotRaster, PlotTrace,
                       PlotSwarm, PlotSpikeTrain)


class BrowsingAnalysis(IAnalysis):

    def __init__(self):
        # CONSTRUCT BASE, FILTER ON TRACE TYPE, LED AND PROTOCOL NAME
        self.currentplots = []

    def __str__(self):
        return type(self).__name__

    def plot(self, level:str, eframe:pd.DataFrame, canvas: MplCanvas = None):
        """Map node level to analysis run & plots created.
        """
        self.currentplots = []
        self.canvas = canvas

        if level == "startdate":
            self.plot_single_epoch(eframe, self.canvas)

    def plot_single_epoch(self, eframe: pd.DataFrame, canvas):

        epoch = eframe.epoch.iloc[0]

        axes = canvas.grid_axis(1,1)
        plttr = PlotTrace(axes[0], epoch)

        self.currentplots.append(plttr)

    @property
    def name(self): return "Browsing"

    @property
    def labels(self):
        return ["genotype", "celltype", "cellname", "protocolname", "led", "tracetype", "lightamplitude", "lightmean"]

    @property
    def tracestype(self): return EpochBlock

    @property
    def tracetype(self): return IEpoch
