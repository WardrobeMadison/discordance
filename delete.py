import sys 
sys.path.append("..")
from dissonance import io
from multiprocessing import Pool
import h5py

from pathlib import Path
from dissonance.io import add_genotype, add_attributes

def test_add_genotypes():
	root_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
	for flder in ["WT", "DR"]:
		wdir = root_dir / flder
		for file in wdir.glob("*.h5"):
			print(file)
			add_genotype(file, flder)


import re
re_date = re.compile(r"^.*(\d{4}-\d{2}-\d{2})(\w\d?).*$")

file = "/home/joe/Projects/DataStore/MappedData/WT/2021-07-28A.h5"
f = h5py.File(str(file), "a")
experiment = f["experiment"]
matches = re_date.match(str(file))

suffix = matches[1].replace("-", "") + matches[2]
for epochgrp in experiment:
    epoch = f[f"experiment/{epochgrp}"]
    epoch.attrs["cellname"] = f'{epoch.attrs["cellname"].split("_")[0]}_{suffix}'

