import sys
sys.path.append("..")
from pathlib import Path
from dissonance import analysis, io, epochtypes
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("tests/presentation.mplstyle")

MAPPED_DIR = Path(r"/Users/jnagy2/Projects/Dissonance/Data/MappedData")
FOLDERS = ["GG2 KO", "GG2 control"]
UNCHECKEDPATH = Path("JennaBegins.txt")
UNCHECKED = set(pd.read_csv(UNCHECKEDPATH, parse_dates=["startdate"]).iloc[:, 0].values)

def get_params(paramnames, protocolnames, tracetype=None):
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
        params = dr.to_params(paramnames, filters={
                                "tracetype": tracetype})
    else:
        params = dr.to_params(paramnames)

    params = params.loc[params.protocolname.isin(protocolnames)]
    epochio = io.EpochIO(params, paths, unchecked=UNCHECKED)

    return epochio

def test_crf():
    # GET DATA
    paramnames = ["led", "holdingpotential", "protocolname", "celltype",
                    "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
    tracetype = "wholetrace"

    protocolnames = ["LedPulseFamily", "LedPulse"]

    epochio = get_params(paramnames, protocolnames, tracetype)
    wa = analysis.LedWholeAnalysis()

    # QUERY NODE
    params = dict(
        Name="LedWholeanalysis",
        protocolname="LedPulse",
        led="UV LED",
        celltype="RGC\ON-alpha",)
    eframe = epochio.query(filters = [params])
    eframe = eframe.loc[eframe.lightmean == 5000]

    # PLOT
    fig, ax = plt.subplots()

    df = epochtypes.groupby(eframe, ["holdingpotential", "protocolname", "led", "celltype", "genotype", "cellname", "lightmean", "lightamplitude"])
    plot = analysis.charting.PlotWholeCRF(ax, metric = "peakamplitude", igor=True)
    for geno, frame in df.groupby("genotype"):
        plot.append_trace(frame)

    plot.ax.get_legend().remove()


    plot.ax.set_yticks([500, 0, -500, -1000, -1500])
    plot.ax.set_yticklabels([500, 0, -500, -1000, -1500])

    fig.savefig("ContrastReponseCurve.png")
    plt.show()


def test_weber():
    # READ H5 FILES
    paramnames = ["led", "holdingpotential", "protocolname", "celltype",
                    "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
    tracetype =  "wholetrace"
    protocolnames = ["LedPulseFamily"]

    epochio = get_params(paramnames, protocolnames, tracetype)

    # QUERY NODE
    params = dict(
        Name="LedWholeanalysis",
        holdingpotential="excitation",
        protocolname="LedPulseFamily",
        led="UV LED",
        celltype="RGC\ON-alpha",)
    eframe = epochio.query(filters = [params])
    df = epochtypes.groupby(eframe, ["holdingpotential", "protocolname", "led", "celltype", "genotype", "cellname", "lightmean", "lightamplitude"])

    # PLOT FIGURE
    fig, ax = plt.subplots()

    plot = analysis.charting.PlotWeber(ax,  igor=True)
    for geno, frame in df.groupby("genotype"):
        plot.append_trace(frame)

    fig.savefig("Weber.png")
    plt.show()


def test_saccade():
    paramnames = ["holdingpotential", "led", "protocolname", "celltype", "genotype",
                    "cellname", "lightamplitude", "lightmean", "startdate"]
    epochio = get_params(paramnames, ["SaccadeTrajectory2"])

    params = dict(
        Name="SaccadeAnalysis",
        protocolname="SaccadeTrajectory2",
        led="UV LED",
        celltype="RGC\ON-alpha",)

    eframe = epochio.query(filters = [params])
    df = epochtypes.groupby(eframe, ["holdingpotential", "protocolname", "led", "celltype", "genotype", "cellname", "lightmean", "lightamplitude"])

    fig , ax = plt.subplots(constrained_layout=True)
    fig.patch.set_facecolor('xkcd:white')
    black = "#000000"
    red = "#CC0000"
    colors = {
        "GG2 control": black,
        "GG2 KO": red
    }
    for key, frame in df.groupby("genotype"):
        Y = np.mean(
            [
                epoch.trace
                for epoch in frame.epoch
            ], axis=0
        )
        X = np.arange(Y.shape[0]) / 10000
        ax.plot(X, Y, label = key, color = colors[key])

    ax.set_title("Response to Saccade Stimulus")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Response (pA)")
    ax.set_yticks([0, -500, -1000, -1500, -2000])
    ax.set_xticks([0, 5, 10])

    #ax.spines['left'].set_bounds(0, 80)
    #ax.spines['bottom'].set_bounds(0, max(X))
    #ax.spines["left"].set_bounds(*ax.get_ylim())

    fig.savefig("saccade.png")
    plt.show()
