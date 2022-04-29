from multiprocessing import Pool
from pathlib import Path
from dissonance import viewer, io, epochtypes
from functools import partial
import unittest


class TestIO(unittest.TestCase):

    def test_to_h5(self):
        nprocesses = 5
        exclude = []
        folders = ["DR", "WT"]
        #folders = ["GA1 KO", "GG2 control", "GG2 KO"]
        #folders = ["GG2 KO", "GG2 control"]

        root_dir = Path(r"/home/joe/Projects/DataStore/EPhysData")
        out_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
        for folder in folders:
            wdir = root_dir / folder

            wodir = (out_dir / folder)
            wodir.mkdir(parents=True, exist_ok=True)

            files = [file for file in wdir.glob("*.h5") if file.name not in exclude]
            func = partial(self.write_file, wodir = wodir)

            with Pool(nprocesses) as p:
                for x in p.imap(func, files):
                    print(x)

    @staticmethod
    def write_file(file, wodir):
        try:
            print(file)
            sr = io.SymphonyReader(file)
            sr.to_h5(wodir / file.name)
        except Exception as e:
            print(f"FAILED {file}")
            raise e

        return f"Done reading {file}"
