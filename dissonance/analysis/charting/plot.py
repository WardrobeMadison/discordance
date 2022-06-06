from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Dict, List, Union

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import numpy as np
import pandas as pd
from matplotlib.pyplot import Axes
from scipy.stats import sem, ttest_ind

from ...epochtypes import IEpoch, WholeEpoch, WholeEpochs, SpikeEpoch, SpikeEpochs
from ...funks import HillEquation, WeberEquation


import logging
logger = logging.getLogger(__name__)


def p_to_star(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "ns"


class Pallette:

    black = "#000000"
    red = "#CC0000"
    green =  "#6a9a23"
    purple= "#441488"

    orange = "#FFA500"

    ccolors = dict()
    ccolors["WT"] = "#545354"
    ccolors["DR"] = "#946073"
    ccolors["GA1"] = "#715b68"
    ccolors["GA1 control"] = "#b86473"
    ccolors["GG2 KO"] = "#d86b69"
    ccolors["GG2 control"] = "#fe8c3a"
    ccolors["None"] = "#f07856"
    #545354
    #715b68
    #946073
    #b86473
    #d86b69
    #f07856
    #fe8c3a
    #ffa600

    def __init__(self, igor:bool=False):
        self.igor = igor
    
    def __getitem__(self, value):
        if self.igor:
            color = None
            if any([x in value for x in ["control", "DR"]]):
                color =  self.green
            elif any([x in value for x in ["WT", "GA1", "KO"]]):
                color =  self.purple
            else:
                color = self.orange
            return color
        else: 
            return self.ccolors.get(value, self.orange)


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

    def __init__(self, ax: Axes, epochs:Union[SpikeEpoch, SpikeEpochs]=None, label=None, igor=False):
        self.ax: Axes = ax

        self.ax.grid(False)
        self.ax.margins( y=0)
        self.ax.set_ylabel("Hz / s")
        self.ax.set_xlabel("10ms bins")

        self.colors = Pallette(igor)

        self.labels = []
        self.psths = []
        self.Xs = []
        self.cntr = 0

        if epochs is not None:
            self.append_trace(epochs, label)

    def __str__(self):
        return f"{type(self).__name__}({','.join(map(str,self.labels))})"

    def append_trace(self, epochs:Union[SpikeEpoch, SpikeEpochs], label):
        self.cntr += 1

        seconds_conversion = 10000 / 100
        if isinstance(epochs, IEpoch):
            n = 1
            psth = epochs.psth
            name = epochs.get_unique("genotype")[0]
            stimtime = epochs.get_unique("stimtime")[0]
            ttp = (epochs.timetopeak - stimtime/100) / seconds_conversion
        elif isinstance(epochs, SpikeEpochs):
            n = len(epochs)
            psth = epochs.psth

            name = epochs.get_unique("genotype")[0]
            stimtime = epochs.get_unique("stimtime")[0]
            ttp = (epochs.timetopeak - stimtime/100) / seconds_conversion
        else:
            psth = np.mean(
                [
                    epoch.psth
                    for epoch in epochs
                ], axis=1
            )
            n = len(epochs)
            name = epochs.genotype.iloc[0]
            stimtime = epochs.epoch.iloc[0].stimtime

        # CALCULATE TTP AND MAX PEAK
        X = (np.arange(len(psth)) - stimtime/100) / (seconds_conversion)

        # PLOT VALUES SHIFT BY STIM TIME - DOTTED LINED FOR BOTH TTP AND PEAK AMP
        peakamp = epochs.peakamplitude
        self.ax.axvline(
            ttp, 
            linestyle='--', 
            color=self.colors[name], 
            alpha=0.4)
        self.ax.plot(X, psth, label=f"{label}(n={n})\nttp={ttp:.3f}, pa={peakamp:.1f}", color=self.colors[name])

        # UPDATE LEGEND WITH EACH APPEND
        # TEXT BOX TO THE LEFT
        self.ax.legend(bbox_to_anchor = (1.04, 0.5), loc="center left")

        # SAVE DATA FOR STORING LATER
        self.labels.append(label)
        self.Xs.append(X)
        self.psths.append(psth)

        if self.cntr == 1:
            # SHADE STIM TIME
            self.ax.axvspan(0, (stimtime / 10000), alpha=0.05, color='black')

        xticks = (
            [min(X)]
            + list(np.arange(0, max(X), 0.5)))

        self.ax.set_xticks(xticks)

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

    def __init__(self, ax, epochs:Union[SpikeEpoch, SpikeEpochs]=None, title=None, igor=False):
        self.ax = ax

        # INITIAL AXIS SETTINGS
        self.ax.grid(False)
        self.ax.spines["bottom"].set_visible(False)
        self.ax.axes.get_xaxis().set_visible(False)
        self.ax.set_title(title)

        self.colors = Pallette(igor)

        # USED FOR WRITING OUT DATA IN TO_*() METHODS
        self.labels = []
        self.values = []

        if epochs is not None:
            self.append_trace(epochs)

    def __str__(self):
        return f"{type(self).__name__}({','.join(map(str,self.labels))})"

    def append_trace(self, epochs:Union[SpikeEpoch, SpikeEpochs]):
        """Raster plots

        Args:        #self.ax.legend()

            epochs (Traces): Epoch traces to plot.
            ax (Axes, optional): Axis obj from parent figure, creates figure if not provided. Defaults to None.
        """
        if self.ax is None:
            fig, ax, = plt.subplots()

        genotype = epochs.get_unique("genotype")[0]

        toplt = []
        for ii, epoch in enumerate(epochs):
            spikes = epoch.spikes / 10000
            y = [ii+1] * len(spikes)
            toplt.append((spikes, y))

        for x, y in toplt:
            self.ax.scatter(x, y, marker="|", color=self.colors[genotype])
            self.values.append(y)

        title = f"{epochs.get_unique('lightamplitude')[0]}, {epochs.get_unique('lightmean')[0]}"
        self.ax.set_title(title)

        # SET THESE EACH LOOP?
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
    cmap = plt.get_cmap("tab10")

    def __init__(self, ax:Axes, epoch:Union[WholeEpoch, WholeEpochs]=None, igor=False, summarytype="epoch"):
        self.ax = ax
        self.ax.grid(False)
        #self.ax.margins(x=0, y=0)
        #self.ax.yaxis.set_visible(False)
        #self.ax.spines["left"].set_visible(False)

        # IF SUMMARIZING CELL NEED A DIFFERENT COLOR FOR EACH CELL, NOT GENOTYPE
        self.summarytype = summarytype
        self.colors = Pallette(igor)

        # LISTS USED IN EXPORTING DATA
        self.labels = []
        self.values = []
        
        # KEEP TRACK OF NUMBER OF PLOTS. MAYBE USED TO CYCLE COLORS IF IN CELL SUMMARY MODE
        self.cntr = 0

        if epoch is not None:
            self.append_trace(epoch)

    def __str__(self):
        return f"{type(self).__name__}({','.join(map(str,self.labels))})"

    def append_trace(self, epoch=Union[WholeEpoch, WholeEpochs]):
        """Plot traces
        """
        # GET ATTRIBUTES FOR PLOT
        stimtime = epoch.get("stimtime")[0]
        if isinstance(epoch, IEpoch):
            label = epoch.startdate
            genotype = epoch.genotype
        else:
            if self.summarytype == "cellname":
                label = epoch.get("cellname")[0]
            elif self.summarytype == "genotype":
                label = epoch.get("genotype")[0]
            elif self.summarytype == "block":
                label = f'{epoch.get("lightamplitude")[0]}, {epoch.get("lightmean")[0]}'
            else:
                label = f'{epoch.get("lightamplitude")[0]}, {epoch.get("lightmean")[0]}'
            genotype = epoch.get("genotype")[0]

        if self.summarytype == "genotype":
            color = self.colors[genotype]
        elif self.summarytype == "cellname":
            color = self.cmap(self.cntr)
        elif self.summarytype == "epoch":
            color = "black"
        else:
            color = self.colors[genotype]

        # PLOT HALF WIDTH
        whm = epoch.width_at_half_max
        start, stop = epoch.widthrange
        peakamp = epoch.peakamplitude

        metricstr = f"whm={whm},ttp={start},pa={peakamp:.0f}"
        label += "\n"+metricstr

        # PLOT TRACE VALUES
        X = np.arange(len(epoch.trace)) - stimtime
        self.ax.plot(
            X,
            epoch.trace, label=label,
            color=color,
            alpha=0.4)

        # HORIZONTAL LINE ACROSS HALF MAX
        y1, y2 = epoch.trace[start], epoch.trace[stop]
        x1, x2 = start - stimtime, stop - stimtime

        self.ax.plot(
            [x1, x2], [y1, y2],
            "--", color=color)

        # MARKER ON PEAK AMPLITUDE
        self.ax.scatter(
            epoch.timetopeak - stimtime, epoch.peakamplitude,
            marker="x",
            color=color)

        # APPEND VALUES NEEDED FOR WRITING OUT
        self.labels.append(label)
        self.values.append(epoch.trace)

        # UPDATE AXIS LEGEND - MOVE TO SIDE
        self.ax.legend(bbox_to_anchor=(1.04, 0.50), loc="center left")

        # ADD X TICKS
        xticks = [min(X)] + list(np.arange(0, max(X), 5000))
        xlabels = [f"{x/10000:0.1f}" for x in xticks]

        self.ax.xaxis.set_ticks(xticks)
        self.ax.xaxis.set_ticklabels(xlabels)
        self.ax.set_xlim((min(X), max(X)))

        #try:
        #    # REMOVE BEGINNING AND END POINT. ALSO REMOVE 0.0
        #    self.ax.xaxis.get_ticklabels()[0].set_visible(False)
        #    self.ax.xaxis.get_ticklabels()[-1].set_visible(False)
        #except:
        #    print("Couldn't remove ticks")

        self.cntr += 1

    def to_csv(self, *args, **kwargs):
        ...

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...


class PlotTrace(PlotBase):

    def __init__(self, ax: Axes, epoch:IEpoch=None, igor=False):
        self.ax: Axes = ax

        self.ax.set_ylabel("pA")
        self.ax.set_xlabel("seconds")
        self.ax.margins(y=0)
        self.ax.spines["left"].set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        self.colors = Pallette(igor)

        self.labels = []
        self.values = []

        if epoch is not None:
            self.append_trace(epoch)

    def __str__(self):
        return f"{type(self).__name__}({','.join(map(str,self.labels))})"

    def append_trace(self, epoch:IEpoch):
        """Plot traces
        """
        # GET ATTRIBUTES FOR PLOT
        stimtime = epoch.get("stimtime")[0]
        if isinstance(epoch, IEpoch):
            label = epoch.startdate
        else:
            label = f'{epoch.get("cellname")[0]}, {epoch.get("lightamplitude")[0]}, {epoch.get("lightmean")}'

        # PLOT SPIKES IF SPIKETRACE
        if (epoch.type == "spiketrace" and epoch.spikes is not None):
            y = epoch.trace[epoch.spikes]
            self.ax.scatter(
                epoch.spikes - stimtime,
                y,
                marker="x", color=self.colors[epoch.genotype])

        # PLOT TRACE VALUES
        X = np.arange(len(epoch.trace)) - stimtime
        self.ax.plot(
            X,
            epoch.trace, label=label,
            color=self.colors[epoch.get("genotype")[0]],
            alpha=0.4)

        # FORMAT AXES - EVERY 0.5 SECONDS FROM STIMTIME MARKED AT 0.0
        xticks = [min(X)] + list(np.arange(0, max(X), 5000))
        xlabels = [f"{x/10000:.1f}" for x in xticks]

        self.ax.set_xticks(xticks)
        self.ax.set_xticklabels(xlabels)

        self.labels.append(label)
        self.values.append(epoch.trace)

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


class PlotSpikeTrain(PlotBase):

    def __init__(self, ax: Axes, epoch:IEpoch=None, igor=False):
        self.ax: Axes = ax

        self.ax.set_ylabel("pA")
        self.ax.set_xlabel("seconds")
        self.ax.margins( y=0)
        self.ax.spines["left"].set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        self.colors = Pallette(igor)

        self.labels = []
        self.values = []

        if epoch is not None:
            self.append_trace(epoch)

    def __str__(self):
        return f"{type(self).__name__}({','.join(map(str,self.labels))})"

    def append_trace(self, epoch:IEpoch):
        """Plot traces
        """
        # GET ATTRIBUTES FOR PLOT
        stimtime = epoch.get("stimtime")[0]
        if isinstance(epoch, IEpoch):
            label = epoch.startdate
        else:
            label = f'{epoch.get("cellname")[0]}, {epoch.get("lightamplitude")[0]}, {epoch.get("lightmean")}'

        # PLOT SPIKES IF SPIKETRACE
        if (epoch.type == "spiketrace" and epoch.spikes is not None):
            y = epoch.trace[epoch.spikes]
            self.ax.scatter(
                epoch.spikes - stimtime,
                y,
                marker="x", color=self.colors[epoch.genotype])

        # PLOT TRACE VALUES
        X = np.arange(len(epoch.trace)) - stimtime
        self.ax.plot(
            X,
            epoch.trace, label=label,
            color=self.colors[epoch.get("genotype")[0]],
            alpha=0.4)

        # FORMAT AXES
        xticks = [min(X)] + list(np.arange(0, max(X), 5000))
        xlabels = [f"{x/10000:.1f}" for x in xticks]

        self.ax.set_xticks(xticks)
        self.ax.set_xticklabels(xlabels)

        self.labels.append(label)
        self.values.append(epoch.trace)

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

    def __init__(self, ax: Axes, metric: str = "peakamplitude", eframe:pd.DataFrame=None, igor=False):
        self.ax: Axes = ax
        self.metric = metric
        #self.ax.margins(y=0)

        # INITIAL AXIS SETTINGS
        #self.ax.spines["bottom"].set_visible(False)
        self.ax.grid(False)

        self.colors = Pallette(igor)

        # USE TO WRITE VALUES OUT IN TWO METHODS
        self.values = []
        self.labels = []

        if eframe is not None:
            self.append_trace(eframe)

    def __str__(self):
        return f"{type(self).__name__}({','.join(map(str,self.labels))})"

    def append_trace(self, eframe: pd.DataFrame) -> None:
        """Swarm plot :: bar graph of means with SEM and scatter. Show signficance

        Args:
            epochs (Dict[str,SpikeTraces]): Maps genos name to traces to plot.
            ax (Axes, optional): Axis obj from parent figure, creates figure if not provided. Defaults to None.
        """
        # FOR EACH GENOTYPE
        # FOR EACH CELL IN CELLS (each epoch stored as indiviudal cell)
        toplt = []
        ymax = 0.0
        toppoint = 0.0  # NEED AXIS TO BE % ABOVE SEM BAR
        for ii, (name, frame) in enumerate(eframe.groupby("genotype",sort=False)):
            celltraces = frame.epoch.values

            if self.metric == "peakamplitude":
                values = np.array([
                    cell.peakamplitude
                    for cell in celltraces
                ], dtype=float)

            elif self.metric == "timetopeak":
                values = np.array([
                    cell.timetopeaksec
                    for cell in celltraces
                ], dtype=float)

            meanval = np.mean(values)
            semval = sem(values)

            # CHANGE SIGN OF AXIS IF NEEDED
            # Compare within current genotype and then to other values
            ymax = (
                max(ymax, np.max(values)) 
                if meanval >= 0 
                else min(ymax, np.min(values)))
            toppoint = (
                    max(toppoint, meanval + semval) 
                    if meanval >= 0 else 
                    min(toppoint, meanval-semval))
            toppoint = (
                max(toppoint, ymax) 
                if toppoint >= 0 else 
                min(toppoint, ymax))

            toplt.append(
                dict(
                    color=self.colors[name],
                    label=name,
                    values=values,
                    meanvalue=meanval,
                    semval=semval))

            self.ax.bar(ii,
                        height=meanval,
                        yerr=semval,
                        #capsize=12,
                        tick_label=name,
                        alpha=0.5,
                        edgecolor=self.colors[name],
                        linewidth = 2,
                        capsize=5,
                        color='None')

            # PLOT SCATTER
            self.ax.scatter(
                np.repeat(ii, len(values)),
                values,
                alpha=0.25,
                color=self.colors[name])

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
                lw=1.5, color=col)

            self.ax.text(
                (x1+x2)*.5,
                ay+h,
                stars,
                ha='center', va='bottom',
                color=col)

        # FIG SETTINGS
        lightamplitude, lightmean = eframe[[
            "lightamplitude", "lightmean"]].iloc[0]
        self.ax.set_title(f"{self.metric}: {lightamplitude, lightmean}")

        # X AXIS FORMAT
        self.ax.xaxis.set_ticks_position('none')
        self.ax.set_xticks(np.arange(len(toplt)), dtype=float)
        self.ax.set_xticklabels([x["label"] for x in toplt])

        # Y AXIS FORMAT
        ymax = toppoint * 1.20
        self.ax.set_ylim((0.0, ymax))
        if self.metric == "peakamplitude":
            self.ax.set_ylabel("Response (Hz)")
        else:
            self.ax.set_ylabel("seconds")

        # WHAT AXIS TO END ON TOP TICK MARK. GET THE TICKS AND ADD LIMIT TO TICK LABELS
        yticks = self.ax.get_yticks()
        yticks = np.array([*yticks, ymax])
        self.ax.set_yticks = yticks
        self.ax.set_yticklabels = yticks

        self.labels.append([lightamplitude, lightmean])

    def to_csv(self, filepath=None):
        ...

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...

