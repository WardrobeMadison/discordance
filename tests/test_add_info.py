import sys
import pytest
sys.path.append("..")
import logging
from dissonance import io
from multiprocessing import Pool
import h5py
import re

from pathlib import Path
from dissonance.io import DissonanceUpdater, DissonanceReader, SymphonyReader

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter=logging.Formatter('%(asctime)s : %(message)s : %(levelname)s -%(name)s',datefmt='%d%m%Y %I:%M:%S %p')
fh = logging.FileHandler("log.txt")
fh.setFormatter(formatter)
logger.addHandler(fh)

class TestAddInfo:

    def setUp(self):
        self.raw_dir = Path(r"/home/joe/Projects/DataStore/EPhysData")
        self.map_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
        self.folders = ["WT", "DR"]
        #folders = ["GG2 control", "GG2 KO"]

    def test_update_rstarr_file(self):
        root_dir = Path(r"/home/joe/Projects/DataStore/EPhysData")
        out_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
        geno = "WT"
        filename = '2021-09-11A.h5'

        rdr = SymphonyReader((root_dir / geno) / filename)
        rdr.update_rstarr((out_dir / geno) / filename)

    def test_update_params_files(self):

        for rawfile, mapfile in self.zip_directories(self.raw_dir, self.map_dir):
            rdr = SymphonyReader(rawfile)
            rdr.update_metadata(mapfile, attrs=True)

    def test_update_rstarr_files(self):

        self.setUp()
        for rawfile, mapfile in self.zip_directories(self.raw_dir, self.map_dir):
            rdr = SymphonyReader(rawfile)
            rdr.update_rstarr(mapfile)

    def zip_directories(self, rawdir:Path, mapdir:Path):
        filepaths = []

        for flder in self.folders:
            rawfiles = [file for file in (rawdir/flder).glob("*.h5")]
            rawstems = list(map(lambda x: x.stem, rawfiles))
            for file in (mapdir / flder).glob("*.h5"):
                if file.stem in rawstems:
                    filepaths.append(
                        [
                            (rawdir / flder) / file.name,
                            (mapdir / flder) / file.name
                        ]
                    )

        return filepaths

    def test_add_genotype_files(self):
        """Add genotypes from folder name"""

        self.setUp()

        for flder in self.folders:
            wdir = self.map_dir / flder
            for file in wdir.glob("*.h5"):
                up = DissonanceUpdater(file)
                up.add_genotype(flder)

    def test_update_cell_labels(self):
        """Combine cellname and experiment date to make unique code"""

        for flder in self.folders:
            wdir = self.map_dir / flder

            for file in wdir.glob("*.h5"):
                up = DissonanceUpdater(file)
                up.update_cell_labels()