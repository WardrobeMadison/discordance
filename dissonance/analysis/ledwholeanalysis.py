from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import pandas as pd

from ..epochtypes import EpochBlock, WholeEpoch, WholeEpochs, groupby
from .trees import Node
from .baseanalysis import IAnalysis
from .charting import (MplCanvas, PlotCRF, PlotHill, PlotSwarm, PlotWeber,
                       PlotWholeTrace)


class LedWholeAnalysis(IAnalysis):

    def __init__(self):
        self.currentplots = []

    def __str__(self):
        return type(self).__name__

    def plot(self, level: str, eframe:pd.DataFrame, canvas: MplCanvas = None):
        """Map node level to analysis run & plots created.
        """
        self.currentplots = []

        if level == "startdate":
            self.plot_single_epoch(eframe, canvas)
        elif level == "lightmean":
            self.plot_summary_epochs(eframe, canvas)
        elif level == "lightamplitude":
            self.plot_summary_epochs(eframe, canvas)
        elif level == "cellname":
            self.plot_summary_cell(eframe, canvas)
        elif level == "genotype":
            self.plot_genotype_summary(eframe, canvas)
        elif level == "celltype":
            self.plot_genotype_comparison(eframe, canvas)

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
        # PLOT FIT GRAPHS IN FIRST EXTRA ROWS IF NEEDED
        df = groupby(epochs, self.labels)
        led = df.led.iloc[0]
        protocolname = df.protocolname.iloc[0]
        n = len(set(zip(df.lightamplitude, df.lightmean)))
        m = 3

        if led.lower() == "uv led" and protocolname.lower() == "ledpulse":
            # ADD EXTRA HEADER ROWS FOR GRID SHAPE - ONE FOR EACH LIGHT MEAN
            n += len(df.lightmean.unique())
            axes = canvas.grid_axis(n, m)
            axii = 0

            for lightmean, frame in df.groupby("lightmean"):
                plt = PlotCRF(axes[axii], metric = "peakamplitude")

                # APPEND TRACE FOR EACH GENOTYPE
                for geno, frame2 in frame.groupby("genotype"):
                    plt.append_trace(frame2)

                plt.ax.set_title(f"Light Mean = {lightmean}")

                self.currentplots.extend([plt])
                axii += 3

        elif led.lower() == "green led" and protocolname.lower() == "ledpulsefamily":
            # ADD AN EXTRA HEADER ROW FOR GRID SHAPE
            n, m = len(set(zip(df.lightamplitude, df.lightmean))
                       ) + len(df.lightmean.unique())*2, 1
            axes = canvas.grid_axis(n, m)
            axii = 0

            for lightmean, frame in df.groupby("lightmean"):
                plt_amp = PlotHill(axes[axii])
                plt_wbr = PlotWeber(axes[axii+1])

                # APPEND TRACE FOR EACH h
                for geno, frame2 in frame.groupby("genotype"):
                    plt_amp.append_trace(frame2)
                    plt_wbr.append_trace(frame2)

                plt_amp.ax.set_title(f"Light Mean = {lightmean}")
                plt_wbr.ax.set_title(f"Light Mean = {lightmean}")

                self.currentplots.extend([plt_amp,plt_wbr])
                # THERE ARE THREE COLUMNS - THESE ARE ONLY COVERING TWO
                axii += 3
        else:
            n, m = len(set(zip(df.lightamplitude, df.lightmean))), 1
            axes = canvas.grid_axis(n, m)
            axii = 0

        # PEAK AMPLITUDE SWARM PLOTS IN FIRST COLUMN
        ii = 0 + axii
        for name, frame in df.groupby(["lightamplitude", "lightmean"]):
            plt = PlotSwarm(axes[ii], metric="peakamplitude", eframe=frame)
            ii += 3
            plt.ax.set_title(f"PA: {name}")
            self.currentplots.append(plt)

        # TTP SWARM PLOTS IN SECOND COLUMN
        ii = 1 + axii
        for name, frame in df.groupby(["lightamplitude", "lightmean"]):
            plt = PlotSwarm(axes[ii], metric="timetopeak", eframe=frame)
            plt.ax.set_title(f"TTP: {name}")
            ii += 3
            self.currentplots.append(plt)

        # OVERLAPPING PSTHS IN THIRD COLUMN
        ii = 2 + axii
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