class PlotWholeCRF(PlotBase):

    def __init__(self, ax: Axes, metric:str, eframe:pd.DataFrame=None, igor=False):
        self.ax: Axes = ax
        self.metric = metric

        self.set_axis_labels()

        self.colors = Pallette(igor)

        # for performing a ttest
        self.peakamps = defaultdict(list)
        self.cntr = 0

        # funky x axis for this
        self.xticks = [-1, -0.75, -0.50, -0.25, 0.25, 0.50, 0.75, 1]
        self.pos = np.arange(8)
        self.xdict = dict(zip(self.xticks, self.pos))

        # for writing to csv
        self.labels = []
        self.lightmean = 0.0
        self.ymax = 0.0
        self.xvalues = []
        self.yvalues = []
        self.sems = []

        if eframe is not None:
            self.append_trace(eframe)

    def __str__(self):
        return f"{type(self).__name__}(lightmean={self.lightmean})"

    def append_trace(self, eframe: pd.DataFrame):
        self.cntr += 1
        X = []
        Y = []
        sems = []
        genotype = eframe.genotype.iloc[0]
        samplesize = 0

        for (lightamp, lightmean), frame in eframe.groupby(["lightamplitude", "lightmean"]):
            if lightmean != 0:
                contrast = lightamp / lightmean

                if contrast in self.xticks:
                    # GET PEAK AMPLITUDE FROM EACH PSTH - USED IN SEM
                    peakamps = np.array([
                        epoch.crf_value if self.metric == "peakamplitude" else epoch.timetopeak
                        for epoch in frame.epoch.values
                    ])

                    X.append(contrast)
                    Y.append(np.mean(peakamps))
                    sems.append(0.0 if len(peakamps) == 1 else sem(peakamps))

                    self.peakamps[genotype].append(peakamps)

                    samplesize = max(samplesize, np.max(peakamps))

        # SORT VALUES ALONG X AXIS
        if len(X) > 0:
            indexes = list(np.arange(len(X)))
            indexes.sort(key=X.__getitem__)
            X = np.array(X)
            Y = np.array(Y)
            sems = np.array(sems)
            X = X[indexes]
            Y = Y[indexes]
            sems = sems[indexes]

            # PLOT CRF EVENLY - IGNORE CONTRAST VALUES
            X_ = [self.xdict.get(x, 0.0) for x in X]
            #self.ax.errorbar(
                #X_, Y,
                #yerr=sems,
                #label=f"{genotype} (n = {len(peakamps)})",
                #color=self.colors[genotype])

            self.ax.plot(X_ ,Y,
                label=f"{genotype} (n = {len(peakamps)})",
                color=self.colors[genotype])
            self.ax.fill_between(X_, Y-sems, Y+sems, color=self.colors[genotype], alpha=0.25)

            self.labels.append(genotype)
            self.xvalues.append(X)
            self.yvalues.append(Y)
            self.sems.append(sems)

            # FORMAT X AXIS
            # TODO HOW TO REMOVE 0? 
            #self.ax.spines["bottom"].set_bounds(0, 7)
            self.ax.set_xticks(np.arange(8))
            self.ax.set_xticklabels([f"{x*100:.0f}" for x in self.xticks])

            # SET Y LIMITS
            ## MAX OR MIN BASED ON SIGN OF Y - ALWAYS WANT FROM 0 UP REGARDLESS OF SIGN
            bottom, top = self.ax.get_ylim()
            if top > 0:
                self.ax.set_ylim((top, bottom))
                locator = MaxNLocator(prune="both", nbins=4)
                self.ax.yaxis.set_major_locator(locator)
        
            if self.cntr == 2:
                self.t_test()



    def set_axis_labels(self):
        self.ax.set_xlabel("Percent Contrast")
        if self.metric.lower() == "timetopeak":
            self.ax.set_ylabel("Seconds")
            self.ax.set_title("Time to Peak Amplitude over Contrast")
        else:
            self.ax.set_ylabel("Response (pA)")
            self.ax.set_title("Contrast Response Curve")

    def t_test(self):
        g1, g2 = self.labels[:2]
        v1 = self.peakamps[g1]
        v2 = self.peakamps[g2]

        ylim = 0.0
        text = []
        for ii, (a1, a2) in enumerate(zip(v1, v2)):
            stat, p = ttest_ind(
                a1, a2)
            stars = p_to_star(p)

            if stars != "ns":

                # GETS POSITION TO WRITE STARS
                # ON TOP MOST ERROR BAR
                ymax = np.sign(np.mean(a1)) * max(
                    (np.abs(np.mean(a1)) + sem(a1)),
                    (np.abs(np.mean(a2)) + sem(a2)))

                ylim = max(ylim, ymax) if ymax > 0 else min(ylim, ymax)

                self.ax.text(
                    ii,  # ASSUME IN SAME ORDER
                    ymax*1.05,
                    stars,
                    ha='center',
                    va='bottom', color='k', rotation=90)

        bottom, top = self.ax.get_ylim()
        ntop = ylim * 1.08
        self.ax.set_ylim((bottom, ylim * 1.08))

    def to_csv(self):
        ...

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, outputdir: Path, *args, **kwargs):

        df = pd.DataFrame()
        for label, X, Y, sems in zip(self.labels, self.xvalues, self.yvalues, self.sems):
            df["X"] = X
            df[f"Y_{label}"] = Y
            df[f"SEM_{label}"] = sems

        df.to_csv(outputdir / f"PlotCRF{datetime.now()}.txt", sep="\t", index=False)



