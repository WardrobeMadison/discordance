from typing import Any, Dict, List, Tuple, Union
import pandas as pd
from pathlib import Path

from dissonance.epochtypes.spikeepoch import SpikeEpoch

from ..epochtypes import (EpochBlock, SpikeEpochs, WholeEpoch, WholeEpochs,
                          filter, groupby)
from ..funks import hill
from ..trees import Node
from .baseanalysis import BaseAnalysis
from .charting import (MplCanvas, PlotCRF, PlotHill, PlotPsth, PlotRaster,
                       PlotTrace, PlotWeber, PlotWholeTrace)

class LedWholeAnalysis(BaseAnalysis):

    def __init__(
        self, params:pd.DataFrame, experimentpaths:List[Path], unchecked: set = None):
        # CONSTRUCT BASE, FILTER ON TRACE TYPE, LED AND PROTOCOL NAME
        super().__init__(
            params,
            experimentpaths,
            unchecked)

        # USED IN SAVING PLOTS AND EXPORTING DATA
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
        # RSTARR
        elif level == 8:
            self.plot_summary_epochs(epochs, canvas)
        # LIGHTMEAN
        elif level == 7:
            self.plot_summary_epochs(epochs, canvas)
        # LIGHT AMPLITUDE
        elif level == 6:
            self.plot_summary_epochs(epochs, canvas)
        # GENOTYPE
        elif level == 5:
            self.plot_genotype_summary(epochs, canvas)
        # CELLTYPE
        elif level == 4:
            self.plot_genotype_comparison(epochs, canvas)

        canvas.draw()

    def plot_single_epoch(self, epoch, canvas):

        axes = canvas.grid_axis(1, 1)
        plttr = PlotWholeTrace(axes[0], epoch)
        canvas.draw()

        self.currentplots.append(plttr)

    def plot_summary_epochs(self, epochs: WholeEpochs, canvas: MplCanvas = None):
        """Plot faceted mean trace
        """
        # GROUP EPOCHS UP TO LIGHT AMP AND MEAN
        grps = groupby(epochs, self.labels)

        # BUILD GRID
        n = grps.shape[0]
        axes = canvas.grid_axis(n, 1)
        axii = 0

        # PLOT AVERAGE TRACE FOR EACH LIGHT AMP AND MEAN COMBO
        for ii, row in grps.iterrows():
            traces = row["trace"]

            pltraster = PlotWholeTrace(axes[axii], traces)
            axii += 1

            self.currentplots.extend([pltraster])

    def plot_genotype_summary(self, epochs, canvas):
        """
        Plot initial row for fit data CRF, Weber and Hill. 
        Then plot mean traces faceted by light amplitude and lightmean.
        """
        grps = groupby(epochs, self.labels)

        # PLOT FIT GRAPHS IN FIRST ROW IF NEEDED
        led = grps.led.iloc[0]
        protocolname = grps.protocolname.iloc[0]
        if led.lower() == "uv led" and protocolname.lower() == "ledpulse":
            # ADD EXTRA HEADER ROWS FOR GRID SHAPE - ONE FOR EACH LIGHT MEAN
            n, m = len(set(zip(grps.lightamplitude, grps.lightmean))) + len(grps.lightmean.unique()), 1
            axes = canvas.grid_axis(n, m)
            axii = 0

            for lightmean, frame in grps.groupby("lightmean"):
                plt = PlotCRF(axes[axii], metric="peakamplitude", epochs=frame)
                plt.ax.set_title(f"Light Mean = {lightmean}")
                axii += 1

                self.currentplots.extend([plt])

        elif led.lower() == "green led" and protocolname.lower() == "ledpulsefamily":
            # ADD AN EXTRA HEADER ROW FOR GRID SHAPE
            n, m = len(set(zip(grps.lightamplitude, grps.lightmean))) + len(grps.lightmean.unique())*2, 1
            axes = canvas.grid_axis(n, m)
            axii = 0

            for lightmean, frame in grps.groupby("lightmean"):

                plt_amp = PlotHill(axes[axii], epochs=grps)
                plt_amp.ax.set_title(f"Light Mean = {lightmean}")
                axii += 1
                
                plt_wbr = PlotWeber(axes[axii], epochs=grps)
                plt_wbr.ax.set_title(f"Light Mean = {lightmean}")
                axii += 1

                self.currentplots.extend([plt_amp, plt_wbr])
        else:
            n, m = len(set(zip(grps.lightamplitude, grps.lightmean))), 1
            axes = canvas.grid_axis(n, m)
            axii = 0

        # AVERAGE TRACE ON EVERY PLOT
        ## ITERATE THROUGH EVERY AMP X MEAN COMBO
        for (lightamp, lightmean), frame in grps.groupby(["lightamplitude", "lightmean"]):
            plt = PlotWholeTrace(axes[axii])
            
            # APPEND THE AVERAGE TRACE FOR EACH CELL
            for _, row in frame.iterrows():
                plt.append_trace(row["trace"])

            plt.ax.set_title(f"LightAmp={lightamp}, LightMean={lightmean}")

            self.currentplots.append(plt)
            axii += 1

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
        for (lightamp, lightmean), frame in df.groupby(["lightamplitude", "lightmean"]):
            axes[ii].set_title(f"{lightamp},{lightmean}")
            for geno, fframe in frame.groupby("genotype"):
                # SHOULD ONLY BE ONE GENOTYPE HERE
                epoch = fframe.iloc[0, -1]

                plt = PlotWholeTrace(axes[ii], epoch)
                self.currentplots.append(plt)
            ii += 3


    @property
    def name(self): return "LedWholeAnalysis"

    @property
    def labels(self):
        return ["protocolname", "led", "celltype", "genotype", "cellname", "lightamplitude", "lightmean"]

    @property
    def tracestype(self): return WholeEpochs

    @property
    def tracetype(self): return WholeEpoch
