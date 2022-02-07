import json
import h5py
import pandas as pd
from typing import List, Union

from .symphonyreader import SymphonyReader
from .. import epochtypes
from . filemap import FileMap

class DiscordanceReader:

	def __init__(self, filemaps: Union[FileMap, List[FileMap]]):
		if not isinstance(filemaps, list):
			filemaps = [filemaps]

		self.experiments = dict()
		for filemap in filemaps:
			experiment = json.load(open(filemap.discordancefilepath))
			self.experiments[filemap.symphonyfilepath] = experiment

	def to_epochs(self):
		data = []
		for symphfilepath, epochs in self.experiments.items():
			h5file = h5py.File(symphfilepath)
			for epoch in epochs:
				if epoch["parameters"]["backgrounds:Amp1:value"] == 0.0:
					trace = epochtypes.SpikeTrace(
						h5file,
						epoch["path"],
						epoch["parameters"], 
						epoch["responses"])
				else:
					trace = epochtypes.WholeTrace(
						h5file,
						epoch["path"],
						epoch["parameters"], 
						epoch["responses"])
	
				data.append([
					trace.epochpath, 
					trace.type,
					trace.cellname,
					trace.lightamplitude,
					trace.lightmean,
					trace
				])	

		# What should this be?
		columns = "EpochPath Type CellName LightAmplitude LightMean Epoch".split()
		df = pd.DataFrame(columns=columns, data=data)
		return df