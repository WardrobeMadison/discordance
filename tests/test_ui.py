from pathlib import Path
import pandas as pd
from dissonance import viewer, io, epochtypes 
from dissonance.epochtypes import filter
from time import time
import unittest


class GuiTestCases(unittest.TestCase):

	def test_window(self):
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
			epochs = dr.to_epochs(tracetype = "wholetrace")
			epochs = epochtypes.SpikeEpochs(epochs)

			tree = viewer.analysistrees.LedWholeAnalysis(epochs, unchecked)
			
			viewer.run(tree, unchecked, uncheckedpath)
		except SystemExit as e:
			...
		finally:
			assert True