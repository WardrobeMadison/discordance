import pandas as pd
from dissonance.epochtypes.spikeepoch import SpikeEpoch

from ..epochtypes import SpikeEpochs, groupby , IEpoch, EpochBlock
from .baseanalysis import IAnalysis
from .charting import (MplCanvas, PlotCRF, PlotHill, PlotPsth, PlotRaster, PlotTrace, PlotWholeTrace,
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
        elif level == "lightmean":
            self.plot_summary_epochs(eframe, self.canvas)
        elif level == "lightamplitude":
            self.plot_summary_epochs(eframe, self.canvas)

    def plot_single_epoch(self, eframe: pd.DataFrame, canvas):

        epoch = eframe.epoch.iloc[0]
        axes = canvas.grid_axis(1,1)
        plttr = PlotTrace(axes[0], epoch)
        self.currentplots.append(plttr)

    def plot_summary_epochs(self, eframe: pd.DataFrame, canvas: MplCanvas = None):
        """Plot faceted mean psth
        """

        if eframe.tracetype.iloc[0] == "spiketrace":
            grps = groupby(eframe, self.labels)
            n, m = grps.shape[0], 2
            axes = canvas.grid_axis(n, m)
            axii = 0

            for ii, row in grps.iterrows():
                cepochs = row["epoch"]

                # FIRST COLUMN
                pltpsth = PlotPsth(axes[axii], cepochs,
                                cepochs.get_unique("cellname")[0])
                axii += 1

                # SECOND COLUMN
                pltraster = PlotRaster(axes[axii], cepochs)
                axii += 1

                self.currentplots.extend([pltpsth, pltraster])

        elif eframe.tracetype.iloc[0] == "wholetrace":
            grps = groupby(eframe, self.labels)
            n, m = grps.shape[0], 2
            axes = canvas.grid_axis(n, m)
            axii = 0

            grps = groupby(eframe, self.labels)

            # BUILD GRID
            n = grps.shape[0]
            axes = canvas.grid_axis(n, 1)
            axii = 0

            # PLOT AVERAGE TRACE FOR EACH LIGHT AMP AND MEAN COMBO
            for ii, row in grps.iterrows():
                epochs = row["epoch"]

                pltraster = PlotWholeTrace(axes[axii], epochs)
                axii += 1

                self.currentplots.extend([pltraster])

    @property
    def name(self): return "Browsing"

    @property
    def labels(self):
        return ["genotype", "celltype", "cellname", "protocolname", "led", "tracetype", "backgroundval", "lightamplitude", "lightmean"]

    @property
    def tracestype(self): return EpochBlock

    @property
    def tracetype(self): return IEpoch
