import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import ttest_ind
from datetime import datetime

def p_to_star(p):
	if p < 0.001:
		return "***"
	elif p <0.01:
		return "**"
	elif p < 0.05:
		return "*"
	else:
		return "ns"

COLORS = dict(
WT="#533E85",
DR="#488FB1"
#4FD3C4
#C1F8CF
)


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
        except:
            name = epochs.genotype

        # CALCULATE TTP AND MAX PEAK
        seconds_conversion = 10000 / 100
        ttp = (np.argmax(psth) + 1) / (seconds_conversion)
        x = (np.arange(len(psth)) + 1) / (seconds_conversion)
        self.ax.axvline(ttp, linestyle='--', color='k', alpha=0.4)

        self.ax.plot(x, psth, label=f"{label} (n={n})", c=COLORS[name])

        # UPDATE LEGEND WITH EACH APPEND
        self.ax.legend()

        # SAVE DATA FOR STORING LATER
        self.labels.append(label)
        self.psths.append(psth)

    def to_csv(self, filepath=None):
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
        if filepath is None:
            filepath = f"PlotPsth_{datetime.now()}.csv"
            
        df.to_csv(filepath, index=False)

class PlotRaster:

    def __init__(self, ax, epochs=None):
        self.ax = ax
        self.ax.grid(False)

        ax.set_ylabel("Hz / s")
        ax.set_xlabel("10ms bins")
        self.ax.axes.get_xaxis().set_visible(False)

        if epochs is not None:
            self.append_trace(epochs)

    def append_trace(self, epochs):
        """Raster plots

        Args:
            epochs (Traces): Epoch traces to plot.
            ax (Axes, optional): Axis obj from parent figure, creates figure if not provided. Defaults to None.
        """
        if self.ax is None: fig, ax, = plt.subplots()

        toplt = []
        for ii, epoch in enumerate(epochs):
            spikes = epoch.spikes.sp / 10000
            y = [ii+1] * len(spikes)
            toplt.append((spikes, y))

        for x,y in toplt:
            self.ax.scatter(x,y, marker="|", c="k")

        title = f"cellname={epochs.cellnames[0]}, lightamp={epochs.lightamplitudes[0]}, lightmean={epochs.lightmeans[0]}"
        
        # SET THESE EACH LOOP?
        self.ax.title.set_text(title)	
        self.ax.set_yticks(np.arange(len(epochs))+1)
        self.ax.set_yticklabels([f"{epoch.number}" for epoch in epochs])

class PlotTrace:

    def __init__(self, ax, epoch=None):
        self.ax = ax

        ax.set_ylabel("pA")
        ax.set_xlabel("10e-4 seconds")

        if epoch is not None:
            self.append_trace(epoch)

    def append_trace(self, epoch):
        """Plot traces

        Args:
            epoch (SpikeTraces): Epochs to trace
            ax ([type]): Matlab figure axis
        """
        self.ax.plot(epoch.values, label=epoch.startdate)

        # PLOT SPIKES IF YOU HAVE THEM
        if (
            epoch.type == "spiketrace"
            and epoch.spikes.sp is not None):
                y = epoch.values[epoch.spikes.sp]
                self.ax.scatter(epoch.spikes.sp, y, marker="x", c="#FFA500")

        self.ax.legend()

 
class PlotSwarm:

    def __init__(self, ax, metric:str="peakamplitude", epochs=None):
        self.ax = ax
        self.metric = metric

        if epochs is not None:
            self.append_trace(epochs)

        self.ax.grid(False)

    def append_trace(self, epochs: pd.DataFrame) -> None:
        """Swarm plot :: bar graph of means with SEM and scatter. Show signficance

        Args:
            epochs (Dict[str,SpikeTraces]): Maps genos name to traces to plot.
            ax (Axes, optional): Axis obj from parent figure, creates figure if not provided. Defaults to None.
        """
        if self.ax is None: fig, ax, = plt.subplots()

        # FOR EACH GENOTYPE
        # FOR EACH CELL IN CELLS (each epoch stored as indiviudal cell)
        toplt = []
        ymax = 0.0
        toppoint = 0.0 # NEED AXIS TO BE % ABOVE SEM BAR
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
            ymax = max(ymax, np.max(values)) if meanval > 0 else min(ymax, np.max(values))
            toppoint = max(toppoint, meanval+sem) if meanval > 0 else min(toppoint, meanval-sem)

            toplt.append(
                dict(
                    color = COLORS[name],
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
                alpha = 0.25,
                c=COLORS[name])
            
            # LABEL NUMBER OF CELLS 
            self.ax.text(ii, 0, f"n={len(values)}",
                ha='center', va='bottom', color='k')

        # CALCULATE SIGNIFICANCE
        if len(toplt) > 1:
            stat, p = ttest_ind(
                toplt[0]["values"], toplt[1]["values"])

            stars = p_to_star(p)
            stars = f"p={p:0.03f}" if stars == "ns" and p < 0.06 else stars
            x1, x2 = 0, 1 # ASSUME ONLY 2

            # PLOT SIGNFICANCE LABEL
            # HACK PERCENT TO PUT ABOVE MAX POINT. DOESN'T WORK WELL FOR SMALL VALUES
            pct = 0.05 
            ay, h, col = ymax + ymax * pct, ymax * pct, 'k'

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
        lamp, lmean = epochs.lightamplitude.iloc[0], epochs.lightmean.iloc[0]
        self.ax.set_title(f"{self.metric}: {lamp}, {lmean}")

        # X AXIS FORMAT
        self.ax.xaxis.set_ticks_position('none') 
        self.ax.set_xticks(np.arange(len(toplt)), dtype=float)
        self.ax.set_xticklabels([x["label"] for x in toplt])
        self.ax.set_xlabel("Background (R*/S-Cone/sec)")

        # Y AXIS FORMAT
        self.ax.set_ylabel("pA")
        self.ax.set_ylim((0.0, toppoint * 1.20))

