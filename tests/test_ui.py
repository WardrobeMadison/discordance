from pathlib import Path
from discordance import viewer, io, epochtypes


def test_window():
	try:
		path = Path(r"tests/output/2020-07-21A.h5")
		dr = io.DiscordanceReader([path])
		epochs = dr.to_epochs()
		traces = epochtypes.Traces(epochs)
		groupbykeys = ["protocolname", "celltype", "cellname", "lightamplitude", "lightmean"]
		viewer.run(traces, groupbykeys=groupbykeys)

	except SystemExit as e:
		...
	finally:
		assert True