import sys
sys.path.append("..")
from dissonance import io, init_log

from pathlib import Path
from dissonance.io import DissonanceUpdater, SymphonyReader, read_rstarr_table

from .constants import MAPPED_DIR, ROOT_DIR, RAW_DIR

logger = init_log()


class TestAddInfo:

    def setUp(self):
        self.raw_dir = RAW_DIR
        self.map_dir = MAPPED_DIR
        self.rstarrdf = read_rstarr_table()
        #self.folders = ["WT", "DR"]
        ##self.folders = ["GG2 control", "GG2 KO"]
        self.folders = ["GA1 control", "GA1 KO"]

        self.folders = [#"WT", "DR",
            "GG2 control", "GG2 KO",
            "GA1 control", "GA1 KO"]

    def test_update_rstarr_file(self):
        self.setUp()
        geno = "GG2 control"
        filename = '2021-10-21A.h5'

        rdr = SymphonyReader((self.raw_dir / geno) / filename, self.rstarrdf)
        rdr.update_rstarr((self.map_dir / geno) / filename)

    def test_update_params_files(self):
        self.setUp()
        for rawfile, mapfile in self.zip_directories(self.raw_dir, self.map_dir):
            rdr = SymphonyReader(rawfile, self.rstarrdf)
            rdr.update_metadata(mapfile, attrs=True)

    def test_update_rstarr_files(self):
        self.setUp()
        for rawfile, mapfile in self.zip_directories(self.raw_dir, self.map_dir):
            try:
                rdr = SymphonyReader(rawfile, self.rstarrdf)
                rdr.update_rstarr(mapfile)
            except Exception as e:
                logger.info(e)

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

    def test_add_genotype_file(self):
        #geno = "GG2 KO"
        #genodir = MAPPED_DIR / geno
        #filename = "2022-06-03B.h5"

        genodir = MAPPED_DIR / "GG2 control"
        geno = "GG2 control"
        filename = "2022-06-02B.h5"

        up = DissonanceUpdater(genodir / filename)
        up.add_genotype(geno)


    def test_update_cell_labels(self):
        """Combine cellname and experiment date to make unique code"""

        self.setUp()

        for flder in self.folders:
            wdir = self.map_dir / flder

            for file in wdir.glob("*.h5"):
                up = DissonanceUpdater(file)
                up.update_cell_labels()