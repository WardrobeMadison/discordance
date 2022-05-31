from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import pandas as pd

from dissonance.analysis.charting.plot import PlotTrace, PlotWeberCoeff

from ..epochtypes import EpochBlock, groupby, ChirpEpochs, ChirpEpoch
from .trees import Node
from .baseanalysis import IAnalysis
from .charting import (MplCanvas, PlotHill, PlotSwarm, PlotWeber,
                       PlotWholeTrace, PlotWholeCRF, PlotCellWeber)


class ChirpAnalysis(IAnalysis):

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
        elif level == "cellname":
            self.plot_summary_cell(eframe, canvas)
        elif level == "genotype":
            self.plot_genotype_summary(eframe, canvas)
        elif level == "celltype":
            self.plot_genotype_comparison(eframe, canvas)

    def plot_single_epoch(self, eframe, canvas):
        epoch = eframe.epoch.iloc[0]
        axes = canvas.grid_axis(1, 1)
        plttr = PlotTrace(axes[0], epoch)
        canvas.draw()

        self.currentplots.append(plttr)

    def plot_summary_epochs(self, eframe: pd.DataFrame, canvas: MplCanvas = None):
        """Plot faceted mean trace
        """
        # GROUP EPOCHS UP TO LIGHT AMP AND MEAN
        grps = groupby(eframe, self.labels)
        grps = grps.sort_values(["lightmean"], ascending=True)

        # BUILD GRID
        n = grps.shape[0]
        axes = canvas.grid_axis(n, 1)
        axii = 0

        # PLOT AVERAGE TRACE FOR EACH LIGHT AMP AND MEAN COMBO
        for ii, row in grps.iterrows():
            epochs = row["epoch"]

            plt = PlotTrace(axes[axii], epochs)
            axii += 1

            self.currentplots.extend([plt])

    def plot_summary_cell(self, eframe: pd.DataFrame, canvas: MplCanvas = None):
        ...

    def plot_genotype_summary(self, epochs, canvas):
        ...

    def plot_genotype_comparison(self, epochs: EpochBlock, canvas: MplCanvas = None):
        ...

    @property
    def name(self): return "ChirpAnalysis"

    @property
    def labels(self):
        return ["holdingpotential", "protocolname", "led", "celltype", "genotype", "cellname", "lightmean"]

    @property
    def tracestype(self): return ChirpEpoch

    @property
    def tracetype(self): return ChirpEpochs
