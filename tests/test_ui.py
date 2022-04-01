from pathlib import Path
from dissonance import viewer, io, epochtypes 
from dissonance.epochtypes import filter


def test_window():
	try:
		paths = [
			Path(r"tests/output/2021-09-23A.h5"),
			Path(r"tests/output/2021-10-05A.h5"),
			Path(r"tests/output/2021-10-21A.h5"),
			Path(r"tests/output/g2021-07-12A2.h5"),
			Path(r"tests/output/g2021-07-12A2.h5"),
			Path(r"tests/output/g2021-07-12A2.h5"),
		]
		dr = io.DissonanceReader(paths)
		epochs = dr.to_epochs()
		epochs = [x for x in epochs if x.tracetype == "spiketrace"]
		epochs = epochtypes.SpikeEpochs(epochs)

		tree = viewer.analysistrees.LedPulseAnalysis(epochs)

		viewer.run(tree)

	except SystemExit as e:
		...
	finally:
		assert True