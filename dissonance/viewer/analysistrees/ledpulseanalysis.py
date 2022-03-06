from typing import List, Tuple, Union, Dict, Any

import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from scipy.stats import ttest_ind

from dissonance.epochtypes.spiketrace import SpikeTrace

from .baseanalysis import BaseAnalysis
from ...trees import Node
from ...epochtypes import groupby, Traces, ITrace, SpikeTraces, filter
from ..components.chart import MplCanvas

def p_to_star(p):
	if p < 0.001:
		return "***"
	elif p <0.01:
		return "**"
	elif p < 0.05:
		return "*"
	else:
		return "ns"

class LedPulseAnalysis(BaseAnalysis):

	def __init__(self, epochs: Traces, unchecked:set=None):
		# CONSTRUCT BASE, FILTER ON TRACE TYPE, LED AND PROTOCOL NAME
		epochs_ = filter(epochs, led=self.led, protocolname = self.protocolname, tracetype="spiketrace"),
		super().__init__(
			epochs_,
			unchecked)

	@property
	def name(self): return "AnalysisTest"

	@property
	def protocolname(self): return "LedPulse"

	@property
	def led(self): return "Green"

	@property
	def labels(self): return ("celltype", "genotype", "cellname", "lightamplitude", "lightmean") 

	@property
	def tracestype(self): return SpikeTraces

	@property
	def tracetype(self): return SpikeTrace
	
	def plot(self, node: Node, canvas: MplCanvas=None):
		"""Map node level to analysis run & plots created.
		"""
		scope = list(node.path.keys())
		# INDIVIUDAL TRACE
		if node.isleaf:
			epoch = self.query(node)
			self.plot_spike_trace(epoch, canvas)
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
			# Check if UVLED
			# CRF plots (pct contrast x avg peak amplitude)
			# CRF plots (pct contrast x time to peak)
			...

			# GET ALL CHILD EPOCHS FROM SELECTION
			epochs = self.query(node)

			# SEPARATE EPOCHS
			df = groupby(epochs, self.labels)

			# ANALYSIS IS AT AVERAGE OF CELLS
			idx = ["celltype", "genotype", "lightamplitude", "lightmean"]
			n,m  = df.shape[0], 2
			axes = canvas.grid_axis(n,m)
			for name, frame in df.groupby(idx):
				self.plot_swarm("peakamplitude", frame)

		# COMPARE GENOTYPES
		elif (scope[1:] == ["led", "celltype"]):
			epochs = self.query(node)
			self.genotype_comparison(epochs, canvas)

	def genotype_comparison(self, epochs: Traces, canvas: MplCanvas = None):
		"""Compare epochs by genotype

		Args:
			epochs (Traces): Epochs to compare.
			canvas (MplCanvas, optional): Parent MPL canvas, figure created if not provided. Defaults to None.
		"""
		# TODO Bar graph ttp and amp

		# GROUP EPOCHS SELECTED BY LABELS
		df = groupby(epochs, self.labels)
		n,m  = df.shape[0], 2
		axes = canvas.grid_axis(n,m)

		# GROUP INTO GENOTYPES

		genos = df.genotype.unique()

		for name, frame in df.groupby(["lightmean", "lightamplitude"]):
			epochs = dict(zip(genos, frame.trace.values))
			self.plot_swarm(epochs, axes)

	def grid_plot(self, epochs: SpikeTraces, canvas: MplCanvas=None):
		"""Plot faceted mean psth
		"""
		# TODO fix scope of group by. Need to determine which ones to plot separately
		grps = groupby(epochs, self.labels)
		n,m  = grps.shape[0], 2
		axes = canvas.grid_axis(n,m)
		
		axii = 0
		for row in grps.values:
			traces = row[-1]
			psth = traces.psth
			self.plot_psth(psth, n=len(traces.traces), ax=axes[axii]); axii += 1
			self.plot_raster(traces, ax=axes[axii]); axii += 1

		canvas.draw()

	def plot_spike_trace(self, epoch: SpikeTraces, canvas: MplCanvas=None):
		"""Plot trace with spikes and psth

		Args:
			epoch ([type]): [description]
			canvas (MplCanvas, optional): [description]. Defaults to None.
		"""
		axes = canvas.grid_axis(2,1)

		self.plot_trace(epoch, axes[0])
		self.plot_psth(epoch.psth, ax=axes[1])
		canvas.draw()

	def plot_trace(self, epoch:SpikeTraces, ax):
		"""Plot traces

		Args:
			epoch (SpikeTraces): Epochs to trace
			ax ([type]): Matlab figure axis
		"""
		ax.plot(epoch.values)

		if (
			epoch.type == "spiketrace"
			and epoch.spikes.sp is not None):
				y = epoch.values[epoch.spikes.sp]
				ax.scatter(epoch.spikes.sp, y, marker="x", c="#FFA500")

		#ax.title =  epoch.startdate
		ax.title.set_text(epoch.startdate)
		ax.set_ylabel("pA")
		ax.set_xlabel("10e-4 seconds")

	def plot_psth(self, psth: np.array, ax: Axes=None, n:int=None, ):
		"""Psth plot

		Args:
			psth (np.array): psth values from traces
			ax ([type]): [description]
		"""
		ax.clear()

		# PLOT VEERTICAL LINE FOR PEAK TIME	
		seconds_conversion = 10000 / 100
		ttp = (np.argmax(psth) + 1) / (seconds_conversion) # IN SECONDSk
		x = (np.arange(len(psth)) + 1) / (seconds_conversion) # IN SECONDS
		ax.axvline(ttp, linestyle='--', color='k', alpha=0.4)

		# PLOT PSTH
		ax.plot(x, psth)

		# LEGEND FOR TTP
		custom_lines = [Line2D([0], [0], color='k', alpha = 0.4, linestyle="--")]
		ax.legend(custom_lines, [f"Time = {ttp:0.2f}, Amp= {np.max(psth):.02f}"])

		# SET AXIS LABELS
		title = "PSTH"
		if n:
			title = f"{title} (n = {n})"

		ax.set_title(title)	
		ax.set_ylabel("Hz / s")
		ax.set_xlabel("10ms bins")

	def plot_raster(self, epochs: Traces, ax: Axes=None):
		"""Raster plots

		Args:
			epochs (Traces): Epoch traces to plot.
			ax (Axes, optional): Axis obj from parent figure, creates figure if not provided. Defaults to None.
		"""
		if ax is None: fig, ax, = plt.subplots()

		toplt = []
		for ii, epoch in enumerate(epochs):
			spikes = epoch.spikes.sp / 10000
			y = [ii+1] * len(spikes)
			toplt.append((spikes, y))

		ax.clear()
		ax.grid(False)

		for x,y in toplt:
			ax.scatter(x,y, marker="|", c="k")

		title = f"cellname={epochs.cellnames[0]}, lightamp={epochs.lightamplitudes[0]}, lightmean={epochs.lightmeans[0]}"
		
		ax.title.set_text(title)	
		ax.axes.get_yaxis().set_visible(False)
		ax.axis("off")

	def plot_swarm(self, epochs: pd.DataFrame, window: Tuple[int, int] = None, ax: Axes = None) -> None:
		"""Swarm plot :: bar graph of means with SEM and scatter. Show signficance

		Args:
			epochs (Dict[str,SpikeTraces]): Maps genos name to traces to plot.
			ax (Axes, optional): Axis obj from parent figure, creates figure if not provided. Defaults to None.
		"""
		if ax is None: fig, ax, = plt.subplots()

		# EPOCHS DF HAS ALL LABELS BUT SINGLE LIGHT MEAN AND LIGHT AMPLITUDE
		# ASSUME TWO GENOTYPES FOR SWARM PLOT
		assert len((epochs.lightmean.str + epochs.lighamplitude.str).unique()) == 1
		assert len(epochs.genotype.unique()) == 2

		# CALCULATE MEAN AND SEM. WANT TO AVERAGE ALL PSTHS BY CELL & REMOTE MEAN AND SEM ON THAT
		labels = []
		values = []
		for name, frame in epochs.groupby("genotype"):
			labels.append(name)
			values_ = []
			# GET PSTH FOR EACH CELL
			celltraces = frame.trace.values
			for traces in celltraces:
				psth = traces.psth

				# CALCULATE PSTH METRIC
				metval = np.max(psth)
				time = np.argmax(psth)

				values_.append(metval)
				#times_.append(time)
			values.append(np.array(values_))


		for ii, (name, value) in zip(labels, values):
			# PLOT BAR with MEAN and SEM
			ax.bar(ii,
				height=np.mean(value),
				yerr=np.std(value) / np.sqrt(len(value)), 
				capsize=12, 	
				tick_label=labels[ii],
				alpha=0.5)

			# PLOT SCATTER
			ax.scatter(
				np.repeat(ii, len(value)), 
				value, 
				alpha = 0.25)
			
			# LABEL NUMBER OF CELLS 
			ax.text(ii, 0, f"n={len(value)}",
				ha='center', va='bottom', color='k')

		# CALCULATE SIGNIFICANCE
		stat, p = ttest_ind(
			values[0][~np.isnan(values[0])], 
			values[1][~np.isnan(values[1])])

		print(p)
		stars = p_to_star(p)
		stars = f"p={p:0.03f}" if stars == "ns" and p < 0.06 else stars
		x1, x2 = 0, 1 # ASSUME ONLY 2

		#COMBINE FOR MAXIMUM CALCULATION FOR PLACEMENT OF HORIZONTAL SIG BAR
		Ys = []
		for y in values:
			Ys.extend(y[~np.isnan(y)])
		ymax = np.max(Ys)

		# PLOT SIGNFICANCE LABEL
		# HACK PERCENT TO PUT ABOVE MAX POINT. DOESN'T WORK WELL FOR SMALL VALUES
		pct = 0.05 
		ay, h, col = ymax + ymax * pct, ymax * pct, 'k'

		ax.plot(
			[x1, x1, x2, x2], 
			[ay, ay+h, ay+h, ay], 
			lw=1.5, c=col)

		ax.text(
			(x1+x2)*.5, 
			ay+h, 
			stars, 
			ha='center', va='bottom', 
			color=col)

		# FIG SETTINGS
		ax.grid(False)
		ax.set_title("Background")

		# X AXIS FORMAT
		ax.xaxis.set_ticks_position('none') 
		ax.set_xticks(np.array([1,2], dtype=float))
		ax.set_xticklabels(labels)
		ax.set_xlabel("Background (R*/S-Cone/sec)")

		# Y AXIS FORMAT
		ax.set_ylabel("pA")
		ax.set_ylim((0.0, ymax * 1.20))

