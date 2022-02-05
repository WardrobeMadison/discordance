# %%
from discordance.io.symphonyreader import SymphonyReader
from discordance.io.filemap import FileMap
from discordance.funks.psth import calculate_psth
from discordance.funks.spike_detection import detect_spikes
from discordance.io.discordancereader import DiscordanceReader
from discordance.funks import charting
# %%
path = "tests/data/2020-07-21A.h5"
outpath = "tests/output/2020-07-21A.json"

filemap = FileMap(path, outpath)

# %%
sr = SymphonyReader(filemap.symphonyfilepath)
sr.to_json(filemap.discordancefilepath)
# %%
dr = DiscordanceReader(filemap)
df = dr.to_epochs()

# %%
epoch = df.Epoch.iloc[55]
# %%
charting.plt_trace(epoch)
charting.plt_spikes(epoch)
# %%
psth = calculate_psth(epoch, plot=True)
# %%

# %%
