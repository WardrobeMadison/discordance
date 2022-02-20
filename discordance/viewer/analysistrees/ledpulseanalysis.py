from typing import List, Tuple, Union, Dict, Any

import seaborn as sns
import pandas as pd
import numpy as np

from ...trees import Tree, Node
from ...epochtypes import groupby, Traces, ITrace, SpikeTraces
from ..components.chart import MplCanvas

# AMP, MEAN
PCTCNTRST = {
	(-0.001,0.005):-25,
	(-0.003,0.005):-50,
	(-0.005,0.005):-100,
	(0.001,0.005):25,
	(0.003,0.005):50,
	(0.005,0.005):100,
	(0.002,0.007):25,
	(0.004,0.007):50,
	(0.005,0.007):75,
	(0.007,0.007):100,
	(-0.002,0.007):-25,
	(-0.004,0.007):-50,
	(-0.005,0.007):-75,
	(-0.007,0.007):-100,
	(-0.002,0.006):-25,
	(-0.003,0.006):-50,
	(-0.006,0.006):-100,
	(0.002,0.006):25,
	(0.003,0.006):50,
	(0.006,0.006):100,
	(-0.006,0.006):-100,
	(0.002,0.005):50,
	(0.004,0.005):75,
	(-0.004,0.005):-75,
	(0.005,0.006):75,
	(-0.005,0.006):-75,
	(0.005,0):0,
	(0.006,0):0}
# LED, AMP
RSTRMAP = {
	("Green",0.007): 5,
	("Green",0.014): 10,
	("Green",0.0121): 10,
	("Green",0.006): 5,
	("Green",0.003): 0.025,
	("Green",0.006): 0.05,
	("Green",0.012): 0.1,
	("Green",0.024): 0.2,
	("Green",0.048): 0.4,
	("Green",0.096): 0.8,
	("Green",0.192): 1.6,
	("Green",0.384): 3.2,
	("Green",0.015): 0.1,
	("Green",0.03): 0.2,
	("Green",0.06): 0.4,
	("Green",0.12): 0.8,
	("Green",0.24): 1.6,
	("Green",0.48): 3.2,
	("Green",0.004): 0.025,
	("Green",0.008): 0.05,
	("Green",0.016): 0.1,
	("Green",0.032): 0.2,
	("Green",0.064): 0.4,
	("Green",0.128): 0.8,
	("Green",0.256): 1.6,
	("Green",0.512): 3.2,
	("Green",0.007): 0.05,
	("Green",0.014): 0.1,
	("Green",0.028): 0.2,
	("Green",0.056): 0.4,
	("Green",0.112): 0.8,
	("Green",0.224): 1.6,
	("Green",0.448): 3.2,
	("Green",0.896): 6.4,
	("Green",0.768): 6.4,
	("Green",0.0074): 0.05,
	("Green",0.0148): 0.1,
	("Green",0.006): 5,
	("Green",0.007): 5,
	("Green",0.012): 10,
	("Green",0.013): 10,
	("Green",0.014): 10,
	("Green",0.0121): 10}

