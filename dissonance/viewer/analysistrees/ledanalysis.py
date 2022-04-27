from typing import List, Tuple, Union, Dict, Any

from dissonance.epochtypes.spikeepoch import SpikeEpoch
from dissonance.viewer.plot import PlotSwarm

from .baseanalysis import BaseAnalysis
from ...trees import Node
from ...funks import hill
from ...epochtypes import groupby, EpochBlock, SpikeEpochs, filter, WholeEpoch, WholeEpochs
from ..components.chart import MplCanvas
from ..plot import PlotPsth, PlotRaster, PlotTrace, PlotCRF, PlotWholeTrace, PlotHill


class LedWholeAnalysis(BaseAnalysis):

    def __init__(self, epochs: EpochBlock, unchecked: set = None):
        # CONSTRUCT BASE, FILTER ON TRACE TYPE, LED AND PROTOCOL NAME
        epochs_ = filter(epochs, tracetype="wholetrace")
        super().__init__(
            epochs_,
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
        elif level == 7:
            self.plot_summary_epochs(epochs, canvas)
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
        plttr = PlotWholeTrace(axes[0], epoch)
        canvas.draw()

        self.currentplots.append(plttr)

    def plot_summary_epochs(self, epochs: SpikeEpochs, canvas: MplCanvas = None):
        """Plot faceted mean trace
        """
        grps = groupby(epochs, self.labels)

        n, m = grps.shape[0]+1, 2
        axes = canvas.grid_axis(n, m)
        axii = 0

        for ii, row in grps.iterrows():
            traces = row["trace"]

            # SECOND COLUMN
            pltraster = PlotWholeTrace(axes[axii], traces)
            axii += 1

            self.currentplots.extend([pltraster])

    def plot_genotype_summary(self, epochs, canvas):
        """Plot three chart columns - Peak ampltiude, width at half max, average trace"""
        grps = groupby(epochs, ["celltype", "lightamplitude", "lightmean"])
        n, m = grps.shape[0], 3
        axes = canvas.grid_axis(n, m)

        # FIRST COLUMN - PEAK AMPLITUDE
        ii = 0
        for rstarr, row in grps.groupby(["lightamplitude", "lightmean"]):
           cepochs = row["trace"]
           plt = PlotPsth(axes[ii], cepochs, label=cepochs.get("genotype")[0])
           plt.ax.set_title(rstarr)
           self.currentplots.append(plt)
           ii += 2

        # SECOND COLUMN - WIDTH AT HALF MAX
        ii = 1
        grps = groupby(epochs, ["lightamplitude", "lightmean"])
        for _, epoch in grps.iterrows():
            cepoch = row["trace"]
            plt = PlotRaster(axes[ii], cepoch)
            self.currentplots.append(plt)
            ii += 2

        # THIRD COLUMN - AVERAGE TRACE
        ii = 2
        grps = groupby([epochs, "lightamplitude", "lightmean"])
        for _, row in grps.iterrows():
            cepoch = row["trace"]
            plt = PlotWholeTrace(axes[ii], cepoch)
            self.currentplots.append(plt)
            ii += 2

    def plot_genotype_comparison(self, epochs: EpochBlock, canvas: MplCanvas = None):
        """Compare epochs by genotype

        Args:
            epochs (Traces): Epochs to compare.
            canvas (MplCanvas, optional): Parent MPL canvas, figure created if not provided. Defaults to None.
        """
        df = groupby(epochs, self.labels)
        n = len(df[["lightamplitude", "lightmean"]].unique())
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

                plt = PlotPsth(axes[ii], epoch, label=geno)
                self.currentplots.append(plt)
            ii += 3

    def plot_summary_cell(self, epochs: SpikeEpochs, canvas: MplCanvas = None):
        """Plot faceted mean psth
        """
        # DIFFERENT ROW FEACH EACH CELL, RSTARR
        grps = groupby(epochs, self.labels)

        n, m = grps.shape[0]+1, 2
        axes = canvas.grid_axis(n, m)
        axii = 2

        led = grps.led.iloc[0]
        if led.lower() == "uv led":
            plt_amp = PlotCRF(axes[0], metric="peakamplitude", epochs=grps)
            plt_ttp = PlotCRF(axes[1], metric="timetopeak", epochs=grps)
            self.currentplots.extend([plt_amp, plt_ttp])
        else:
            ...

        for ii, row in grps.iterrows():
            traces = row["trace"]

            # FIRST COLUMN
            pltpsth = PlotPsth(axes[axii], traces, epochs.cellnames[0])
            axii += 1

            # SECOND COLUMN
            pltraster = PlotRaster(axes[axii], traces)
            axii += 1

            self.currentplots.extend([pltpsth, pltraster])

    @property
    def name(self): return "LedWholeAnalysis"

    @property
    def labels(self):
        return ("protocolname", "led", "celltype", "genotype", "cellname", "lightamplitude", "lightmean")

    @property
    def tracestype(self): return WholeEpochs

    @property
    def tracetype(self): return WholeEpoch


class LedSpikeAnalysis(BaseAnalysis):

    def __init__(self, epochs: EpochBlock, unchecked: set = None):
        # CONSTRUCT BASE, FILTER ON TRACE TYPE, LED AND PROTOCOL NAME
        epochs_ = filter(epochs, tracetype="spiketrace")
        super().__init__(
            epochs_,
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
            n, m = grps.shape[0]+1, 2
            axes = canvas.grid_axis(n, m)
            axii = 2

            plt_amp = PlotCRF(axes[0], metric="peakamplitude", epochs=grps)
            plt_ttp = PlotCRF(axes[1], metric="timetopeak", epochs=grps)
            self.currentplots.extend([plt_amp, plt_ttp])

        elif led.lower() == "green led" and protocolname.lower() == "ledpulsefamily":
            # ADD AN EXTRA HEADER ROW FOR GRID SHAPE
            n, m = grps.shape[0]+1, 2
            axes = canvas.grid_axis(n, m)
            axii = 2

            plt_amp = PlotHill(axes[0], epochs=grps)
            #plt_ttp = PlotHill(axes[1], metric="timetopeak", epochs=grps)
            self.currentplots.extend([plt_amp, plt_ttp])

        else:
            n, m = grps.shape[0], 2
            axes = canvas.grid_axis(n, m)
            axii = 0

        # PLOT EVERY CELL AND RASTER (CELLNAME, RSTARR)
        #ii = 0
        #for _, row in grps.iterrows():
        #    cepochs = row["trace"]
        #    title = f'{row["cellname"]}: {row["lightamplitude"]}, {row["lightmean"]}'

        #    plt = PlotPsth(axes[ii], cepochs, label=row["genotype"])
        #    plt.ax.set_title(title)
        #    self.currentplots.append(plt)
        #    ii += 1

        #    cepochs = row["trace"]
        #    plt = PlotRaster(axes[ii], cepochs)
        #    plt.ax.set_title(title)
        #    self.currentplots.append(plt)
        #    ii += 1

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
        return ("protocolname", "led", "celltype", "genotype", "cellname", "lightmean", "lightamplitude")

    @property
    def tracestype(self): return SpikeEpochs

    @property
    def tracetype(self): return SpikeEpoch
