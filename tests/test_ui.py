from discordance import viewer, io


def test_window():
	try:
		path = "tests/data/2020-07-21A.h5"
		outpath = "tests/output/2020-07-21A.json"

		filemap = io.FileMap(path, outpath)

		dr = io.DiscordanceReader(filemap)
		epochs = dr.to_epochs()
		viewer.run(epochs)

	except SystemExit as e:
		...
	finally:
		assert True