class PlotCRF(PlotBase):

    def __init__(self, ax: Axes, metric:str, eframe:pd.DataFrame=None, igor=False):
        self.ax: Axes = ax
        self.metric = metric

        self.set_axis_labels()

        self.colors = Pallette(igor)

        # for performing a ttest
        self.peakamps = defaultdict(list)
        self.cntr = 0

        # funky x axis for this
        self.xticks = [-1, -0.75, -0.50, -0.25, 0.25, 0.50, 0.75, 1]
        self.pos = np.arange(8)
        self.xdict = dict(zip(self.xticks, self.pos))

        # for writing to csv
        self.labels = []
        self.lightmean = 0.0
        self.ymax = 0.0
        self.xvalues = []
        self.yvalues = []
        self.sems = []

        if eframe is not None:
            self.append_trace(eframe)

    def __str__(self):
        return f"{type(self).__name__}(lightmean={self.lightmean})"

    def append_trace(self, eframe: pd.DataFrame):
        self.cntr += 1
        X = []
        Y = []
        sems = []
        genotype = eframe.genotype.iloc[0]

        for (lightamp, lightmean), frame in eframe.groupby(["lightamplitude", "lightmean"]):
            if lightmean != 0:
                contrast = lightamp / lightmean

                if contrast in self.xticks:
                    # GET PEAK AMPLITUDE FROM EACH PSTH - USED IN SEM
                    peakamps = np.array([
                        epoch.peakamplitude if self.metric == "peakamplitude" else epoch.timetopeak
                        for epoch in frame.epoch.values
                    ])

                    X.append(contrast)
                    Y.append(np.mean(peakamps))
                    sems.append(0.0 if len(peakamps) == 1 else sem(peakamps))

                    self.peakamps[genotype].append(peakamps)

        # SORT VALUES ALONG X AXIS
        if len(X) > 0:
            indexes = list(np.arange(len(X)))
            indexes.sort(key=X.__getitem__)
            X = np.array(X)
            Y = np.array(Y)
            sems = np.array(sems)
            X = X[indexes]
            Y = Y[indexes]

            # PLOT CRF EVENLY - IGNORE CONTRAST VALUES
            X_ = [self.xdict.get(x, 0.0) for x in X]
            #self.ax.errorbar(
            #    X_, Y,
            #    yerr=sems,
            #    label=f"{genotype} (n = {len(peakamps)})",
            #    color=self.colors[genotype])

            self.ax.plot(X_ ,Y,
                label=f"{genotype} (n = {len(peakamps)})",
                color=self.colors[genotype])
            self.ax.fill_between(X_, Y-sems, Y+sems, color=self.colors[genotype], alpha=0.25)


            self.labels.append(genotype)
            self.xvalues.append(X)
            self.yvalues.append(Y)
            self.sems.append(sems)

            # FORMAT X AXIS
            # TODO HOW TO REMOVE 0? 
            #self.ax.spines["bottom"].set_bounds(0, 7)
            self.ax.set_xticks(np.arange(8))
            self.ax.set_xticklabels([f"{x*100:.0f}%" for x in self.xticks])

            # SET Y LIMITS
            ## MAX OR MIN BASED ON SIGN OF Y - ALWAYS WANT FROM 0 UP REGARDLESS OF SIGN
            self.ymax = max(self.ymax, np.max(Y)) if np.max(Y) > 0.0 else min(self.ymax, np.min(Y))
            if self.ymax < 0:
                bottom, top = self.ax.get_ylim()
                self.ax.set_ylim((top, bottom))
                locator = MaxNLocator(prune="both", nbins=4)
                self.ax.yaxis.set_major_locator(locator)
        
            self.ax.legend()
            
            if self.cntr == 2:
                self.t_test()


    def set_axis_labels(self):
        self.ax.set_xlabel("Percent Contrast")
        if self.metric.lower() == "timetopeak":
            self.ax.set_ylabel("Seconds")
            self.ax.set_title("Time to Peak Amplitude over Contrast")
        else:
            self.ax.set_ylabel("Response (pA)")
            self.ax.set_title("Contrast Response Curve")

    def t_test(self):
        g1, g2 = self.labels[:2]
        v1 = self.peakamps[g1]
        v2 = self.peakamps[g2]

        ylim = 0.0
        for ii, (a1, a2) in enumerate(zip(v1, v2)):
            stat, p = ttest_ind(
                a1, a2)
            stars = p_to_star(p)

            if stars!="ns":
                # GETS POSITION TO WRITE STARS
                # ON TOP MOST ERROR BAR
                ymax = np.sign(np.mean(a1)) * max(
                    (np.abs(np.mean(a1)) + sem(a1)),
                    (np.abs(np.mean(a2)) + sem(a2)))

                ylim = max(ylim, ymax) if ymax > 0 else min(ylim, ymax)

                self.ax.text(
                    ii,  # ASSUME IN SAME ORDER
                    ymax*1.05,
                    stars,
                    ha='center',
                    va='bottom', color='k', rotation=90)

        self.ax.set_ylim((0, ylim * 1.08))

    def to_csv(self):
        ...

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, outputdir: Path, *args, **kwargs):

        df = pd.DataFrame()
        for label, X, Y, sems in zip(self.labels, self.xvalues, self.yvalues, self.sems):
            df["X"] = X
            df[f"Y_{label}"] = Y
            df[f"SEM_{label}"] = sems

        df.to_csv(outputdir / f"PlotCRF{datetime.now()}.txt", sep="\t", index=False)

