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

		#paths = [file for ii, file in enumerate((root_dir/"DR").glob("*.h5"))]
		#paths.extend([file for ii, file in enumerate((root_dir / "WT").glob("*.h5"))])
		paths = [file for ii, file in enumerate((root_dir/"GG2 control").glob("*.h5"))]
		paths.extend([file for ii, file in enumerate((root_dir / "GG2 KO").glob("*.h5"))])

		dr = io.DissonanceReader(paths)
		epochs = dr.to_epochs(tracetype = "spiketrace")
		epochs = epochtypes.SpikeEpochs(epochs)

		tree = viewer.analysistrees.LedSpikeAnalysis(epochs, unchecked)
		
		viewer.run(tree, unchecked, uncheckedpath)
	except SystemExit as e:
		...
	finally:
		assert True