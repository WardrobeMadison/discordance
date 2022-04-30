# %%
from pathlib import Path

from numpy import isin
from dissonance.trees import Tree
from dissonance import epochtypes, io, analysis
from dissonance.epochtypes import groupby
import pandas as pd
import h5py


%load_ext autoreload
%autoreload 2


# %%
ROOTDIR = Path("/home/joe/Projects/DataStore/MappedData")

def load_epochs(folders, paramnames, filters, uncheckedpath = None, nfiles = 5):
    if uncheckedpath is None:
        unchecked = None
    else:
        unchecked = io.read_unchecked_file(uncheckedpath)

    paths = []
    for fldr in folders:
        paths.extend(
            [	file
                for ii, file in enumerate((root_dir/fldr).glob("*.h5"))
                if ii < nfiles
            ]
        )

    dr = io.DissonanceReader(paths)
    df = dr.to_params(paramnames=paramnames, filters = filters, nprocesses=10)
    return df, paths

paramnames = (
    "protocolname",
    "led",
    "celltype",
    "genotype",
    "cellname",
    "lightamplitude",
    "lightmean",   
    "startdate")

root_dir = ROOTDIR
filters = {"tracetype":"wholetrace"}
params, paths = load_epochs(["DR","WT"],paramnames, filters, nfiles=50)

# %%
#*******************************************************************************
labels = [
    "protocolname",
    "led",
    "celltype",
    "genotype",
    "cellname",
    "lightamplitude",
    "lightmean",   
    "startdate"]

#keys = df[labels].values

#tree = Tree("Test", labels, keys)

sis = analysis.LedWholeAnalysis(params, paths)

# %%

print(sis.visual)
