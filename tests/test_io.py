import pytest
from functools import partial
import logging
from multiprocessing import Pool
from pathlib import Path

from dissonance import epochtypes, io, viewer

import sys
sys.stdout = open("delete.txt", "w+")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter=logging.Formatter('%(asctime)s : %(message)s : %(levelname)s -%(name)s',datefmt='%d%m%Y %I:%M:%S %p')
fh = logging.FileHandler("log.txt")
fh.setFormatter(formatter)
logger.addHandler(fh)


def write_file(file, wodir):
    try:
        print(file)
        sr = io.SymphonyReader(file)
        sr.to_h5(wodir / file.name)
    except Exception as e:
        print(f"FILEFAILED {file}")
        print(e)
        #raise e

    return f"Done reading {file}"


class TestIO():

    def test_all_to_h5(self):
        nprocesses = 6
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

            files = [file for file in wdir.glob(
                "*.h5") if file.name not in exclude]
            func = partial(write_file, wodir=wodir)

            with Pool(nprocesses) as p:
                for x in p.imap(func, files):

                    print(x)
    
    def test_to_h5(self):
        root_dir = Path(r"/home/joe/Projects/DataStore/EPhysData")
        out_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
        geno = "WT"
        filename = '2021-09-11A.h5'

        write_file((root_dir/geno) / filename, (out_dir/geno))