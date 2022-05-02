from pathlib import Path
import pandas as pd
from dissonance import viewer, io, epochtypes, analysis
from dissonance.epochtypes import filter
from time import time
import pytest


class TestGui():

	def test_window_wholecell(self):
		try:
			root_dir = Path("/home/joe/Projects/DataStore/MappedData")
			#uncheckedpath = Path("DemoForJenna.txt")
			#unchecked = io.read_unchecked_file(uncheckedpath)
			unchecked = None
			uncheckedpath = None

			folders = ["DR", "WT"]
			#folders = ["GG2 control", "GG2 KO"]
			paths = []
			for fldr in folders:
				paths.extend(
					[	file
						for ii, file in enumerate((root_dir/fldr).glob("*.h5"))
					]
				)

			dr = io.DissonanceReader(paths)
			paramnames = ["led", "holdingpotential", "protocolname", "celltype", "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
			params = dr.to_params(paramnames, filters={"tracetype" : "wholetrace"})
			params = params.loc[params.protocolname.isin(["LedPulseFamily", "LedPulse"])]

			epochio = analysis.EpochIO(params, paths)
			wa = analysis.LedWholeAnalysis()
			
			viewer.run(epochio, wa, unchecked, uncheckedpath)
		except SystemExit as e:
			...
		finally:
			assert True

	def test_window_spikecell(self):
		try:
			root_dir = Path("/home/joe/Projects/DataStore/MappedData")
			#uncheckedpath = Path("DemoForJenna.txt")
			#unchecked = io.read_unchecked_file(uncheckedpath)
			unchecked = None
			uncheckedpath = None

			folders = ["DR", "WT"]
			#folders = ["GG2 control", "GG2 KO"]
			paths = []
			for fldr in folders:
				paths.extend(
					[	file
						for ii, file in enumerate((root_dir/fldr).glob("*.h5"))
						if ii < 5
					]
				)

			dr = io.DissonanceReader(paths)
			paramnames = ["led", "protocolname", "celltype", "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
			params = dr.to_params(paramnames, filters={"tracetype" : "spiketrace"})
			params = params.loc[params.protocolname.isin(["LedPulseFamily", "LedPulse"])]

			epochio = analysis.EpochIO(params, paths)
			lsa = analysis.LedSpikeAnalysis()
			
			viewer.run(epochio, lsa, unchecked, uncheckedpath)
		except SystemExit as e:
			...
		finally:
			assert True