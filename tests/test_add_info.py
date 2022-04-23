import sys 
sys.path.append("..")
from dissonance import io
from multiprocessing import Pool

from pathlib import Path
from dissonance.io import add_genotype

def test_add_genotypes():
	root_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
	for flder in ["WT", "DR"]:
		wdir = root_dir / flder
		for file in wdir.glob("*.h5"):
			print(file)
			add_genotype(file, flder)