class PlotCellWeber(PlotBase):

    def __init__(self, ax:Axes, eframe:pd.DataFrame=None, igor=False):
        self.ax = ax
        self.fits: Dict[str, Dict[str, WeberEquation]] = defaultdict(list)

        self.ax.set_yscale("log")
        self.ax.set_xscale("log")

        self.colors = Pallette(igor)

        self.lightmean = 0.0

        self.ax.set_title("Weber Adaptation")
        self.ax.set_ylabel("Gain (1/R*)")
        self.ax.set_xlabel("Background (R*/S-cone/sec)")

        if eframe is not None:
            self.append_trace(eframe)

    def __str__(self):
        return f"{type(self).__name__}(lightmean={self.lightmean})"

    def filestem(self):
        return f"PlotWeber_{'_'.join([x for x in self.fits])}"

    def append_trace(self, eframe: pd.DataFrame):
        """HILL FIT ON EACH CELL AND AVERAGE OF EACH CELLS"""
        genotype = eframe.genotype.iloc[0]
        self.lightmean = eframe.genotype.iloc[0]

        # GET 100 PCT CONTRAST VALUES
        minamp0 = eframe.loc[eframe.lightmean == 0.0]
        minamp0 = minamp0.lightamplitude.min()

        frame = eframe.loc[
            (eframe.lightmean == eframe.lightamplitude) |
            ((eframe.lightmean == 0.0) & (eframe.lightamplitude == minamp0))]
        frame = frame.loc[frame.lightamplitude > 0] # get rid of -10000

        frame = frame.sort_values(["lightmean", "lightamplitude"])

        frame["gain"] = frame.epoch.apply(lambda x: x.gain).values
        frame = frame.groupby(["lightmean", "lightamplitude"]).gain.mean().reset_index()
        X = frame.lightmean.values
        Y = frame.gain

        weber = WeberEquation()
        weber.fit(X, Y)

        self.fits[genotype].append(weber)

        # PLOT LINE AND AVERAGES
        topltX = np.arange(50000)

        # TODO decide on line labels
        self.ax.plot(topltX, weber(topltX), color=self.colors[genotype])
        self.ax.scatter(*weber.normalize(X, Y),
                        alpha=0.4, color=self.colors[genotype])

        self.ax.set_title(f"iHalf={weber.ihalf:.0f}, r2={weber.r2:.3f}")

        #self.fits[f"{genotype}mean"] = weber

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
            columns="Label Beta R2".split(),
            data=data
        )

        outputpath = outputdir / (self.filestem + "_Data.csv")
        df.to_csv(outputpath, index=False)

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...



