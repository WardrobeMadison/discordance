# %%
from discordance.io.symphonyreader import SymphonyReader
from discordance.io.filemap import FileMap
from discordance.funks.psth import calculate_psth
from discordance.io.discordancereader import DiscordanceReader
from discordance.funks import charting
# %%
path = "tests/data/2020-07-21A.h5"
outpath = "tests/output/2020-07-21A.json"

filemap = FileMap(path, outpath)

# %%
#sr = SymphonyReader(filemap.symphonyfilepath)
#sr.to_json(filemap.discordancefilepath)
# %%
dr = DiscordanceReader(filemap)
df = dr.to_epochs()
df.head()

# %%
for name, frame in df.groupby(["Type","CellName"]):
	print(name)
