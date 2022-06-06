# %%
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append("..")
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import sem
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from dissonance import io, analysis, epochtypes

plt.style.use("presentation.mplstyle")

MAPPED_DIR = Path(r"/Users/jnagy2/Projects/Dissonance/Data/MappedData")
FOLDERS = ["GG2 KO", "GG2 control"]
UNCHECKEDPATH = Path("/Users/jnagy2/Projects/discordance/WHOLECELLFILTERS.txt")
UNCHECKED = set(pd.read_csv(UNCHECKEDPATH, parse_dates=[
                "startdate"]).iloc[:, 0].values)


def p_to_star(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "ns"


def get_params(paramnames, protocolnames, nprocesses=5, tracetype=None):
    folders = FOLDERS
    paths = []
    for fldr in folders:
        paths.extend(
            [file
                for ii, file in enumerate((MAPPED_DIR/fldr).glob("*.h5"))
             ]
        )

    dr = io.DissonanceReader(paths)
    if tracetype is not None:
        params = dr.to_params(paramnames, nprocesses=nprocesses, filters={
            "tracetype": tracetype})
    else:
        params = dr.to_params(paramnames, nprocesses=nprocesses)

    params = params.loc[params.protocolname.isin(protocolnames)]
    epochio = io.EpochIO(params, paths, unchecked=UNCHECKED)

    return epochio

# %%
#plt.style.use("tests/presentation.mplstyle")
paramnames = ["led", "holdingpotential", "protocolname", "celltype",
                "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
tracetype = "wholetrace"
protocolnames = ["LedPulseFamily"]


epochio = get_params(paramnames, protocolnames=protocolnames, tracetype=tracetype, nprocesses=1)

# QUERY NODE
params = dict(
    Name="LedWholeanalysis",
    holdingpotential="excitation",
    protocolname="LedPulseFamily",
    led="UV LED",
    celltype=r"RGC\ON-alpha",)
eframe = epochio.query(filters=[params])
df = epochtypes.groupby(eframe, ["holdingpotential", "protocolname", "led",
                        "celltype", "genotype", "cellname", "lightmean", "lightamplitude"])

# %%
# PLOT FIGURE
fig, ax = plt.subplots()

plot = analysis.charting.PlotWeber(ax,  igor=True)
for geno, frame in df.groupby("genotype"):
    plot.append_trace(frame)


# %%
fig, ax = plt.subplots(figsize=(4,6))


# THIS IS A HACK PLOT
plt_coeff = analysis.charting.PlotWeberCoeff(plot.fits, igor=True)
plt_coeff.plot(ax)
plt_coeff.ax.set_xticklabels(["Control", "KO"])

plt_coeff.ax.set_title("Half Max")
plt_coeff.ax.set_ylabel("Intensity (R*/S-Cone/s)")

fig.patch.set_facecolor('xkcd:white')

fig.savefig("WeberHalfMax.png")
# %%
