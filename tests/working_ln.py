import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from pathlib import Path
from scipy import fft
import pandas as pd
from dissonance import viewer, io, epochtypes, analysis
from dissonance.epochtypes import filter
from time import time
import pytest

#%load_ext autoreload
#%autoreload 2

ROOT_DIR = Path("/home/joe/Projects/DataStore/MappedData")

#uncheckedpath = Path("DemoForJenna.txt")
#unchecked = io.read_unchecked_file(uncheckedpath)
unchecked = None
uncheckedpath = None

folders = ["DR", "WT"]
#folders = ["GG2 control", "GG2 KO"]
paths = [] 
for fldr in folders:
    paths.extend(
        [	file
            for ii, file in enumerate((ROOT_DIR/fldr).glob("*.h5"))
        ]
    )

dr = io.DissonanceReader(paths)
paramnames = ["led", "protocolname", "celltype", "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
params = dr.to_params(paramnames)
#params = params.loc[params.protocolname.isin(["LedNoiseFamily"])]
params = params.loc[params.protocolname == "LedNoiseFamily"]

epochio = io.EpochIO(params, paths)
lsa = analysis.LedSpikeAnalysis()

eframe = epochio.query(filters=[{"protocolname":"LedNoiseFamily"}])

epoch = eframe.epoch.iloc[0]



epoch.stimuli
std = epoch.stimuli["stdev"]
mean = epoch.stimuli["mean"]
seed = epoch.stimuli["seed"]
samplerate = epoch.stimuli["samplerate"]
stimtime = epoch.stimuli["stimtime"]
freqcutoff = epoch.stimuli["freqcutoff"]
numfilters = epoch.stimuli["numfilters"]

noiseTime = np.random.randn(len(epoch)) * std

noiseFreq  = fft.fft(noiseTime)


freqStep = samplerate / stimtime

if stimtime % 2 ==0:
    frequences = np.arange(stimtime // 2) * freqStep
    onesidedFilter = 1 / (1 + (frequences / freqcutoff) ** (2 * numfilters))
    filter = np.array([*onesidedFilter, *onesidedFilter[1:-1:-1]])
else:
    frequences = np.arange((stimtime-1) // 2) * freqStep




stim = np.clip(stim, epoch.stimuli["lowerlimit"], epoch.stimuli["upperlimit"])

df = pd.DataFrame(columns=["Value"],data=stim)
px.line(df, y="Value")

