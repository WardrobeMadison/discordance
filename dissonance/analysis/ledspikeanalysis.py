import pandas as pd
from dissonance.epochtypes.spikeepoch import SpikeEpoch

from ..epochtypes import SpikeEpochs, groupby
from .baseanalysis import IAnalysis
from .charting import (MplCanvas, PlotCRF, PlotHill, PlotPsth, PlotRaster,
                       PlotSwarm, PlotSpikeTrain)


class LedSpikeAnalysis(IAnalysis):

    def __init__(self):
        # CONSTRUCT BASE, FILTER ON TRACE TYPE, LED AND PROTOCOL NAME
        self.currentplots = []

    def __str__(self):
        return type(self).__name__

    def plot(self, level:str, eframe:pd.DataFrame, canvas: MplCanvas = None):
        """Map node level to analysis run & plots created.
        """
        self.currentplots = []
        if level == "startdate":
            self.plot_single_epoch(eframe, canvas)
        elif level == "lightamplitude":
            self.plot_summary_epochs(eframe, canvas)
        elif level == "lightmean":
            # TODO light mean analysis - analyze faceted light amplitudes
            ...
        elif level == "cellname":
            self.plot_summary_cell(eframe, canvas)
        elif level == "genotype":
            self.plot_genotype_summary(eframe, canvas)
        elif level == "celltype":
            self.plot_genotype_comparison(eframe, canvas)

    def plot_single_epoch(self, eframe: pd.DataFrame, canvas):

        epoch = eframe.epoch.iloc[0]

        axes = canvas.grid_axis(1, 2)
        plttr = PlotSpikeTrain(axes[0], epoch)
        pltpsth = PlotPsth(axes[1], epoch, label=epoch.startdate)

        self.currentplots.append(plttr)
        self.currentplots.append(pltpsth)

    def plot_genotype_summary(self, eframe: pd.DataFrame, canvas):
        grps = groupby(eframe, self.labels)

        # PLOT FIT GRAPHS IN FIRST ROW IF NEEDED
        led = grps.led.iloc[0]
        protocolname = grps.protocolname.iloc[0]
        if led.lower() == "uv led" and protocolname.lower() == "ledpulse":
            # ADD AN EXTRA HEADER ROW FOR GRID SHAPE
            #n, m = grps.shape[0]+1, 2
            n, m = 1, 2
            axes = canvas.grid_axis(n, m)
            axii = 2

            # TODO iterate by lightmean
            plt_amp = PlotCRF(axes[0], metric="peakamplitude", eframe=grps)
            plt_ttp = PlotCRF(axes[1], metric="timetopeak", eframe=grps)

            self.currentplots.extend([plt_amp, plt_ttp])

        elif led.lower() == "green led" and protocolname.lower() == "ledpulsefamily":
            # ADD AN EXTRA HEADER ROW FOR GRID SHAPE
            #n, m = grps.shape[0]+1, 2
            # TODO iterate by lightmean
            n, m = 1, 2
            axes = canvas.grid_axis(n, m)
            axii = 2

            plt_amp = PlotHill(axes[0], eframe=grps)
            #plt_ttp = PlotHill(axes[1], metric="timetopeak", epochs=grps)
            self.currentplots.extend([plt_amp])

    def plot_genotype_comparison(self, epochs: pd.DataFrame, canvas: MplCanvas = None):
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
            self.currentplots.append(plt)

        # TTP SWARM PLOTS IN Seoncd COLUMN
        ii = 1
        for name, frame in df.groupby(["lightamplitude", "lightmean"]):
            plt = PlotSwarm(axes[ii], metric="timetopeak", eframe=frame)
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

    def plot_summary_cell(self, eframe: pd.DataFrame, canvas: MplCanvas = None):
        """Plot faceted mean psth
        """
        # DIFFERENT ROW FEACH EACH CELL, RSTARR
        grps = groupby(eframe, self.labels)
        n, m = grps.shape[0], 2
        axes = canvas.grid_axis(n, m)
        axii = 0

        # ITERATE FOR EVERY LIGHTAMPLITUDE, LIGHTMEAN COMBO
        for ii, row in grps.iterrows():
            epochs = row["epoch"]

            # FIRST COLUMN
            pltpsth = PlotPsth(axes[axii], epochs, label=str(row["cellname"]))
            pltpsth.ax.set_title(f"({row.lightamplitude}, {row.lightmean})")
            axii += 1

            # SECOND COLUMN
            pltraster = PlotRaster(axes[axii], epochs)
            pltraster.ax.set_title(f"({row.lightamplitude}, {row.lightmean})")
            axii += 1

            self.currentplots.extend([pltpsth, pltraster])

    def plot_summary_epochs(self, eframe: pd.DataFrame, canvas: MplCanvas = None):
        """Plot faceted mean psth
        """
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

    @property
    def name(self): return "LedSpikeAnalysis"

    @property
    def labels(self):
        return ["protocolname", "led", "celltype", "genotype", "cellname", "lightmean", "lightamplitude"]

    @property
    def tracestype(self): return SpikeEpochs

    @property
    def tracetype(self): return SpikeEpoch