class PlotHill(PlotBase):

    def __init__(self, ax, eframe: pd.DataFrame = None, igor=False):
        self.ax = ax
        self.fits = dict()

        self.colors = Pallette(igor)
        self.lightmean = 0.0

        if eframe is not None:
            self.append_trace(eframe)

    def __str__(self):
        return f"{type(self).__name__}(lightmean={self.lightmean})"

    def append_trace(self, eframe: pd.DataFrame):
        """HILL FIT ON EACH CELL AND AVERAGE OF EACH CELLS"""
        # EPOCH SEPARATED BY CELL, LIGHTAMPLITUDE. ASSUMING SAME LIGHT MEAN
        genotype = eframe.genotype.iloc[0]
        self.lightmean = eframe.lightmean.iloc[0]

        # TODO will this be done on epoch level?
        # FIT HILL TO EACH CELL - ONLY PLOT PEAK AMOPLITUDES
        for cellname, frame in eframe.groupby(["cellname"]):
            frame = frame.sort_values(["lightamplitude"])
            X = frame.lightamplitude.values
            Y = frame.epoch.apply(lambda x: x.peakamplitude).values

            Y = -1 * Y if max(Y) < 0 else Y

            hill = HillEquation()
            hill.fit(X, Y)
            self.fits[cellname] = hill

        # FIT HILL TO AVERAGE OF PEAK AMPLITUDES
        df = eframe.copy()
        df["peakamp"] = eframe.epoch.apply(lambda x: x.peakamplitude).values
        dff = df.groupby("lightamplitude").peakamp.mean().reset_index()

        # PLOT LINE AND AVERAGES
        X, Y = dff.lightamplitude.values, dff.peakamp.values
        Y = -1 * Y if max(Y) < 0 else Y
        hill = HillEquation()
        hill.fit(X, Y)
        X_ = np.linspace(0, np.max(X), 1000)
        self.ax.plot(X_, hill(X_), color=self.colors[genotype])
        self.ax.scatter(X, Y, alpha=0.4, color=self.colors[genotype])

        # TODO decide on label based on grouping
        self.fits[f"{genotype}_average"] = hill

    def to_csv(self):
        ...

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...


