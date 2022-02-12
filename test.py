from pathlib import Path
from discordance import viewer, io, epochtypes
from discordance.trees import Tree
from discordance.epochtypes import groupby
from typing import List, Tuple

import seaborn as sns


path = Path(r"tests/output/2020-07-21A.h5")
dr = io.DiscordanceReader([path])

epochs = dr.to_epochs()
traces = epochtypes.Traces(epochs)
traces = filter(traces, celltype="spiketrace")

splitby = ("protocolname", "celltype", "cellname", "lightamplitude", "lightmean")
keys = [x for x, _ in groupby(traces, splitby)]

splitby
keys

# %%
t = Tree("Test", splitby, keys)
t.visual

for leaf in t.leaves: print(leaf.path)


for key in keys: 
	f = dict(zip(splitby, key))
	print(len(filter(traces, **f)))


class AnalysisTest(Tree):
	name = "AnalysisTest"
	labels = ("protocolname", "celltype", "cellname", "lightamplitude", "lightmean") 
	
	def __init__(self, epochs):
		self.groupedvals = groupby(epochs, self.labels)
		super().__init__(self.name, self.labels, self.groupedvals)

		# Specify which node gets what analysis
		# Group epochs at that level by traversing sub trees

	def psth(self, scope, epochs):
		...

test = AnalysisTest(epochs)


t
t[]