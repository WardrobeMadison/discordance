from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from scipy.stats import sem
import pandas as pd
import numpy as np
from dissonance import analysis, io, epochtypes
from pathlib import Path
import sys
sys.path.append("..")

plt.style.use("tests/presentation.mplstyle")

MAPPED_DIR = Path(r"/Users/jnagy2/Projects/Dissonance/Data/MappedData")
FOLDERS = ["GG2 KO", "GG2 control"]
UNCHECKEDPATH = Path("/Users/jnagy2/Projects/discordance/WHOLECELLFILTERS.txt")
UNCHECKED = set(pd.read_csv(UNCHECKEDPATH, parse_dates=[
                "startdate"]).iloc[:, 0].values)

colors = {
    "GG2 control":  "#6a9a23",
    "GG2 KO": "#441488"}


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


def test_crf():
    # GET DATA
    paramnames = ["led", "holdingpotential", "protocolname", "celltype",
                  "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
    tracetype = "wholetrace"

    protocolnames = ["LedPulseFamily", "LedPulse"]

    epochio = get_params(paramnames, protocolnames=protocolnames, tracetype=tracetype)
    wa = analysis.LedWholeAnalysis()

    # QUERY NODE
    params = dict(
        Name="LedWholeanalysis",
        protocolname="LedPulse",
        led="UV LED",
        celltype=r"RGC\ON-alpha",)
    eframe = epochio.query(filters=[params])
    eframe = eframe.loc[eframe.lightmean == 5000]

    # PLOT
    fig, ax = plt.subplots()

    df = epochtypes.groupby(eframe, ["holdingpotential", "protocolname", "led",
                            "celltype", "genotype", "cellname", "lightmean", "lightamplitude"])
    plot = analysis.charting.PlotWholeCRF(
        ax, metric="peakamplitude", igor=True)
    for geno, frame in df.groupby("genotype"):
        plot.append_trace(frame)

    plot.ax.set_yticks([500, 0, -500, -1000, -1500])
    plot.ax.set_yticklabels([500, 0, -500, -1000, -1500])

    samples = df.groupby("genotype lightmean lightamplitude".split()).cellname.count().reset_index()
    samples = samples.groupby("genotype").cellname.max().reset_index()

    ncontrol = samples.loc[samples.genotype == 'GG2 control', "cellname"].iloc[0]
    nko = samples.loc[samples.genotype == 'GG2 KO', "cellname"].iloc[0]

    custom_lines = [
                    Line2D([0], [0], color=colors["GG2 control"], lw=4),
                    Line2D([0], [0], color=colors["GG2 KO"], lw=4)]
    labels = [f"Control (n={ncontrol})", f"KO (n={nko})"]
    ax.legend(custom_lines, labels, frameon=False,
        bbox_to_anchor=(1.04,0), loc="lower left")

    fig.savefig("ContrastReponseCurve.png")
    plt.show()


def test_weber():
    # READ H5 FILES
    paramnames = ["led", "holdingpotential", "protocolname", "celltype",
                  "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
    tracetype = "wholetrace"
    protocolnames = ["LedPulseFamily"]

    epochio = get_params(paramnames, protocolnames=protocolnames, tracetype=tracetype)

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

    # PLOT FIGURE
    fig, ax = plt.subplots()

    plot = analysis.charting.PlotWeber(ax,  igor=True)
    for geno, frame in df.groupby("genotype"):
        plot.append_trace(frame)

    fig.savefig("Weber.png")
    plt.show()
    fig, ax = plt.subplots()

    # THIS IS A HACK PLOT
    plt_coeff = analysis.charting.PlotWeberCoeff(plot.fits)
    plt_coeff.plot(ax)
    fig.savefig("WeberHalfMax.png")


def test_saccade():
    paramnames = ["holdingpotential", "led", "protocolname", "celltype", "genotype",
                  "cellname", "lightamplitude", "lightmean", "startdate"]
    epochio = get_params(paramnames, ["SaccadeTrajectory2"])

    params = dict(
        Name="SaccadeAnalysis",
        protocolname="SaccadeTrajectory2",
        led="UV LED",
        celltype=r"RGC\ON-alpha",)

    eframe = epochio.query(filters=[params])
    df = epochtypes.groupby(eframe, ["holdingpotential", "protocolname", "led",
                            "celltype", "genotype", "cellname", "lightmean", "lightamplitude"])

    fig, ax = plt.subplots(constrained_layout=True)
    fig.patch.set_facecolor('xkcd:white')
    colors = {
        "GG2 control":  "#6a9a23",
        "GG2 KO": "#441488"}
    for key, frame in df.groupby("genotype"):
        Y = np.mean(
            [
                epoch.trace
                for epoch in frame.epoch
            ], axis=0
        )
        X = np.arange(Y.shape[0]) / 10000
        ax.plot(X, Y, label=key, color=colors[key])

    samples = df.groupby("genotype").cellname.count().reset_index()
    ncontrol = samples.loc[samples.genotype == "GG2 control", "cellname"].iloc[0]
    nko = samples.loc[samples.genotype == "GG2 KO", "cellname"].iloc[0]
    # LEGEND
    ax.set_title("Response to Saccade Stimulus")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Response (pA)")
    ax.set_yticks([0, -500, -1000, -1500, -2000])
    ax.set_xticks([0, 5, 10])

    custom_lines = [
                    Line2D([0], [0], color=colors["GG2 control"], lw=4),
                    Line2D([0], [0], color=colors["GG2 KO"], lw=4)]
    labels = [f"Control (n={ncontrol})", f"KO (n={nko})"]
    ax.legend(custom_lines, labels, frameon=False,
        bbox_to_anchor=(1.04,0), loc="lower left")

    fig.savefig("saccade.png")
    plt.show()

def test_grouped_swarm():
    grouped_swarm("gain")
    grouped_swarm("timetopeak")

def grouped_swarm(metric):

    paramnames = ["led", "holdingpotential", "protocolname", "celltype",
                  "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
    tracetype = "wholetrace"
    protocolnames = ["LedPulseFamily"]

    epochio = get_params(paramnames, protocolnames=protocolnames,
                         tracetype=tracetype)

    # QUERY NODE
    params = dict(
        Name="LedWholeanalysis",
        holdingpotential="excitation",
        protocolname="LedPulseFamily",
        led="UV LED",
        celltype=r"RGC\ON-alpha")
    eframe = epochio.query(filters=[params])
    df = epochtypes.groupby(eframe, ["holdingpotential", "protocolname", "led",
                            "celltype", "genotype", "cellname", "lightmean", "lightamplitude"])

    df = df.loc[df.lightmean == df.lightamplitude]
    df = df.loc[df.lightmean >= 2500]

    fig, ax = plt.subplots(figsize=(8,6))
    width = 0.35
    ii = 0
    xlabels = []
    colors = {
        "GG2 control":  "#6a9a23",
        "GG2 KO": "#441488"}

    for lightmean, frame in df.groupby("lightmean".split()):
        ii += 1
        xlabels.append(f"{lightmean:0.0f}")
        yvalues = []
        pltY = []
        for kk, (geno, grame) in enumerate(frame.groupby("genotype")):
            if metric == "gain":
                Ys = grame.epoch.apply(lambda x: x.gain).values * -1
            else:
                Ys = grame.epoch.apply(lambda x: x.timetopeaksec).values
            yvalues.append(Ys)
            Y = np.mean(Ys)
            pltY.append(Y)
            semval = sem(Ys)
            x = ii + (-1)**kk * width / 2
            ax.bar(
                x,
                Y,
                yerr=semval,
                width=width - 0.025,
                label=geno,
                linewidth = 2,
                capsize=5,
                edgecolor=colors[geno],
                color='None'
            )
            # PLOT SCATTER
            ax.scatter(
                np.repeat(x, len(Ys)),
                Ys,
                alpha=0.25,
                color=colors[geno])

            ax.text(x, 0, f"n={len(Ys)}", fontdict=dict(size=10), ha='center', va="bottom")

        # TTEST
        stat, p = ttest_ind(
            yvalues[0], yvalues[1])

        stars = p_to_star(p)
        #stars = f"p={p:0.03f}" if stars == "ns" and p < 0.06 else stars
        # PLOT SIGNFICANCE LABEL
        # HACK PERCENT TO PUT ABOVE MAX POINT. DOESN'T WORK WELL FOR SMALL VALUES
        _, toppoint = ax.get_ylim()
        toppoint = max(np.max(yvalues[0]), np.max(yvalues[1]))
        pct = 0.05
        ay, h, col = toppoint + toppoint * pct, toppoint * pct, 'k'

        ax.plot(
            [ii - width / 2, ii-width/2, ii+width/2, ii+width/2],
            [ay, ay+h, ay+h, ay],
            lw=1.5, color=col)

        ax.text(
            ii,
            ay+h,
            stars,
            ha='center',
            va='bottom')

    # FIGURE ATTRIBUTES
    ax.set_xticks(np.arange(len(xlabels))+1)
    ax.set_xticklabels(xlabels)
    custom_lines = [
                    Line2D([0], [0], color=colors["GG2 control"], lw=4),
                    Line2D([0], [0], color=colors["GG2 KO"], lw=4)]
    ax.legend(custom_lines, ["Control", "KO"], frameon=False,
        bbox_to_anchor=(1.04,0), loc="lower left")
    ax.tick_params(axis='x', which='both', length=0)

    if metric == "gain":
        ax.set_title("Gain at Background")
        ax.set_ylabel("Gain (1/R*)")
        ax.set_xlabel("Background Intensity (R*/S-Cone/s)")
    else:
        ax.set_title("Time to Peak Response")
        ax.set_ylabel("Time (s)")
        ax.set_xlabel("Background Intensity (R*/S-Cone/s)")

    plt.savefig(f"{metric}.png", dpi=600)


def test_specific_swarm_offs():
    # READ H5 FILES
    paramnames = ["led", "holdingpotential", "protocolname", "celltype",
                  "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
    tracetype = "spiketrace"
    protocolnames = ["LedPulse"]

    epochio = get_params(paramnames, protocolnames=protocolnames, tracetype=tracetype)

    # QUERY NODE
    params = dict(
        Name="LedSpikeAnalysis",
        protocolname="LedPulse",
        led="Green LED",
        celltype=r"RGC\OFF-sustained")

    eframe = epochio.query(filters=[params])
    df = epochtypes.groupby(eframe, ["protocolname", "led",
                            "celltype", "genotype", "cellname", "lightmean", "lightamplitude"])

    # PLOT FIGURE
    fig, ax = plt.subplots(figsize=(4,6))

    frame = df.loc[(df.lightamplitude == 10) & (df.lightmean == 0.0)]
    #frame["genotype"] = frame.genotype.apply(lambda x: "Control" if x == "GG2 control" else "KO")
    frame =frame.sort_values("genotype", ascending=False)

    plot = analysis.charting.PlotSwarm(ax,eframe=frame, igor=True)
    plot.ax.set_title("OFF-S")
    plot.ax.set_xticklabels(["Control", "KO"])

    fig.savefig("Swarm_Offsustained.png")
    plt.show()
    fig, ax = plt.subplots()


def test_specific_swarm_offt():
    # READ H5 FILES
    paramnames = ["led", "holdingpotential", "protocolname", "celltype",
                  "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
    tracetype = "spiketrace"
    protocolnames = ["LedPulse"]

    epochio = get_params(paramnames, protocolnames=protocolnames, tracetype=tracetype)

    # QUERY NODE
    params = dict(
        Name="LedSpikeAnalysis",
        protocolname="LedPulse",
        led="Green LED",
        celltype=r"RGC\OFF-transient")

    eframe = epochio.query(filters=[params])
    df = epochtypes.groupby(eframe, ["protocolname", "led",
                            "celltype", "genotype", "cellname", "lightmean", "lightamplitude"])

    # PLOT FIGURE
    fig, ax = plt.subplots(figsize=(4,6), tight_layout=True)

    frame = df.loc[(df.lightamplitude == 10) & (df.lightmean == 0.0)]
    #frame["genotype"] = frame.genotype.apply(lambda x: "Control" if x == "GG2 control" else "KO")
    frame =frame.sort_values("genotype", ascending=False)

    plot = analysis.charting.PlotSwarm(ax,eframe=frame, igor=True)
    plot.ax.set_title("OFF-T")
    plot.ax.set_xticklabels(["Control", "KO"])


    fig.savefig("Swarm_Offtransient.png")
    plt.show()
    fig, ax = plt.subplots()
