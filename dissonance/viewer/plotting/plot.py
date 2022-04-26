import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
from scipy.stats import ttest_ind
from datetime import datetime


def p_to_star(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "ns"


def def_value(): return "#003f5c"


COLORS = defaultdict(def_value)
COLORS["WT"] = "#003f5c"
COLORS["DR"] = "#2f4b7c"
COLORS["GA1"] = "#665191"
COLORS["GG2 control"] = "#a05195"
COLORS["GG2 KO"] = "#d45087"
COLORS["None"] = "#f95d6a"
# ff7c43
# ffa600

PCTCNTRST = pd.DataFrame(
    columns="lightamplitude lightmean pctcontrast".split(),
    data=[
        [-0.001, 0.005, -25],
        [-0.003, 0.005, -50],
        [-0.005, 0.005, -100],
        [0.001, 0.005, 25],
        [0.003, 0.005, 50],
        [0.005, 0.005, 100],
        [0.002, 0.007, 25],
        [0.004, 0.007, 50],
        [0.005, 0.007, 75],
        [0.007, 0.007, 100],
        [-0.002, 0.007, -25],
        [-0.004, 0.007, -50],
        [-0.005, 0.007, -75],
        [-0.007, 0.007, -100],
        [-0.002, 0.006, -25],
        [-0.003, 0.006, -50],
        [-0.006, 0.006, -100],
        [0.002, 0.006, 25],
        [0.003, 0.006, 50],
        [0.006, 0.006, 100],
        [-0.006, 0.006, -100],
        [0.002, 0.005, 50],
        [0.004, 0.005, 75],
        [-0.004, 0.005, -75],
        [0.005, 0.006, 75],
        [-0.005, 0.006, -75],
        [0.005, 0, 0],
        [0.006, 0, 0]])


def get_pctcntrst(lightamp, lightmean):
    try:
        return PCTCNTRST.loc[
            (PCTCNTRST.lightamplitude == lightamp) &
            (PCTCNTRST.lightmean == lightmean),
            "pctcontrast"
        ]
    except:
        return 0.0


class PlotPsth:

    def __init__(self, ax, epochs=None, label=None):
        self.ax = ax
        self.ax.grid(False)

        ax.set_ylabel("Hz / s")
        ax.set_xlabel("10ms bins")

        self.labels = []
        self.psths = []

        if epochs is not None:
            self.append_trace(epochs, label)

    def append_trace(self, epochs, label):
        n = len(epochs)
        psth = epochs.psth

        # TODO fix this
        try:
            name = epochs.genotypes[0]
            stimtime = epochs.stimtimes[0]
        except:
            name = epochs.genotype
            stimtime = epochs.stimtime

        # CALCULATE TTP AND MAX PEAK
        seconds_conversion = 10000 / 100
        ttp = (np.argmax(psth) + 1) / (seconds_conversion)
        x = (np.arange(len(psth)) + 1 - stimtime/100) / (seconds_conversion)
        self.ax.axvline(ttp, linestyle='--', color=COLORS[name], alpha=0.4)

        self.ax.plot(x, psth, label=f"{label} (n={n})", c=COLORS[name])

        # UPDATE LEGEND WITH EACH APPEND
        self.ax.legend()

        # SAVE DATA FOR STORING LATER
        self.labels.append(label)
        self.psths.append(psth)

    def to_csv(self, outputdir=None):
        columns = "Chart Label Time Value".split()

        dfs = []
        for label, psth in zip(self.labels, self.psths):
            df = pd.DataFrame(columns=columns)
            df["Value"] = psth
            df["Time"] = np.arange(len(psth))
            df["Label"] = label
            df["Chart"] = "PSTH"
            dfs.append(df)

        df = pd.concat(dfs)
        filename = f"PlotPsth_{datetime.now()}.csv"
        if outputdir:
            filename = outputdir / filename

        df.to_csv(filename, index=False)


class PlotRaster:

    def __init__(self, ax, epochs=None, title=None):
        self.ax = ax
        self.ax.grid(False)

        if title:
            self.ax.set_title(title)

        ax.set_ylabel("Hz / s")
        ax.set_xlabel("10ms bins")
        self.ax.axes.get_xaxis().set_visible(False)

        self.labels = []
        self.values = []

        if epochs is not None:
            self.append_trace(epochs)

    def append_trace(self, epochs):
        """Raster plots

        Args:
            epochs (Traces): Epoch traces to plot.
            ax (Axes, optional): Axis obj from parent figure, creates figure if not provided. Defaults to None.
        """
        if self.ax is None:
            fig, ax, = plt.subplots()

        toplt = []
        for ii, epoch in enumerate(epochs):
            spikes = epoch.spikes.sp / 10000
            y = [ii+1] * len(spikes)
            toplt.append((spikes, y))

        for x, y in toplt:
            self.ax.scatter(x, y, marker="|", c=COLORS[epochs.genotypes[0]])
            self.values.append(y)

        title = f"{epochs.rstarrs[0]}"
        self.ax.set_title(title)

        # SET THESE EACH LOOP?
        # self.ax.title.set_text(title)
        self.ax.set_yticks(np.arange(len(epochs))+1)
        self.ax.set_yticklabels([f"{epoch.number}" for epoch in epochs])

        for epoch in epochs:
            self.labels.append(epoch.startdate)

    def to_csv(self, outputdir=None):
        columns = "Chart Label Time Value".split()

        dfs = []
        for label, values in zip(self.labels, self.values):
            df = pd.DataFrame(columns=columns)
            df["Value"] = values
            df["Time"] = np.arange(len(values))
            df["Label"] = label
            df["Chart"] = "Raster"
            dfs.append(df)

        df = pd.concat(dfs)
        filename = f"PlotRaster_{datetime.now()}.csv"
        if outputdir:
            filename = outputdir / filename

        df.to_csv(filename, index=False)


class PlotTrace:

    def __init__(self, ax, epoch=None):
        self.ax = ax

        ax.set_ylabel("pA")
        ax.set_xlabel("10e-4 seconds")

        self.labels = []
        self.values = []

        if epoch is not None:
            self.append_trace(epoch)

    def append_trace(self, epoch):
        """Plot traces

        Args:
            epoch (SpikeTraces): Epochs to trace
            ax ([type]): Matlab figure axis
        """
        if (
                epoch.type == "spiketrace"
                and epoch.spikes.sp is not None):
            y = epoch.values[epoch.spikes.sp]
            # WANT 0 TO BE STIM TIME
            self.ax.scatter(
                epoch.spikes.sp - epoch.stimtime,
                y,
                marker="x", c=COLORS[epoch.genotype])

        self.ax.plot(
            np.arange(len(epoch.values)) - epoch.stimtime,
            epoch.values, label=epoch.startdate,
            color=COLORS[epoch.genotype], alpha=0.4)

        self.labels.append(epoch.startdate)
        self.values.append(epoch.values)

        self.ax.legend()

    def to_csv(self, outputdir=None):
        columns = "Chart Label Time Value".split()

        dfs = []
        for label, values in zip(self.labels, self.values):
            df = pd.DataFrame(columns=columns)
            df["Value"] = values
            df["Time"] = np.arange(len(values))
            df["Label"] = label
            df["Chart"] = "Trace"
            dfs.append(df)

        df = pd.concat(dfs)
        filename = f"PlotTrace_{datetime.now()}.csv"
        if outputdir:
            filename = outputdir / filename

        df.to_csv(filename, index=False)


class PlotSwarm:

    def __init__(self, ax, metric: str = "peakamplitude", epochs=None):
        self.ax = ax
        self.metric = metric

        self.values = []

        if epochs is not None:
            self.append_trace(epochs)

        self.ax.grid(False)

    def append_trace(self, epochs: pd.DataFrame) -> None:
        """Swarm plot :: bar graph of means with SEM and scatter. Show signficance

        Args:
            epochs (Dict[str,SpikeTraces]): Maps genos name to traces to plot.
            ax (Axes, optional): Axis obj from parent figure, creates figure if not provided. Defaults to None.
        """
        if self.ax is None:
            fig, ax, = plt.subplots()

        # FOR EACH GENOTYPE
        # FOR EACH CELL IN CELLS (each epoch stored as indiviudal cell)
        toplt = []
        ymax = 0.0
        toppoint = 0.0  # NEED AXIS TO BE % ABOVE SEM BAR
        for ii, (name, frame) in enumerate(epochs.groupby("genotype")):
            celltraces = frame.trace.values

            if self.metric == "peakamplitude":
                values = np.array([
                    np.max(cell.psth)
                    for cell in celltraces
                ], dtype=float)

            else:
                values = np.array([
                    np.argmax(cell.psth)
                    for cell in celltraces
                ], dtype=float)

            meanval = np.mean(values)
            sem = np.std(values) / np.sqrt(len(values))

            # CHANGE SIGN OF AXIS IF NEEDED
            ymax = max(ymax, np.max(values)) if meanval > 0 else min(
                ymax, np.max(values))
            toppoint = max(toppoint, meanval +
                           sem) if meanval > 0 else min(toppoint, meanval-sem)
            toppoint = max(toppoint, ymax) if toppoint > 0 else min(
                toppoint, ymax)

            toplt.append(
                dict(
                    color=COLORS[name],
                    label=name,
                    values=values,
                    meanvalue=meanval,
                    sem=sem))

            self.ax.bar(ii,
                        height=meanval,
                        yerr=sem,
                        capsize=12,
                        tick_label=name,
                        alpha=0.5,
                        color=COLORS[name])

            # PLOT SCATTER
            self.ax.scatter(
                np.repeat(ii, len(values)),
                values,
                alpha=0.25,
                c=COLORS[name])

            self.values.extend(toplt)

            # LABEL NUMBER OF CELLS
            self.ax.text(ii, 0, f"n={len(values)}",
                         ha='center', va='bottom', color='k')

        # CALCULATE SIGNIFICANCE
        if len(toplt) > 1:
            stat, p = ttest_ind(
                toplt[0]["values"], toplt[1]["values"])

            stars = p_to_star(p)
            stars = f"p={p:0.03f}" if stars == "ns" and p < 0.06 else stars
            x1, x2 = 0, 1  # ASSUME ONLY 2

            # PLOT SIGNFICANCE LABEL
            # HACK PERCENT TO PUT ABOVE MAX POINT. DOESN'T WORK WELL FOR SMALL VALUES
            pct = 0.05
            ay, h, col = toppoint + toppoint * pct, toppoint * pct, 'k'

            self.ax.plot(
                [x1, x1, x2, x2],
                [ay, ay+h, ay+h, ay],
                lw=1.5, c=col)

            self.ax.text(
                (x1+x2)*.5,
                ay+h,
                stars,
                ha='center', va='bottom',
                color=col)

        # FIG SETTINGS
        rstarr = epochs.rstarr.iloc[0]
        self.ax.set_title(f"{self.metric}: {rstarr}")

        # X AXIS FORMAT
        self.ax.xaxis.set_ticks_position('none')
        self.ax.set_xticks(np.arange(len(toplt)), dtype=float)
        self.ax.set_xticklabels([x["label"] for x in toplt])
        self.ax.set_xlabel("Background (R*/S-Cone/sec)")

        # Y AXIS FORMAT
        self.ax.set_ylabel("pA")
        self.ax.set_ylim((0.0, toppoint * 1.20))

    def to_csv(self, filepath=None):
        # TODO what data is needed for this?
        ...


class PlotCRF:

    def __init__(self, ax, metric, epochs):
        self.ax = ax
        self.metric = metric

        self.set_axis_labels()

        # for performing a ttest
        self.peakamps = defaultdict(list)
        self.cntr = 0

        # for writing to csv
        self.labels = []
        self.xvalues = []
        self.yvalues = []

        if epochs:
            self.append_trace(epochs)

    def append_trace(self, epochs: pd.DataFrame):
        self.cntr += 1
        X = []
        Y = []
        sems = []
        genotype = epochs.genotype.iloc[0]
        for rstarr, frame in epochs.groupby("rstarr"):
            lightamplitude, lightmean = frame[[
                "lightamplitude", "lightmean"]].iloc[0, :]
            contrast = get_pctcntrst(lightamplitude, lightmean)

            peakamps = np.array([
                np.max(epoch.psth)
                for epoch in frame.trace.values
            ])

            X.append(contrast)
            Y.append(np.mean(peakamps))
            sems.append(peakamps.std() / np.sqrt(len(peakamps)))

            self.peakamps[genotype].append(peakamps)

        self.ax.errorbar(
            X, Y,
            yerr=sems,
            label=genotype,
            color=COLORS[genotype])

        self.labels.append(genotype)
        self.xvalues.append(X)
        self.yvalues.append(Y)

        if self.cntr == 2:
            self.t_test()

    def set_axis_labels(self):
        self.ax.legend()
        self.ax.set_xlabel("Percent Contrast")
        if self.metric == "TimeToPeak":
            self.ax.set_ylabel("Seconds")
            self.ax.set_title("1000 R* Contrast Steps: Time to Peak")
        else:
            self.ax.set_ylabel("pA")
            self.ax.set_title("1000 R* Contrast Response")

    def t_test(self):
        g1, g2 = self.labels[:2]
        v1 = self.peaksamps[g1]
        v2 = self.peaksamps[g2]

        for a1, a2 in zip(v1, v2):
            stat, p = ttest_ind(
                a1, a2)
            stars = p_to_star(p)

            # GETS POSITION TO WRITE STARS
            # ON TOP MOST ERROR BAR
            ymax = max(
                np.mean(a1) + np.std(a1) / np.sqrt(len(a1)),
                np.mean(a2) + np.std(a1) / np.sqrt(len(a2)))

            self.ax.text(
                self.xvalues[0],  # ASSUME IN SAME ORDER
                ymax*1.05,
                stars,
                ha='center',
                va='bottom', color='k', rotation=90)

    def to_csv(self):
        ...

class PlotHill:

    def __init__(self, ax, epochs):

        self.ax = ax

        if epochs:
            self.append_trace(epochs)

    def append_trace(self, epochs):
        ...