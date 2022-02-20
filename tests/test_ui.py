from pathlib import Path
from discordance import viewer, io, epochtypes 
from discordance .epochtypes import filter


def test_window():
	try:
		paths = [
			Path(r"tests/output/pdr2021-07-12A.h5"),
			Path(r"tests/output/2021-10-05A.h5")
		]
		dr = io.DiscordanceReader(paths)
		epochs = dr.to_epochs()
		traces = epochtypes.Traces(epochs)

		traces = filter(traces, tracetype="spiketrace")

		tree = viewer.analysistrees.LedPulseAnalysis(traces)

		viewer.run(traces, tree)

	except SystemExit as e:
		...
	finally:
		assert True