from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, List, Dict
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
from scipy.stats import ttest_ind, sem
from datetime import datetime
from ..epochtypes import IEpoch, WholeEpoch, WholeEpochs
from ..funks import HillEquation, WeberEquation


def p_to_star(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "ns"


# MORE COLORS TO USE: ff7c43, ffa600
def def_value():
    """DUMMY FUNCTION FOR DEFAULT DICT COLORS"""
    return "#003f5c"


COLORS = defaultdict(def_value)
COLORS["WT"] = "#003f5c"
COLORS["DR"] = "#2f4b7c"
COLORS["GA1"] = "#665191"
COLORS["GG2 control"] = "#a05195"
COLORS["GG2 KO"] = "#d45087"
COLORS["None"] = "#f95d6a"


class PlotBase(ABC):

    @abstractmethod
    def append_trace(self, *args, **kwargs):
        ...

    @abstractmethod
    def to_csv(self, *args, **kwargs):
        ...
    
    @abstractmethod
    def to_image(self, *args, **kwargs):
        ...

    @abstractmethod
    def to_igor(self, *args, **kwargs):
        ...



class PlotPsth(PlotBase):

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

        name = epochs.get_unique("genotype")[0]
        stimtime = epochs.get_unique("stimtime")[0]

        # CALCULATE TTP AND MAX PEAK
        seconds_conversion = 10000 / 100
        ttp = (np.argmax(psth) + 1 - stimtime/100) / (seconds_conversion)
        x = (np.arange(len(psth)) + 1 - stimtime/100) / (seconds_conversion)

        # PLOT VALUES SHIFT BY STIM TIME
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

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...


class PlotRaster(PlotBase):

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

        genotype = epochs.get_unique("genotype")[0]

        toplt = []
        for ii, epoch in enumerate(epochs):
            spikes = epoch.spikes.sp / 10000
            y = [ii+1] * len(spikes)
            toplt.append((spikes, y))

        for x, y in toplt:
            self.ax.scatter(x, y, marker="|", c=COLORS[genotype])
            self.values.append(y)

        title = f"{epochs.get_unique('lightamplitude')[0]}, {epochs.get_unique('lightmean')[0]}"
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

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...


class PlotWholeTrace(PlotBase):

    def __init__(self, ax, epoch=None):
        self.ax = ax
        ax.grid(False)

        if epoch is not None:
            self.append_trace(epoch)

    def append_trace(self, epoch=Union[WholeEpoch, WholeEpochs]):
        """Plot traces
        """
        # GET ATTRIBUTES FOR PLOT
        stimtime = epoch.get("stimtime")[0]
        if isinstance(epoch, IEpoch):
            label = epoch.startdate
            genotype = epoch.genotype
        else:
            label = f'{epoch.get("cellname")[0]}, {epoch.get("lightamplitude")[0]}, {epoch.get("lightmean")}'
            genotype = epoch.get("genotype")[0]

        # PLOT TRACE VALUES
        self.ax.plot(
            np.arange(len(epoch.trace)) - stimtime,
            epoch.trace, label=label,
            color=COLORS[epoch.get("genotype")[0]],
            alpha=0.4)

        # PLOT HALF WIDTH
        whm = epoch.widthathalfmax
        wrange = epoch.widthrange

        # HORIZONTAL LINE ACROSS HALF MAX
        self.ax.line(
            wrange, [whm, whm],
            marker="--",
            color=COLORS[genotype])

        # MARKER ON PEAK AMPLITUDE
        self.scatter(
            epoch.timetopeak, epoch.peakamplitude,
            marker="x")

        self.labels.append(label)
        self.values.append(epoch.trace)

        self.ax.legend()

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...


class PlotTrace(PlotBase):

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
        """
        # GET ATTRIBUTES FOR PLOT
        stimtime = epoch.get("stimtime")[0]
        if isinstance(epoch, IEpoch):
            label = epoch.startdate
        else:
            label = f'{epoch.get("cellname")[0]}, {epoch.get("lightamplitude")[0]}, {epoch.get("lightmean")}'

        # PLOT SPIKES IF SPIKETRACE
        if (epoch.type == "spiketrace" and epoch.spikes.sp is not None):
            y = epoch.trace[epoch.spikes.sp]
            self.ax.scatter(
                epoch.spikes.sp - stimtime,
                y,
                marker="x", c=COLORS[epoch.genotype])

        # PLOT TRACE VALUES
        self.ax.plot(
            np.arange(len(epoch.trace)) - stimtime,
            epoch.trace, label=label,
            color=COLORS[epoch.get("genotype")[0]],
            alpha=0.4)

        self.labels.append(label)
        self.values.append(epoch.trace)

        self.ax.legend()

    def to_csv(self, outputdir=None):
        columns = "Chart Label Time Value".split()

        dfs = []
        for label, values in zip(self.labels, self.values):
            df = pd.DataFrame(columns=columns)
            df["Value"] = values
            df["Time"] = np.arange(len(values))
            # TODO split label up to get component keys. Try to associate a label with every epoch list for unique attributes
            df["Label"] = label
            df["Chart"] = "Trace"
            dfs.append(df)

        df = pd.concat(dfs)
        filename = f"PlotTrace_{datetime.now()}.csv"
        if outputdir:
            filename = outputdir / filename

        df.to_csv(filename, index=False)

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...


class PlotSwarm(PlotBase):

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
            semval = sem(values)

            # CHANGE SIGN OF AXIS IF NEEDED
            ymax = max(ymax, np.max(values)) if meanval > 0 else min(
                ymax, np.max(values))
            toppoint = max(toppoint, meanval +
                           semval) if meanval > 0 else min(toppoint, meanval-semval)
            toppoint = max(toppoint, ymax) if toppoint > 0 else min(
                toppoint, ymax)

            toplt.append(
                dict(
                    color=COLORS[name],
                    label=name,
                    values=values,
                    meanvalue=meanval,
                    semval=semval))

            self.ax.bar(ii,
                        height=meanval,
                        yerr=semval,
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
        lightamplitude, lightmean = epochs[[
            "lightamplitude", "lightmean"]].iloc[0]
        self.ax.set_title(f"{self.metric}: {lightamplitude, lightmean}")

        # X AXIS FORMAT
        self.ax.xaxis.set_ticks_position('none')
        self.ax.set_xticks(np.arange(len(toplt)), dtype=float)
        self.ax.set_xticklabels([x["label"] for x in toplt])
        self.ax.set_xlabel("Background (R*/S-Cone/sec)")

        # Y AXIS FORMAT
        self.ax.set_ylabel("pA")
        self.ax.set_ylim((0.0, toppoint * 1.20))

    def to_csv(self, filepath=None):
        ...

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...


class PlotCRF(PlotBase):

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

        if epochs is not None:
            self.append_trace(epochs)

    def append_trace(self, epochs: pd.DataFrame):
        self.cntr += 1
        X = []
        Y = []
        sems = []
        genotype = epochs.genotype.iloc[0]
        for (lightamp, lightmean), frame in epochs.groupby(["lightamplitude", "lightmean"]):
            contrast = float(lightamp) / float(lightmean) if float(lightmean) != 0.0 else 0.0

            # GET PEAK AMPLITUDE FROM EACH PSTH - USED IN SEM
            peakamps = np.array([
                np.max(epoch.psth) if self.metric == "peakamplitude" else np.argmax(epoch.psth)
                for epoch in frame.trace.values
            ])

            X.append(contrast)
            Y.append(np.mean(peakamps))
            sems.append(0.0 if len(peakamps) == 1 else sem(peakamps))

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
                np.mean(a1) + sem(a1),
                np.mean(a2) + sem(a2))

            self.ax.text(
                self.xvalues[0],  # ASSUME IN SAME ORDER
                ymax*1.05,
                stars,
                ha='center',
                va='bottom', color='k', rotation=90)

    def to_csv(self):
        ...

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...


class PlotHill(PlotBase):

    def __init__(self, ax, epochs):
        self.ax = ax
        self.fits = dict()

        if epochs:
            self.append_trace(epochs)

    def append_trace(self, epochs: pd.DataFrame):
        """HILL FIT ON EACH CELL AND AVERAGE OF EACH CELLS"""
        # EPOCH SEPARATED BY CELL, LIGHTAMPLITUDE. ASSUMING SAME LIGHT MEAN
        genotype = epochs.genotype.iloc[0]

        # TODO will this be done on epoch level?
        # FIT HILL TO EACH CELL - ONLY PLOT PEAK AMOPLITUDES
        for cellname, frame in epochs.groupby(["cellname"]):
            frame = frame.sort_values(["lightamplitude"])
            X = frame.lightamplitude.values
            Y = frame.trace.apply(lambda x: x.peakamplitude).values

            hill = HillEquation()
            hill.fit(X, Y)
            self.fits[cellname] = hill

        # FIT HILL TO AVERAGE OF PEAK AMPLITUDES
        df = epochs.copy()
        df["peakamp"] = epochs.trace.apply(lambda x: x.peakamplitude)
        dff = df.groupby("lightamplitude").peakamp.mean().reset_index()

        # PLOT LINE AND AVERAGES
        X, Y = dff.lightamplitude.values, dff.peakamp.values
        hill = HillEquation()
        hill.fit(X, Y)
        self.ax.plot(X, hill(Y), color=COLORS[genotype])
        self.ax.scatter(X, Y, alpha=0.4, color=COLORS[genotype])

        # TODO decide on label based on grouping
        self.fits[f"{genotype}_average"] = hill

    def to_csv(self):
        ...

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...

class PlotWeber(PlotBase):

    def __init__(self, ax, epochs):
        self.ax = ax
        self.fits: Dict[str, WeberEquation] = dict()

        self.ax.set_yscale("log")
        self.ax.set_xscale("log")

        if epochs:
            self.append_trace(epochs)

    def filestem(self):
        return f"PlotWeber_{'_'.join([x for x in self.fits])}"

    def append_trace(self, epochs: pd.DataFrame):
        """HILL FIT ON EACH CELL AND AVERAGE OF EACH CELLS"""
        # EPOCH SEPARATED BY CELL, LIGHTAMPLITUDE. ASSUMING SAME LIGHT MEAN
        genotype = epochs.genotype.iloc[0]

        # FIT HILL TO EACH CELL - ONLY PLOT PEAK AMPLITUDES
        for cellname, frame in epochs.groupby(["cellname"]):
            frame = frame.sort_values(["lightamplitude"])
            X = frame.lightamplitude.values
            Y = frame.trace.apply(lambda x: x.peakamplitude).values

            weber = WeberEquation()
            weber.fit(X, Y)

            self.fits[cellname] = weber

        # FIT HILL TO AVERAGE OF PEAK AMPLITUDES
        df = epochs.copy()
        df["peakamp"] = epochs.trace.apply(lambda x: x.peakamplitude)
        dff = df.groupby("lightamplitude").peakamp.mean().reset_index()

        # FIT WEBER TO AVERAGE PEAK AMPLITUDES
        weber = WeberEquation()
        X, Y = dff.lightamplitude.values, dff.peakamp.values
        weber.fit(X, Y)

        # PLOT LINE AND AVERAGES
        topltX = np.array(40000)

        # TODO decide on line labels
        self.ax.plot(topltX, weber(X), color=COLORS[genotype])
        self.ax.scatter(*weber.normalize(X, Y),
                        alpha=0.4, color=COLORS[genotype])

        self.fits[f"{genotype}mean"] = weber

    def to_csv(self, outputdir: Path = Path(".")):
        data = []
        for label, fit in self.fits.items():
            row = [
                label,
                fit.beta,
                fit.r2
            ]
            data.append(row)

        df = pd.DataFrame(
            columns = "Label Beta R2".split(),
            data = data
        )

        outputpath = outputdir / (self.filestem + "_Data.csv")
        df.to_csv(outputpath, index=False)

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...