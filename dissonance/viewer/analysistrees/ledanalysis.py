from typing import List, Tuple, Union, Dict, Any

from dissonance.epochtypes.spikeepoch import SpikeEpoch
from dissonance.viewer.plotting.plot import PlotSwarm

from .baseanalysis import BaseAnalysis
from ...trees import Node
from ...funks import hill
from ...epochtypes import groupby, Epochs, SpikeEpochs, filter, WholeEpoch, WholeEpochs
from ..components.chart import MplCanvas
from ..plotting import PlotPsth, PlotRaster, PlotTrace, PlotCRF


class LedWholeAnalysis(BaseAnalysis):

    def __init__(self, epochs: Epochs, unchecked: set = None):
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
        plttr = PlotTrace(axes[0], epoch)
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
            pltraster = PlotTrace(axes[axii], traces)
            axii += 1

            self.currentplots.extend([pltraster])


    def plot_genotype_summary(self, epochs, canvas):
        grps = groupby(epochs, ["cellname", "rstarr"])
        n, m = grps.shape[0], 2
        axes = canvas.grid_axis(n, m)

        ii = 0
        for _, row in grps.iterrows():
            epochs = row["trace"]
            title = f'{row["rstarr"]}'

            plt = PlotPsth(axes[ii], epochs, label=epochs.genotypes[0])
            plt.ax.set_title(title)
            self.currentplots.append(plt)
            ii += 1

            plt = PlotRaster(axes[ii], epochs)
            plt.ax.set_title(title)
            self.currentplots.append(plt)
            ii += 1

    def plot_genotype_comparison(self, epochs: Epochs, canvas: MplCanvas = None):
        """Compare epochs by genotype

        Args:
            epochs (Traces): Epochs to compare.
            canvas (MplCanvas, optional): Parent MPL canvas, figure created if not provided. Defaults to None.
        """
        df = groupby(epochs, self.labels)
        n = len(df.rstarr.unique())
        n, m = n, 3
        axes = canvas.grid_axis(n, m)

        # PEAK AMPLITUDE SWARM PLOTS IN FIRST COLUMN
        ii = 0
        for name, frame in df.groupby("rstarr"):
            plt = PlotSwarm(axes[ii], metric="peakamplitude", epochs=frame)
            ii += 3
            self.currentplots.append(plt)

        # TTP SWARM PLOTS IN Seoncd COLUMN
        ii = 1
        for name, frame in df.groupby("rstarr"):
            plt = PlotSwarm(axes[ii], metric="timetopeak", epochs=frame)
            ii += 3
            self.currentplots.append(plt)

        # OVERLAPPING PSTHS IN THIRD COLUMN
        ii = 2
        for name, frame in df.groupby("rstarr"):
            axes[ii].set_title(name)
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
        return ("protocolname", "led", "celltype", "genotype", "cellname", "rstarr")

    @property
    def tracestype(self): return WholeEpochs

    @property
    def tracetype(self): return WholeEpoch



class LedSpikeAnalysis(BaseAnalysis):

    def __init__(self, epochs: Epochs, unchecked: set = None):
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
        plttr = PlotTrace(axes[0], epoch)
        pltpsth = PlotPsth(axes[1], epoch, label=epoch.startdate)
        canvas.draw()

        self.currentplots.append(plttr)
        self.currentplots.append(pltpsth)

    def plot_genotype_summary(self, epochs, canvas):
        grps = groupby(epochs, ["cellname", "rstarr"])
        n, m = grps.shape[0], 2
        axes = canvas.grid_axis(n, m)

        ii = 0
        for _, row in grps.iterrows():
            epochs = row["trace"]
            title = f'{row["rstarr"]}'

            plt = PlotPsth(axes[ii], epochs, label=epochs.genotypes[0])
            plt.ax.set_title(title)
            self.currentplots.append(plt)
            ii += 1

            plt = PlotRaster(axes[ii], epochs)
            plt.ax.set_title(title)
            self.currentplots.append(plt)
            ii += 1

    def plot_genotype_comparison(self, epochs: Epochs, canvas: MplCanvas = None):
        """Compare epochs by genotype

        Args:
            epochs (Traces): Epochs to compare.
            canvas (MplCanvas, optional): Parent MPL canvas, figure created if not provided. Defaults to None.
        """
        df = groupby(epochs, self.labels)
        n = len(df.rstarr.unique())
        n, m = n, 3
        axes = canvas.grid_axis(n, m)

        # PEAK AMPLITUDE SWARM PLOTS IN FIRST COLUMN
        ii = 0
        for name, frame in df.groupby("rstarr"):
            plt = PlotSwarm(axes[ii], metric="peakamplitude", epochs=frame)
            ii += 3
            self.currentplots.append(plt)

        # TTP SWARM PLOTS IN Seoncd COLUMN
        ii = 1
        for name, frame in df.groupby("rstarr"):
            plt = PlotSwarm(axes[ii], metric="timetopeak", epochs=frame)
            ii += 3
            self.currentplots.append(plt)

        # OVERLAPPING PSTHS IN THIRD COLUMN
        ii = 2
        for name, frame in df.groupby("rstarr"):
            axes[ii].set_title(name)
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

    def plot_summary_epochs(self, epochs: SpikeEpochs, canvas: MplCanvas = None):
        """Plot faceted mean psth
        """
        grps = groupby(epochs, self.labels)

        n, m = grps.shape[0]+1, 2
        axes = canvas.grid_axis(n, m)
        axii = 0

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
    def name(self): return "LedSpikeAnalysis"

    @property
    def labels(self): 
        return ("protocolname", "led", "celltype", "genotype", "cellname", "rstarr")

    @property
    def tracestype(self): return SpikeEpochs

    @property
    def tracetype(self): return SpikeEpoch