class PlotWeber(PlotBase):

    def __init__(self, ax:Axes, eframe:pd.DataFrame=None, igor=False):
        self.ax = ax
        self.fits: Dict[str, Dict[str, WeberEquation]] = defaultdict(dict)

        self.ax.set_yscale("log")
        self.ax.set_xscale("log")

        self.colors = Pallette(igor)

        self.lightmean = 0.0
        self.cntr = 0
        self.gains = dict()
        self.tY = defaultdict(list)

        self.ax.set_title("Weber Adaptation")
        self.ax.set_ylabel("Gain (1/R*)")
        self.ax.set_xlabel("Background (R*/S-cone/sec)")

        if eframe is not None:
            self.append_trace(eframe)

    def __str__(self):
        return f"{type(self).__name__}(lightmean={self.lightmean})"

    def filestem(self):
        return f"PlotWeber_{'_'.join([x for x in self.fits])}"

    def append_trace(self, eframe: pd.DataFrame):
        genotype = eframe.genotype.iloc[0]
        self.lightmean = eframe.genotype.iloc[0]
        self.cntr += 1

        # FIT HILL TO EACH CELL - ONLY PLOT PEAK AMPLITUDES
        for cellname, framef in eframe.groupby(["cellname"]):
            # GET 100 PCT CONTRAST VALUES
            minamp0 = framef.loc[framef.lightmean == 0.0]
            minamp0 = minamp0.lightamplitude.min()

            frame = framef.loc[
                (framef.lightmean == framef.lightamplitude) |
                ((framef.lightmean == 0.0) & (framef.lightamplitude == minamp0))]
            frame = frame.loc[frame.lightamplitude > 0] # get rid of -10000

            frame = frame.sort_values(["lightmean", "lightamplitude"])

            X = frame.lightmean.values
            Y = frame.epoch.apply(lambda x: x.gain).values

            weber = WeberEquation()
            weber.fit(X, Y)

            self.fits[genotype][cellname] = weber

        # GET VALUES FOR A TTEST
        minamp0 = eframe.loc[(eframe.lightmean == 0.0), "lightamplitude"].min()
        for (lmean, lamp), frame in eframe.groupby(["lightmean", "lightamplitude"]):
            if (lmean == lamp) or (lmean == 0.0 and lamp == minamp0):
                self.tY[genotype].append(np.mean(frame.epoch.apply(lambda x: x.gain).values))
                self.gains[lmean] = self.tY

        # FIT HILL TO AVERAGE OF PEAK AMPLITUDES
        df = eframe.copy()
        df["gain"] = eframe.epoch.apply(lambda x: x.gain)
        df = df.groupby(["lightamplitude", "lightmean"]).gain.mean().reset_index()

        # GET MIN AMPLITUDE FPOR LIGHT MEAN 0.0
        minamp0 = df.loc[df.lightmean == 0.0]
        minamp0 = minamp0.lightamplitude.min()

        # FILTER TO 0 WITH MIN AMP AND REST 100PCT CONTRAST
        frame = df.loc[
            (df.lightmean == df.lightamplitude) |
            ((df.lightmean == 0.0) & (df.lightamplitude == minamp0))]
        frame = frame.loc[frame.lightamplitude > 0] # get rid of -10000

        frame = frame.sort_values(["lightmean", "lightamplitude"])

        # FIT WEBER TO AVERAGE PEAK AMPLITUDES
        weber = WeberEquation()
        X = frame.lightmean.values
        Y = frame.gain.values
        weber.fit(X, Y)

        self.X = X

        # PLOT LINE AND AVERAGES
        topltX = np.arange(50000)

        # TODO decide on line labels
        self.ax.plot(topltX, weber(topltX), color=self.colors[genotype], label=f"{genotype}: r2={weber.r2}")
        self.ax.scatter(*weber.normalize(X, Y),color=self.colors[genotype])
                        #alpha=0.4

        logger.info(f"{genotype}: {weber.r2}")

        #if self.cntr > 1:
        #    self.ttest()

        #self.ax.legend()

        #self.fits[f"{genotype}mean"] = weber


    def ttest(self):

        self.ax.set_ylim(0, 3)
        for lightmean in self.gains:
            genos = list(self.gains[lightmean].values())

            toppoint = 1.5
            if len(genos) > 1:
                y1 = genos[0]
                y2 = genos[1]

                stat, p = ttest_ind(y1, y2)
                stars = p_to_star(p)

                stars = f"p={p:0.03f}" if stars == "ns" and p < 0.06 else stars

                self.ax.text(
                    x = lightmean,
                    y=toppoint,
                    s=stars,
                    ha='center',
                    va='bottom', color='k')

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
            columns="Label Beta R2".split(),
            data=data
        )

        outputpath = outputdir / (self.filestem + "_Data.csv")
        df.to_csv(outputpath, index=False)

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...

