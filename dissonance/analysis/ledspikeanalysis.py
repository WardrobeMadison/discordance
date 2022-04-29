from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
import pandas as pd

from dissonance.epochtypes.spikeepoch import SpikeEpoch

from ..epochtypes import (EpochBlock, SpikeEpochs, WholeEpoch, WholeEpochs,
                          filter, groupby)
from ..funks import hill
from ..trees import Node
from .baseanalysis import BaseAnalysis
from .charting import (MplCanvas, PlotCRF, PlotHill, PlotPsth, PlotRaster,
                       PlotTrace, PlotWeber, PlotWholeTrace, PlotSwarm)

class LedSpikeAnalysis(BaseAnalysis):

    def __init__(self, params:pd.DataFrame, experimentpaths:List[Path], unchecked: set = None):
        # CONSTRUCT BASE, FILTER ON TRACE TYPE, LED AND PROTOCOL NAME
        super().__init__(
            params,
            experimentpaths,
            unchecked)

        # USED IN SAVING PLOTS AND EXPORTING` DATA
        self.plotmap = dict()
        self.currentplots = []

    def plot(self, node: Node, canvas: MplCanvas = None):
        """Map node level to analysis run & plots created.
        """
        self.currentplots = []

        scope = list(node.path.keys())
        level = len(scope)

        epochs = self.query(node)

        # STARTDATE
        if node.isleaf:
            self.plot_single_epoch(epochs, canvas)
        # light amplitude
        elif level == 8:
            self.plot_summary_epochs(epochs, canvas)
        # light mean
        elif level == 7:
            #TODO light mean anlaysis - analyze faceted light amplitudes
            ...
        # CELLNAME
        elif level == 6:
            self.plot_summary_cell(epochs, canvas)
        # GENOTYPE
        elif level == 5:
            self.plot_genotype_summary(epochs, canvas)
        # CELLTYPE
        elif level == 4:
            self.plot_genotype_comparison(epochs, canvas)

        canvas.draw()

    def plot_single_epoch(self, epoch, canvas):

        axes = canvas.grid_axis(1, 2)
        plttr = PlotTrace(axes[0], epoch)
        pltpsth = PlotPsth(axes[1], epoch, label=epoch.startdate)
        canvas.draw()

        self.currentplots.append(plttr)
        self.currentplots.append(pltpsth)

    def plot_genotype_summary(self, epochs, canvas):
        grps = groupby(epochs, self.labels)

        # PLOT FIT GRAPHS IN FIRST ROW IF NEEDED
        led = grps.led.iloc[0]
        protocolname = grps.protocolname.iloc[0]
        if led.lower() == "uv led" and protocolname.lower() == "ledpulse":
            # ADD AN EXTRA HEADER ROW FOR GRID SHAPE
            #n, m = grps.shape[0]+1, 2
            n,m = 1, 2
            axes = canvas.grid_axis(n, m)
            axii = 2

            plt_amp = PlotCRF(axes[0], metric="peakamplitude", epochs=grps)
            plt_ttp = PlotCRF(axes[1], metric="timetopeak", epochs=grps)

            self.currentplots.extend([plt_amp, plt_ttp])

        elif led.lower() == "green led" and protocolname.lower() == "ledpulsefamily":
            # ADD AN EXTRA HEADER ROW FOR GRID SHAPE
            #n, m = grps.shape[0]+1, 2
            n,m = 1, 2
            axes = canvas.grid_axis(n, m)
            axii = 2

            plt_amp = PlotHill(axes[0], epochs=grps)
            #plt_ttp = PlotHill(axes[1], metric="timetopeak", epochs=grps)
            self.currentplots.extend([plt_amp])

    def plot_genotype_comparison(self, epochs: EpochBlock, canvas: MplCanvas = None):
        """Compare epochs by genotype

        Args:
            epochs (Traces): Epochs to compare.
            canvas (MplCanvas, optional): Parent MPL canvas, figure created if not provided. Defaults to None.
        """
        df = groupby(epochs, self.labels)
        n = len(set(zip(df.lightamplitude, df.lightmean)))
        n, m = n, 3
        axes = canvas.grid_axis(n, m)

        # PEAK AMPLITUDE SWARM PLOTS IN FIRST COLUMN
        ii = 0
        for name, frame in df.groupby(["lightamplitude", "lightmean"]):
            plt = PlotSwarm(axes[ii], metric="peakamplitude", epochs=frame)
            ii += 3
            self.currentplots.append(plt)

        # TTP SWARM PLOTS IN Seoncd COLUMN
        ii = 1
        for name, frame in df.groupby(["lightamplitude", "lightmean"]):
            plt = PlotSwarm(axes[ii], metric="timetopeak", epochs=frame)
            ii += 3
            self.currentplots.append(plt)

        # OVERLAPPING PSTHS IN THIRD COLUMN
        ii = 2
        for name, frame in df.groupby(["lightamplitude", "lightmean"]):
            axes[ii].set_title(name)
            plt = PlotPsth(axes[ii])
            for geno, fframe in frame.groupby("genotype"):
                # SHOULD ONLY BE ONE GENOTYPE HERE
                epoch = fframe.iloc[0, -1]
                plt.append_trace(epoch, label=geno)
            self.currentplots.append(plt)
            ii += 3

    def plot_summary_cell(self, epochs: SpikeEpochs, canvas: MplCanvas = None):
        """Plot faceted mean psth
        """
        # DIFFERENT ROW FEACH EACH CELL, RSTARR
        grps = groupby(epochs, self.labels)
        n, m = grps.shape[0], 2
        axes = canvas.grid_axis(n, m)
        axii = 0

        # ITERATE FOR EVERY LIGHTAMPLITUDE, LIGHTMEAN COMBO
        for ii, row in grps.iterrows():
            traces = row["trace"]

            # FIRST COLUMN
            pltpsth = PlotPsth(axes[axii], traces, epochs.get_unique("cellname")[0])
            axii += 1

            # SECOND COLUMN
            pltraster = PlotRaster(axes[axii], traces)
            axii += 1

            self.currentplots.extend([pltpsth, pltraster])

    def plot_summary_epochs(self, epochs: SpikeEpochs, canvas: MplCanvas = None):
        """Plot faceted mean psth
        """
        grps = groupby(epochs, self.labels)

        n, m = grps.shape[0]+1, 2
        axes = canvas.grid_axis(n, m)
        axii = 0

        for ii, row in grps.iterrows():
            cepochs = row["trace"]

            # FIRST COLUMN
            pltpsth = PlotPsth(axes[axii], cepochs, epochs.get_unique("cellname")[0])
            axii += 1

            # SECOND COLUMN
            pltraster = PlotRaster(axes[axii], cepochs)
            axii += 1

            self.currentplots.extend([pltpsth, pltraster])

    @property
    def name(self): return "LedSpikeAnalysis"

    @property
    def labels(self):
        return ["protocolname", "led", "celltype", "genotype", "cellname", "lightmean", "lightamplitude"]

    @property
    def tracestype(self): return SpikeEpochs

    @property
    def tracetype(self): return SpikeEpoch

    def get_args(self, node):
        # TODO get arguments needed for gui from plotting functions like fit params
        level = len(node.path.values()) - 1
        func = self.plotmap[level]

