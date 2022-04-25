from pathlib import Path
from dissonance import viewer, io, epochtypes 
from dissonance.epochtypes import filter


def test_window():
	try:

		root_dir = Path("/home/joe/Projects/DataStore/MappedData")

		#paths = [file for ii, file in enumerate((root_dir/"DR").glob("*.h5")) if ii <3]
		#paths.extend([file for ii, file in enumerate((root_dir / "WT").glob("*.h5")) if ii < 3])
		paths = [file for ii, file in enumerate((root_dir/"DR").glob("*.h5"))]
		paths.extend([file for ii, file in enumerate((root_dir / "WT").glob("*.h5"))])

		dr = io.DissonanceReader(paths)
		epochs = dr.to_epochs()
		epochs = [x for x in epochs if x.tracetype == "spiketrace"]
		epochs = epochtypes.SpikeEpochs(epochs)

		tree = viewer.analysistrees.LedPulseAnalysis(epochs, "DemoForJenna.txt")

		viewer.run(tree, "DemoForJenna.txt")
	except SystemExit as e:
		...
	finally:
		assert True