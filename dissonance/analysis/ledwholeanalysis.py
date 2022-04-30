from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import pandas as pd

from ..epochtypes import EpochBlock, WholeEpoch, WholeEpochs, groupby
from ..trees import Node
from .baseanalysis import BaseAnalysis
from .charting import (MplCanvas, PlotCRF, PlotHill, PlotSwarm, PlotWeber,
                       PlotWholeTrace)


class LedWholeAnalysis(BaseAnalysis):

    def __init__(
            self, params: pd.DataFrame, experimentpaths: List[Path], unchecked: set = None):
        # CONSTRUCT BASE, FILTER ON TRACE TYPE, LED AND PROTOCOL NAME
        super().__init__(
            params,
            experimentpaths,
            unchecked)

        # USED IN SAVING PLOTS AND EXPORTING DATA
        self.currentplots = []

    def plot(self, node: Node, canvas: MplCanvas = None, useincludeflag=True):
        """Map node level to analysis run & plots created.
        """
        self.currentplots = []

        scope = list(node.path.keys())
        level = len(scope)

        epochs = self.query(filters=[node.path], useincludeflag=useincludeflag)

        # STARTDATE
        if node.isleaf:
            self.plot_single_epoch(epochs, canvas)
        # LIGHTMEAN
        elif level == 9:
            self.plot_summary_epochs(epochs, canvas)
        # LIGHT AMPLITUDE
        elif level == 8:
            self.plot_summary_epochs(epochs, canvas)
        # LIGHT CELL NAME
        elif level == 7:
            self.plot_summary_cell(epochs, canvas)
        # GENOTYPE
        elif level == 6:
            self.plot_genotype_summary(epochs, canvas)
        # CELLTYPE
        elif level == 5:
            self.plot_genotype_comparison(epochs, canvas)

        canvas.draw()

    def plot_single_epoch(self, eframe, canvas):
        epoch = eframe.epoch.iloc[0]
        axes = canvas.grid_axis(1, 1)
        plttr = PlotWholeTrace(axes[0], epoch)
        canvas.draw()

        self.currentplots.append(plttr)

    def plot_summary_epochs(self, eframe: pd.DataFrame, canvas: MplCanvas = None):
        """Plot faceted mean trace
        """
        # GROUP EPOCHS UP TO LIGHT AMP AND MEAN
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

    def plot_summary_cell(self, eframe: pd.DataFrame, canvas: MplCanvas = None):
        """Plot faceted mean trace
        """
        # GROUP EPOCHS UP TO LIGHT AMP AND MEAN
        grps = groupby(eframe, self.labels)

        # BUILD GRID
        n = grps.shape[0]
        axes = canvas.grid_axis(n, 1)
        axii = 0

        # PLOT AVERAGE TRACE FOR EACH LIGHT AMP AND MEAN COMBO
        for ii, row in grps.iterrows():
            epochs = row["epoch"]

            pltraster = PlotWholeTrace(axes[axii], epochs)
            pltraster.ax.set_title(
                f"({row['lightamplitude'], row['lightmean']})")
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
            n, m = len(set(zip(grps.lightamplitude, grps.lightmean))
                       ) + len(grps.lightmean.unique()), 1
            axes = canvas.grid_axis(n, m)
            axii = 0

            for lightmean, frame in grps.groupby("lightmean"):
                plt = PlotCRF(axes[axii], metric="peakamplitude", eframe=frame)
                plt.ax.set_title(f"Light Mean = {lightmean}")
                axii += 1

                self.currentplots.extend([plt])

        elif led.lower() == "green led" and protocolname.lower() == "ledpulsefamily":
            # ADD AN EXTRA HEADER ROW FOR GRID SHAPE
            n, m = len(set(zip(grps.lightamplitude, grps.lightmean))
                       ) + len(grps.lightmean.unique())*2, 1
            axes = canvas.grid_axis(n, m)
            axii = 0

            for lightmean, frame in grps.groupby("lightmean"):

                plt_amp = PlotHill(axes[axii], eframe=grps)
                plt_amp.ax.set_title(f"Light Mean = {lightmean}")
                axii += 1

                plt_wbr = PlotWeber(axes[axii], eframe=grps)
                plt_wbr.ax.set_title(f"Light Mean = {lightmean}")
                axii += 1

                self.currentplots.extend([plt_amp, plt_wbr])
        else:
            n, m = len(set(zip(grps.lightamplitude, grps.lightmean))), 1
            axes = canvas.grid_axis(n, m)
            axii = 0

        # AVERAGE TRACE ON EVERY PLOT
        # ITERATE THROUGH EVERY AMP X MEAN COMBO
        for (lightamp, lightmean), frame in grps.groupby(["lightamplitude", "lightmean"]):
            plt = PlotWholeTrace(axes[axii], cellsummary=True)

            # APPEND THE AVERAGE TRACE FOR EACH CELL
            for _, row in frame.iterrows():
                plt.append_trace(row["epoch"])

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
            plt = PlotSwarm(axes[ii], metric="peakamplitude", eframe=frame)
            ii += 3
            plt.ax.set_title(f"PA: {name}")
            self.currentplots.append(plt)

        # TTP SWARM PLOTS IN Seoncd COLUMN
        ii = 1
        for name, frame in df.groupby(["lightamplitude", "lightmean"]):
            plt = PlotSwarm(axes[ii], metric="timetopeak", eframe=frame)
            plt.ax.set_title(f"TTP: {name}")
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
                plt.ax.set_title(name)
                self.currentplots.append(plt)
            ii += 3

    @property
    def name(self): return "LedWholeAnalysis"

    @property
    def labels(self):
        return ["holdingpotential", "protocolname", "led", "celltype", "genotype", "cellname", "lightamplitude", "lightmean"]

    @property
    def tracestype(self): return WholeEpochs

    @property
    def tracetype(self): return WholeEpoch
