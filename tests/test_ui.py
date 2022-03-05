from pathlib import Path
from dissonance import viewer, io, epochtypes 
from dissonance.epochtypes import filter


def test_window():
	try:
		paths = [
			Path(r"tests/output/pdr2021-07-12A.h5"),
			Path(r"tests/output/2021-10-05A.h5")
		]
		dr = io.DissonanceReader(paths)
		epochs = dr.to_epochs()
		traces = epochtypes.Traces(epochs)

		traces = filter(traces, tracetype="spiketrace")

		tree = viewer.analysistrees.LedPulseAnalysis(traces)

		viewer.run(traces, tree)

	except SystemExit as e:
		...
	finally:
		assert True