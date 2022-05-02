import re
import shutil
from functools import partial
from multiprocessing import Pool
from pathlib import Path
from time import time

import h5py
import pandas as pd
import pytest

import dissonance as dn
from dissonance import analysis, epochtypes, io, viewer
from dissonance.epochtypes import filter

src_dir=Path("/Users/jnagy2/Documents/MATLAB/Packages/sa-working-directory/analysis/rawFiles")
wdir = Path("/Users/jnagy2/Documents/DATA/DissonanceData/RawData")

# COPY FILES TO RAW DATA DIRECTORY
ko = [
"2021-05-06A",
"2021-05-07A",
"2021-06-07A",
"2021-08-18A2",
"2021-11-18A",
"2021-11-23A",
"2022-03-11A"]

gg2 = [
"2021-05-25A",
"2021-08-24A",
"2021-09-21A",
"2021-10-19A",
"2021-10-21A",
"2021-10-26A",
"2021-10-27A",
"2021-11-01A",
"2021-11-17A",
"2021-11-20A",
"2022-02-03A"]

DR = [
"2021-07-06A",
"2021-07-12A",
"2021-07-13A",
"2021-08-02A",
"2021-08-04A",
"2021-08-19A2",
"2021-08-25A2",
"2021-09-23A2",
"2021-09-24A",
"2021-12-05A",
"2021-12-07A",
"2021-12-08A",
"2022-01-03A",
"2022-01-04A",
"2022-01-05A",
"2022-01-06A",
"2022-02-08A",
"2022-02-14A",
"2022-02-21A",
"2022-02-28A",
]

WT = [
"2021-06-23A",
"2021-06-29A",
"2021-06-30A",
"2021-07-05A",
"2021-07-18A",
"2021-07-20A",
"2021-07-20A1",
"2021-07-20A2",
"2021-07-28A",
"2021-08-07A_WT_DR_Ctrl",
"2021-09-07A2",
"2021-09-11A",
"2021-09-12A",
"2021-09-23A",
"2021-10-05A",
"2021-10-19A",
"2021-12-27A",
"2021-12-28A",
"2021-12-29A",
"2021-12-30A",
"2022-02-10A",
"2022-02-15A",
"2022-02-28A2"]

def copyfiles(root_dir, wdir, filestems):
    for filestem in filestems:
        src = root_dir / f"{filestem}.h5"
        dst = wdir

        print(f"Copying {src} to {dst}")
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst /  f"{filestem}.h5")

def write_file(file, wodir):
    try:
        print(file)
        sr = dn.io.SymphonyReader(file)
        sr.to_h5(wodir / file.name)
    except Exception as e:
        print(f"FAILED {file}")
        raise e

    return f"Done reading {file}"
# MAP FILES TO DISSONANCE FORMAT
def map_files(root_dir, out_dir, folders):

    for folder in folders:
        wdir = root_dir / folder

        wodir = (out_dir / folder)
        wodir.mkdir(parents=True, exist_ok=True)

        files = [file for file in wdir.glob("*.h5") if file.name]
        func = partial(write_file, wodir = wodir)

        with Pool(4) as p:
            for x in p.map(func, files):
                print(x)

# UPDATE CELL NAMES
def update_cells(root_dir, folders):
    for flder in folders:
        wdir = root_dir / flder

        for file in wdir.glob("*.h5"):
            up = dn.io.DissonanceUpdater(file)
            up.update_cell_labels()

def add_genotype(file, genotype): 
    up = dn.io.DissonanceUpdater(file)
    up.add_genotype(genotype)

def add_genotypes(root_dir, genotypes):
    for flder in genotypes:
        wdir = root_dir / flder
        files = [file for file in wdir.glob("*.h5")]
        func = partial(add_genotype, genotype = flder)
        with Pool(4) as p:
            for x in p.map(func, files):
                print(x)