class PlotWeberCoeff:

    def __init__(self, coeffs: Dict, igor=False):
        self.coeffs = coeffs

        self.colors = Pallette(igor)

    def plot(self, ax):
        self.ax = ax
        Ys = []
        Ss = []
        Xs = []
        xlabels = []
        for ii, (genotype, fits) in enumerate(sorted(self.coeffs.items(), reverse=True)):
            Y = [
                fit.ihalf
                for cellname, fit in fits.items()
                if cellname != "20210818A2_Cell2"]
            Ys.append(np.mean(Y))
            Ss.append(Y)
            Xs.append(genotype)
            xlabels.append(genotype)

            semval = sem(Y)

            self.ax.bar(ii,
                height=np.mean(Y),
                yerr=semval,
                capsize=12,
                linewidth=2,
                edgecolor=self.colors[genotype],
                color = 'None',
                label=genotype,
                tick_label=genotype)

            # PLOT SCATTER
            self.ax.scatter(
                np.repeat(ii, len(Y)),
                Y,
                alpha=0.25,
                color=self.colors[genotype])

            # LABEL NUMBER OF CELLS
            self.ax.text(ii, 0, f"n={len(Y)}",
                            ha='center', va='bottom', color='k')

        # TTEST
        stat, p = ttest_ind(
            Ss[0], Ss[1])

        stars = p_to_star(p)
        #stars = f"p={p:0.03f}" if stars == "ns" and p < 0.06 else stars
        # PLOT SIGNFICANCE LABEL
        # HACK PERCENT TO PUT ABOVE MAX POINT. DOESN'T WORK WELL FOR SMALL VALUES
        _, toppoint = ax.get_ylim()
        toppoint = max(np.max(Ss[0]), np.max(Ss[1]))
        pct = 0.05
        ay, h, col = toppoint + toppoint * pct, toppoint * pct, 'k'

        ax.plot(
            [0,0,1,1],
            [ay, ay+h, ay+h, ay],
            lw=1.5, color=col)

        ax.text(
            0.5,
            ay+h,
            stars,
            ha='center',
            va='bottom')

        self.ax.set_xticks([0,1])
        self.ax.tick_params(axis='x', which='both', length=0)
        self.ax.set_xticklabels(xlabels)

