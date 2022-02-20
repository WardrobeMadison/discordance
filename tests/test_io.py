from pathlib import Path
from discordance import viewer, io, epochtypes

def test_to_json():
	path = "tests/data/2020-07-21A.h5"
	outpath = "tests/output/2020-07-21A.json"

	filemap = io.FileMap(path, outpath)

	sr = io.SymphonyReader(filemap.symphonyfilepath)
	sr.to_json(filemap.discordancefilepath)

				
def test_to_h5():
	#path = "tests/data/2021-10-21A.h5"
	#outpath = "tests/output/2021-10-21A.h5"
	path = "tests/data/pdr2021-07-12A.h5"
	outpath = "tests/output/pdr2021-07-12A.h5"
	sr = io.SymphonyReader(path)
	sr.to_h5(outpath)

def test_reader():
	path = Path(r"tests/output/2020-07-21A.h5")
	dr = io.DiscordanceReader([path])
	epochs = dr.to_epochs()

	print(epochs)

	assert True