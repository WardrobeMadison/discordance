import sys
sys.path.append("..")
from dissonance import io, init_log

from pathlib import Path
from dissonance.io import DissonanceUpdater, SymphonyReader

from .constants import MAPPED_DIR, ROOT_DIR, RAW_DIR

init_log()

class TestAddInfo:

    def setUp(self):
        self.raw_dir = RAW_DIR
        self.map_dir = MAPPED_DIR
        #self.folders = ["WT", "DR"]
        self.folders = ["GG2 control", "GG2 KO"]

    def test_update_rstarr_file(self):
        root_dir = Path(r"/home/joe/Projects/DataStore/RawData")
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

        self.setUp()

        for flder in self.folders:
            wdir = self.map_dir / flder

            for file in wdir.glob("*.h5"):
                up = DissonanceUpdater(file)
                up.update_cell_labels()