class PlotContrastResponses(PlotBase):
    cmap = plt.get_cmap("tab10")

    def __init__(self, ax:Axes, eframe:pd.DataFrame, igor=False):
        self.ax = ax
        self.ax.grid(False)

        # IF SUMMARIZING CELL NEED A DIFFERENT COLOR FOR EACH CELL, NOT GENOTYPE
        self.colors = Pallette(igor)

        # LISTS USED IN EXPORTING DATA
        self.labels = []
        self.values = []

        if eframe is not None:
            self.append_trace(eframe)

    def __str__(self):
        return f"{type(self).__name__}({','.join(map(str,self.labels))})"

    def append_trace(self, eframe:pd.DataFrame):
        """eframe has single lightmean
        """
        # GET AVERAFE TRACE ACROSS CELLS
        for lightamplitude, frame in eframe.groupby("lightamplitude"):
            Ys = np.fromiter([
                epoch.trace
                for epoch in frame.epoch], dtype=float)
            Y = np.mean(Ys, axis=1)
            stimtime = frame.epoch.iloc[0].stimtime
            lightmean = frame.lightmean.iloc[0]
            label = lightamplitude / lightmean

            X = np.arange(len(Y)) - stimtime

            self.ax.plot(
                X,
                Y, label=lightamplitude / lightmean,
                color="black",
                alpha=0.4)

        # APPEND VALUES NEEDED FOR WRITING OUT
        self.labels.append(label)
        self.values.append(Y)

        # ADD X TICKS
        xticks = [min(X)] + list(np.arange(0, max(X), 5000))
        xlabels = [f"{x/10000:0.1f}" for x in xticks]

        self.ax.xaxis.set_ticks(xticks)
        self.ax.xaxis.set_ticklabels(xlabels)



    def to_csv(self, *args, **kwargs):
        ...

    def to_image(self, *args, **kwargs):
        ...

    def to_igor(self, *args, **kwargs):
        ...

