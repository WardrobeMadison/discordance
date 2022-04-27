from pathlib import Path
import pandas as pd
from dissonance import viewer, io, epochtypes 
from dissonance.epochtypes import filter
from time import time


def test_window():
	try:
		root_dir = Path("/home/joe/Projects/DataStore/MappedData")
		uncheckedpath = Path("DemoForJenna.txt")
		unchecked = io.read_unchecked_file(uncheckedpath)

		#folders = ["DR", "WT"]
		folders = ["GG2 control", "GG2 KO"]
		paths = []
		for fldr in folders:
			paths.extend(
				list((root_dir/fldr).glob("*.h5"))
			)

		dr = io.DissonanceReader(paths)
		epochs = dr.to_epochs(tracetype = "spiketrace")
		epochs = epochtypes.SpikeEpochs(epochs)

		tree = viewer.analysistrees.LedSpikeAnalysis(epochs, unchecked)
		
		viewer.run(tree, unchecked, uncheckedpath)
	except SystemExit as e:
		...
	finally:
		assert True