def zip_directories(rawdir:Path, mapdir:Path):
    filepaths = []
    rawfiles = [file for file in (rawdir).glob("*.h5")]
    rawstems = list(map(lambda x: x.stem, rawfiles))
    for file in (mapdir).glob("*.h5"):
        if file.stem in rawstems:
            filepaths.append(
                [
                    rawdir / file.name,
                    mapdir / file.name
                ]
            )

    return filepaths

def _update_params(rawfile, mapfile):
    rdr = dn.io.SymphonyReader(rawfile)
    rdr.update_metadata(mapfile, attrs=True)

def rerun_params(root_dir, map_dir, genotypes):
    for genotype in genotypes:
        filetuples =  zip_directories(root_dir/genotype, map_dir/genotype)
        with Pool(4) as p:
            for x in p.starmap(_update_params, filetuples):
                print(x)

def gui_whole():
    try:
        root_dir = Path("/Users/jnagy2/Projects/Dissonance/Data/MappedData")
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
                    for ii, file in enumerate((root_dir/fldr).glob("*.h5"))
                ]
            )

        dr = io.DissonanceReader(paths)
        paramnames = ["led", "holdingpotential", "protocolname", "celltype", "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
        params = dr.to_params(paramnames, filters={"tracetype" : "wholetrace"})
        params = params.loc[params.protocolname.isin(["LedPulseFamily", "LedPulse"])]

        epochio = analysis.EpochIO(params, paths)
        wa = analysis.LedWholeAnalysis()
        
        viewer.run(epochio, wa, unchecked, uncheckedpath)
    except SystemExit as e:
        ...
    finally:
        assert True

def gui_spike():
    try:
        root_dir = Path("/Users/jnagy2/Projects/Dissonance/Data/MappedData")
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
                    for ii, file in enumerate((root_dir/fldr).glob("*.h5"))
                ]
            )

        dr = io.DissonanceReader(paths)
        paramnames = ["led", "protocolname", "celltype", "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
        params = dr.to_params(paramnames, filters={"tracetype" : "spiketrace"})
        params = params.loc[params.protocolname.isin(["LedPulseFamily", "LedPulse"])]

        epochio = analysis.EpochIO(params, paths)
        lsa = analysis.LedSpikeAnalysis()
        
        viewer.run(epochio, lsa, unchecked, uncheckedpath)
    except SystemExit as e:
        ...
    finally:
        assert True

def gui_browse():
    try:
        root_dir = Path("/Users/jnagy2/Projects/Dissonance/Data/MappedData")
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
                    for ii, file in enumerate((root_dir/fldr).glob("*.h5"))
                ]
            )

        dr = io.DissonanceReader(paths)
        paramnames = ["led", "protocolname", "celltype", "genotype", "cellname", "lightamplitude", "lightmean", "startdate"]
        params = dr.to_params(paramnames)

        epochio = analysis.EpochIO(params, paths)
        lsa = analysis.BrowsingAnalysis()
        
        viewer.run(epochio, lsa, unchecked, uncheckedpath)
    except SystemExit as e:
        ...
    finally:
        assert True
# MAIN******************************************************************************
src_dir = Path("/Users/jnagy2/Documents/MATLAB/Packages/sa-working-directory/analysis/rawFiles")
raw_dir = Path("/Users/jnagy2/Projects/Dissonance/Data/RawData")
map_dir = Path("/Users/jnagy2/Projects/Dissonance/Data/MappedData")

if __name__ == "__main__":
    #copyfiles(src_dir, raw_dir / "WT", WT)
    #copyfiles(src_dir, raw_dir / "DR", DR)

    #map_files(raw_dir, map_dir, ["DR", "WT"])

    #add_genotypes(map_dir, ["DR", "WT"])

    #rerun_params(raw_dir, map_dir, ["WT", "DR"])
    #add_genotypes(map_dir, ["DR", "WT"])

    #gui_spike()
    #gui_whole()
    gui_browse()
    ...