class LedPulseAnalysis(Tree):
	name = "AnalysisTest"
	labels = ("protocolname", "celltype", "genotype", "cellname", "lightamplitude", "lightmean") 
	
	def __init__(self, epochs: Traces, unchecked:set=None):
		# GROUP EPOCHS INTO FLAT LIST
		self.create_groups(epochs)

		# CREATE TREE STRUCTURE
		super().__init__(self.name, self.labels, self.keys)

		# ADD EPOCHS TO LEAVES OF TREE
		self.add_epoch_leaves()
		
		# CREATE DATAFRAME
		self.create_frame(unchecked)

	def create_groups(self, epochs):
		self.keys, self.groupedvals = list(zip(*list(groupby(epochs, self.labels))))

	def add_epoch_leaves(self):
		# ADD EPOCHS AS LEAVES TO TREE
		for leaf, group in zip(self.leaves, self.groupedvals):
			for epoch in group:
				leaf.add(Node("startdate", epoch.startdate))

	def create_frame(self, unchecked):
		# SET WHICH EPOCHS ARE INCLUDED IN OPERATIONS
		self.unchecked = set() if unchecked is None else unchecked

		# FLAG INCLUDED AND EXCLUDED EPOCHS
		data =[]
		for key, group in zip(self.keys, self.groupedvals):
			for epoch in group:
				if epoch.startdate in self.unchecked:
					data.append([*key, epoch.startdate, False, epoch])
				else: 
					data.append([*key, epoch.startdate, True, epoch])

		# CREATE DATAFRAME FOR INCES LOOKUP OF EPOCHS BY PARAMETERS	FOR FASTER QUERIES
		self.frame = (
			pd.DataFrame(columns=[*self.labels, "startdate", "include", "epoch"], data=data)
			.set_index(keys=[*self.labels, "startdate"])
			.sort_index())

	def update(self, node, paramname:str, value: Any):
		epochs = self.query(node, includeflag=None)
		keys = node.path

		# UPDATE EACH EPOCH
		for epoch in epochs:
			epoch.update(keys, paramname, value)

		# REMAKE THE WHOLE CLASS. 
		epochs = self.frame.epoch.to_list()
		self.__init__(epochs, self.unchecked)


	def query(self, node: Node, includeflag=True) -> Union[Traces, ITrace]:
		"""Relate nodes from tree to underlying dataframe. Only passes inclued nodes

		Args:
			node (Node): Node's path used for lookup

		Returns:
			Union[Traces, ITrace]: Traces or individual Trace for leaf node
		"""
		if node.isleaf:
			return self.frame.query(f"startdate == '{node.uid}'").epoch.iloc[0]
		else:
			path = node.path # dictionary of all values
			#condition = " and ".join([f"{key}=='{val}'" for key,val in path.items()])
			#df.loc[(slice(None), 5, slice(None))]
			condition = []
			for key in self.labels:
				temp = path.get(key)
				if temp is None:
					temp = slice(None)
				condition.append(temp)
				
			dff = self.frame.loc[tuple(condition), :]
			if includeflag is None:
				vals = dff.loc[:, "epoch"].to_list()
			else:
				vals = dff.loc[dff.include == includeflag, "epoch"].to_list()
			return SpikeTraces(self.labels, vals)

	def plot(self, node: Node, canvas: MplCanvas=None):
		"""Logic for selecting analysis from scope of a node
		"""
		scope = list(node.path.keys())
		# TODO split for LedPulse v. Led Pulse Analysis
		# TODO UV LED split special analysis
		if node.isleaf:
			epoch = self.query(node)
			self.plot_spike_trace(epoch, canvas)
		elif (
				scope[1:] == ["protocolname", "celltype", "genotype", "cellname", "lightamplitude", "lightmean"]
				or
		 		scope[1:] == ["protocolname", "celltype", "genotype", "cellname", "lightamplitude"]
				or 
		 		scope[1:] == ["protocolname", "celltype", "genotype", "cellname"]
				or
		 		scope[1:] == ["protocolname", "celltype", "genotype"]):
			epochs = self.query(node)
			self.grid_plot(epochs, canvas)
		elif (
		 		scope[1:] == ["protocolname", "celltype"]):
			epochs = self.query(node)
			self.cell_comparison(epochs, canvas)

	def cell_comparison(self, epochs, canvas):
		# TODO average psth by cell
		# TODO Bar graph ttp and amp

		# IF LEDPULSEFAMILY SOMETHING ...
		...

	def grid_plot(self, epochs: SpikeTraces, canvas: MplCanvas=None):
		"""Plot faceted mean psth
		"""
		# TODO fix scope of group by. Need to determine which ones to plot separately
		grps = list(groupby(epochs, self.labels))
		n,m = len(grps), 2
		axes = canvas.grid_axis(n,m)
		
		axii = 0
		for (name, traces) in grps:
			psth = traces.psth
			self.plot_psth(psth, axes[axii]); axii += 1
			self.plot_raster(traces, axes[axii]); axii += 1

		canvas.draw()

	def plot_spike_trace(self, epoch: SpikeTraces, canvas: MplCanvas=None):
		"""Plot trace with spikes and psth

		Args:
			epoch ([type]): [description]
			canvas (MplCanvas, optional): [description]. Defaults to None.
		"""
		axes = canvas.grid_axis(2,1)

		self.plot_trace(epoch, axes[0])
		self.plot_psth(epoch.psth, axes[1])
		canvas.draw()

	def plot_trace(self, epoch:SpikeTraces, ax):
		"""Plot traces

		Args:
			epoch (SpikeTraces): Epochs to trace
			ax ([type]): Matlab figure axis
		"""
		ax.plot(epoch.values)
		ax.grid(True)

		if (
			epoch.type == "spiketrace"
			and epoch.spikes.sp is not None):
				y = epoch.values[epoch.spikes.sp]
				ax.scatter(epoch.spikes.sp, y, marker="x", c="#FFA500")

		#ax.title =  epoch.startdate
		ax.title.set_text(epoch.startdate)
		ax.set_ylabel("pA")
		ax.set_xlabel("10e-4 seconds")

	def plot_psth(self, psth: np.array, ax):
		"""Psth plot

		Args:
			psth (np.array): psth values from traces
			ax ([type]): [description]
		"""
		ax.clear()
		ax.grid(True)

		ttp = (np.argmax(psth) + 1) / (10000 / 100)
		x = (np.arange(len(psth)) + 1) / (10000/ 100)

		ax.axvline(ttp, linestyle='--', color='k', alpha=0.4)
		ax.plot(x, psth)

		ax.title.set_text("PSTH")	
		ax.set_ylabel("Hz / s")
		ax.set_xlabel("10ms bins")

	def plot_raster(self, epochs, ax):

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
