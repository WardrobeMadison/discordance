from multiprocessing import Pool
from pathlib import Path
from dissonance import viewer, io, epochtypes
from functools import partial


def test_to_json():
    path = "tests/data/2020-07-21A.h5"
    outpath = "tests/output/2020-07-21A.json"

    filemap = io.FileMap(path, outpath)

    sr = io.SymphonyReader(filemap.symphonyfilepath)
    sr.to_json(filemap.dissonancefilepath)


def test_to_h5():
    exclude = [
    "2021-07-06A.h5",
    "2021-12-08A.h5",
    "2022-01-04A.h5",
    "2021-07-13A.h5",
    "2021-09-24A.h5",
    "2022-02-14A.h5",
    "2021-08-25A2.h5",
    "2022-02-28A.h5",
    "2021-08-02A.h5",
    "2022-01-06_.h5"]

    root_dir = Path(r"/home/joe/Projects/DataStore/EPhysData")
    out_dir = Path(r"/home/joe/Projects/DataStore/MappedData")
    for folder in ["DR"]:
        wdir = root_dir / folder

        wodir = (out_dir / folder)
        wodir.mkdir(parents=True, exist_ok=True)

        files = [file for file in wdir.glob("*.h5") if file.name not in exclude]
        func = partial(write_file, wodir = wodir)

        with Pool(4) as p:
            for x in p.imap(func, files):
                print(x)


def write_file(file, wodir):
    try:
        print(file)
        sr = io.SymphonyReader(file)
        sr.to_h5(wodir / file.name)
    except Exception as e:
        print(f"FAILED {file}")
        raise e

    return f"Done reading {file}"


def test_reader():
    path = Path(r"tests/output/2020-07-21A.h5")
    dr = io.DissonanceReader([path])
    epochs = dr.to_epochs()

    print(epochs)

    assert True
