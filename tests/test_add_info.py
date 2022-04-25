import sys 
sys.path.append("..")
from dissonance import io
from multiprocessing import Pool
import h5py
import re

from pathlib import Path
from dissonance.io import add_genotype, add_attributes

def test_add_genotypes():
    root_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
    folders = ["GA1 KO", "GG2 control", "GG2 KO"]
    for flder in folders:
        wdir = root_dir / flder
        for file in wdir.glob("*.h5"):
            print(file)
            add_genotype(file, flder)



def test_update_cell_labels():
    re_date = re.compile(r"^.*(\d{4}-\d{2}-\d{2})(\w\d?).*$")
    root_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
    folders = ["GA1 KO", "GG2 control", "GG2 KO"]

    for flder in folders:
        wdir = root_dir / flder

        for file in wdir.glob("*.h5"):
            f = h5py.File(str(file), "a")
            experiment = f["experiment"]
            matches = re_date.match(str(file))

            suffix = matches[1].replace("-", "") + matches[2]
            for epochgrp in experiment:
                epoch = f[f"experiment/{epochgrp}"]
                epoch.attrs["cellname"] = f'{epoch.attrs["cellname"].split("_")[0]}_{suffix}'

