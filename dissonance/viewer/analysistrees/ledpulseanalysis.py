from typing import List, Tuple, Union, Dict, Any

import seaborn as sns
from datetime import date
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from scipy.stats import ttest_ind

from dissonance.epochtypes.spikeepoch import SpikeEpoch
from dissonance.viewer.plotting.plot import PlotSwarm

from .baseanalysis import BaseAnalysis
from ...trees import Node
from ...epochtypes import groupby, Epochs, SpikeEpochs, filter
from ..components.chart import MplCanvas
from ..plotting import PlotPsth, PlotRaster, PlotTrace


class LedPulseAnalysis(BaseAnalysis):

	def __init__(self, epochs: Epochs, unchecked:set=None):
		# CONSTRUCT BASE, FILTER ON TRACE TYPE, LED AND PROTOCOL NAME
		epochs_ = filter(epochs, led=self.led, protocolname = self.protocolname, tracetype="spiketrace")
		super().__init__(
			epochs_,
			unchecked)

		# USED IN SAVING PLOTS AND EXPORTING DATA
		self.currentplots = []

	@property
	def name(self): return "AnalysisTest"

	@property
	def protocolname(self): return "LedPulse"

	@property
	def led(self): return "Green LED"

	@property
	def labels(self): return ("celltype", "genotype", "cellname", "lightamplitude", "lightmean") 

	@property
	def tracestype(self): return SpikeEpochs

	@property
	def tracetype(self): return SpikeEpoch
	
	def plot(self, node: Node, canvas: MplCanvas=None):
		"""Map node level to analysis run & plots created.
		"""
		self.currentplots = []
		scope = list(node.path.keys())
		# INDIVIUDAL TRACE
		if node.isleaf:
			epoch = self.query(node)

			axes = canvas.grid_axis(1,2)
			plttr, = PlotTrace(axes[0], epoch)
			pltpsth = PlotPsth(axes[1], epoch, label=epoch.startdate)
			canvas.draw()

			self.currentplots.append(plttr)
			self.currentplots.append(pltpsth)

		# GROUPED PLOTS
		elif (
				scope[1:] == ["celltype", "genotype", "cellname", "lightamplitude", "lightmean"]
				or
		 		scope[1:] == ["celltype", "genotype", "cellname", "lightamplitude"]
				or 
		 		scope[1:] == ["celltype", "genotype", "cellname"]):
			epochs = self.query(node)
			self.grid_plot(epochs, canvas)

		# ACROSS CELL ANALYSIS
		elif (scope[1:] == ["celltype", "genotype"]):

			# GET ALL CHILD EPOCHS FROM SELECTION
			epochs = self.query(node)
			grps = groupby(epochs, ["lightamplitude", "lightmean"])
			n,m  = grps.shape[0], 1
			axes = canvas.grid_axis(n,m)
			
			for ii, row in grps.iterrows():
				epochs = row["trace"]

				plt = PlotPsth(axes[ii], epochs, label=node.path["genotype"])
				title = f'{row["lightamplitude"]}, {row["lightmean"]}'
				plt.ax.set_title(title)

				self.currentplots.append(plt)

			canvas.draw()

		# COMPARE GENOTYPES
		elif (scope[1:] == ["celltype"]):
			epochs = self.query(node)
			self.genotype_comparison(epochs, canvas)

	def genotype_comparison(self, epochs: Epochs, canvas: MplCanvas = None):
		"""Compare epochs by genotype

		Args:
			epochs (Traces): Epochs to compare.
			canvas (MplCanvas, optional): Parent MPL canvas, figure created if not provided. Defaults to None.
		"""
		df = groupby(epochs, self.labels)
		n = len((df.lightmean.astype(str) + df.lightamplitude.astype(str)).unique())
		n,m  = n, 3
		axes = canvas.grid_axis(n,m)

		# PEAK AMPLITUDE SWARM PLOTS IN FIRST COLUMN
		ii = 0
		for name, frame in df.groupby(["lightmean", "lightamplitude"]):
			plt = PlotSwarm(axes[ii], metric="peakamplitude", epochs=frame)
			ii += 3
			self.currentplots.append(plt)

		# TTP SWARM PLOTS IN FIRST COLUMN 
		ii = 1
		for name, frame in df.groupby(["lightmean", "lightamplitude"]):
			plt = PlotSwarm(axes[ii], metric="timetopeak", epochs=frame)
			ii += 3
			self.currentplots.append(plt)

		# OVERLAPPING PSTHS IN THIRD COLUMN
		ii = 2
		for name, frame in df.groupby(["lightmean", "lightamplitude"]):
			axes[ii].set_title(name)
			for geno, fframe in frame.groupby("genotype"):
				# SHOULD ONLY BE ONE GENOTYPE HERE
				epoch = fframe.iloc[0, -1]
				
				plt = PlotPsth(axes[ii], epoch, label=geno)
				self.currentplots.append(plt)
			ii += 3

		canvas.draw()

	def grid_plot(self, epochs: SpikeEpochs, canvas: MplCanvas=None):
		"""Plot faceted mean psth
		"""
		# TODO fix scope of group by. Need to determine which ones to plot separately
		grps = groupby(epochs, self.labels)
		n,m  = grps.shape[0], 2
		axes = canvas.grid_axis(n,m)
		
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

		canvas.draw()
