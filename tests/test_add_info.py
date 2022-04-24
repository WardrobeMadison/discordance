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



def test_update_cell_labels():
	root_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
	for flder in ["WT", "DR"]:
		wdir = root_dir / flder
		for file in wdir.glob("*.h5"):
			f = h5py.File(str(file), "a")
			experiment = f["experiment"]
			for epoch in experiment:
				...
				#epoch.attrs["cellname"] = f'{file.stem}{epoch.attrs["cellname"]}'
