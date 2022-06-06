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

plt.style.use("presentation.mplstyle")
#plt.style.use("tests/presentation.mplstyle")

# %%
def p_to_star(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "ns"

from io import StringIO
data = """CellName	Genotype	Time to Peak	Decay Time	Response Range	Linear Slope
2021-10-19ACell1	Control	0.0471	1.60089	942.937193	0.837894
2021-10-21ACell7	Control	0.0509	1.490815	1205.566666	0.870844
2021-10-26ACell9	Control	0.0499	1.741428	881.430921	0.92208
2021-11-01ACell1	Control	0.0517	1.437773	987.249276	1.170882
2021-10-21ACell5	Control	0.0494	1.621407	1258.079272	0.956253
2022-02-03ACell4	Control	0.0573	1.501899	255.531376	0.278238
2022-05-04BCell6	Control	0.0474	1.737961	409.653664	0.695451
2021-06-07ACell1	KO	0.0474	1.431517	1504.61878	1.159883
2021-06-07ACell2	KO	0.0532	1.507578	1569.202141	1.197818
2021-06-07ACell3	KO	0.0483	1.455635	1767.78771	1.627667
2021-08-18A2Cell2	KO	0.0492	1.554598	1154.50385	1.6239
2021-11-18ACell6	KO	0.0551	1.462743	1305.802931	1.826156"""
def swarm(metric):
    fig, ax = plt.subplots(figsize=(4,6))
    fig.patch.set_facecolor('xkcd:white')
    width = 0.25
    xlabels = []
    colors = {
        "Control":  "#6a9a23",
        "KO": "#441488"}



    for ii, (geno, frame) in enumerate(df.groupby("Genotype")):
        Y = frame[metric].mean()
        semval = sem(frame[metric].values)
        xlabels.append(geno)

        ax.bar(
            ii+1,
            Y, 
            yerr=semval,
            linewidth = 2,
            align="center",
            label=geno,
            capsize=5,
            edgecolor=colors[geno],
            color = 'None'
        )
        # PLOT SCATTER
        ax.scatter(
            np.repeat(ii+1, frame.shape[0]),
            frame[metric].values,
            alpha=0.15,
            color=colors[geno])

        ax.text(ii+1, 0.00, f"n={frame.shape[0]}", fontdict=dict(size=16), ha='center', va="bottom")

    # TTEST
    stat, p = ttest_ind(
        df.loc[df.Genotype=="Control", metric].values, 
        df.loc[df.Genotype=="KO", metric].values)


    stars = p_to_star(p)

    print(metric, stat, p, stars)
    _, toppoint = ax.get_ylim()
    toppoint = df[metric].max()
    pct = 0.05
    ay, h, col = toppoint + toppoint * pct, toppoint * pct, 'k'
#
    ax.plot(
        [1, 1, 2, 2],
        [ay, ay+h, ay+h, ay],
        lw=1.5, color=col)

    ax.text(
        1.5,
        ay+h,
        stars,
        ha='center', 
        va='bottom')

    # FIGURE ATTRIBUTES
    ax.set_xticks(np.arange(len(xlabels))+1)
    ax.set_xticklabels(xlabels)
    ax.tick_params(axis=u'x', which=u'both',length=0)
    ax.set_title(metric, pad=20)
    #custom_lines = [Line2D([0], [0], color=colors["KO"], lw=4),
                    #Line2D([0], [0], color=colors["Control"], lw=4)]

    #ax.legend(custom_lines, ["GG2 KO", "GG2 control"])
    #ax.tick_params(axis='x', which='both',length=0)

    # YAXIS LABELS
    if metric == "Decay Time":
        ax.set_ylabel("Time (s)")
    elif metric == "Linear Slope":
        ax.set_ylabel("Slope")
    elif metric == "Response Range":
        ax.set_ylabel("Range (nA)")
    elif metric == "Time to Peak":
        ax.set_ylabel("Time (s)")

    plt.savefig(f"LN_{metric}.png", dpi = 600)


# %%
df = pd.read_csv(StringIO(data), "\t")

for metric in df.columns[2:]:
    swarm(metric)


# %%
